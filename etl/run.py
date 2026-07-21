import argparse
import os
import sys
from datetime import datetime

import fastf1
import pandas as pd

from etl import checkpoint, config, extract, load, transform, utils


def process_race(season, round_, engine):
    race_id = f"{season}-{round_}"

    results_raw = extract.extract_race_results(season, round_)
    status_raw = extract.extract_finishing_status(season, round_)
    qualifying_raw = extract.extract_qualifying_results(season, round_)
    pit_stops_raw = extract.extract_pit_stops(season, round_)
    session = extract.extract_session(season, round_)
    laps_raw = extract.get_lap_times(session)
    weather_raw, session_date = extract.get_weather(session)

    results_df = transform.transform_results(results_raw, status_raw, race_id)
    qualifying_df = transform.transform_qualifying(qualifying_raw, race_id)
    pit_stops_df = transform.transform_pit_stops(pit_stops_raw, race_id)
    lap_times_df = transform.transform_lap_times(laps_raw, results_raw, race_id)
    weather_df = transform.transform_weather(weather_raw, session_date, race_id)

    load.truncate_and_load(engine, "stg", "Result", results_df)
    load.truncate_and_load(engine, "stg", "Qualifying", qualifying_df)
    load.truncate_and_load(engine, "stg", "PitStop", pit_stops_df)
    load.truncate_and_load(engine, "stg", "LapTime", lap_times_df)
    load.truncate_and_load(engine, "stg", "Weather", weather_df)


def _load_dimensions(engine, season):
    drivers_raw = extract.extract_drivers(season)
    constructors_raw = extract.extract_constructors(season)
    circuits_raw = extract.extract_circuits(season)

    load.truncate_and_load(engine, "stg", "Driver", transform.transform_drivers(drivers_raw))
    load.truncate_and_load(engine, "stg", "Constructor", transform.transform_constructors(constructors_raw))
    load.truncate_and_load(engine, "stg", "Circuit", transform.transform_circuits(circuits_raw))


def _load_status(engine, season, round_):
    status_raw = extract.extract_finishing_status(season, round_)
    load.truncate_and_load(engine, "stg", "Status", transform.transform_status(status_raw))


def _load_race_dim(engine, schedule_df):
    load.truncate_and_load(engine, "stg", "Race", transform.transform_races(schedule_df))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Formula1DW ETL pipeline")
    parser.add_argument("--season", type=int)
    parser.add_argument("--round", type=int)
    parser.add_argument("--full-reload", action="store_true")
    args = parser.parse_args(argv)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger, log_path = utils.setup_logging(config.LOG_DIR, run_id)
    os.makedirs(config.FASTF1_CACHE_DIR, exist_ok=True)
    fastf1.Cache.enable_cache(config.FASTF1_CACHE_DIR)

    engine = load.get_engine()

    if args.season and args.round:
        schedule_df = extract.extract_race_schedule(args.season)
        races = [(args.season, args.round)]
    else:
        schedule_frames = [
            extract.extract_race_schedule(season)
            for season in range(config.START_SEASON, config.END_SEASON + 1)
        ]
        schedule_df = pd.concat(schedule_frames, ignore_index=True)

        if args.full_reload:
            races = sorted(
                (int(s), int(r)) for s, r in zip(schedule_df["season"], schedule_df["round"])
            )
        else:
            races = checkpoint.get_races_to_process(engine, schedule_df)

    _load_race_dim(engine, schedule_df)
    seasons_touched = sorted({season for season, _ in races})
    for season in seasons_touched:
        _load_dimensions(engine, season)

    failures = 0
    for season, round_ in races:
        try:
            _load_status(engine, season, round_)
            process_race(season=season, round_=round_, engine=engine)
            logger.info("Processed race %d-%d", season, round_)
        except Exception as exc:
            failures += 1
            logger.warning("Failed to process race %d-%d: %s", season, round_, exc)
            continue

        # ponytail: MERGE per race, not once at the end -- stg is
        # truncate+reload per race, so a single end-of-run MERGE would only
        # ever see the last race's staged data.
        try:
            batch_id = load.run_orchestrator(engine)
            logger.info("Orchestrator batch %s completed for race %d-%d", batch_id, season, round_)
        except load.ETLLoadError as exc:
            logger.error("Orchestrator failed for race %d-%d: %s", season, round_, exc)
            return 2

    if failures > 0:
        logger.warning("%d race(s) failed to extract, see log at %s", failures, log_path)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
