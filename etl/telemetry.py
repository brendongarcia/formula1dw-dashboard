import argparse
import os
import sys

import fastf1
import pandas as pd
from sqlalchemy import text

from etl import config, load
from etl.utils import retry


@retry()
def extract_driver_telemetry(season, round_, driver_code):
    session = fastf1.get_session(season, round_, "R")
    session.load(laps=True, telemetry=True)

    laps = session.laps.pick_driver(driver_code)
    frames = []
    for _, lap in laps.iterrows():
        tel = lap.get_telemetry().copy()
        tel["LapNumber"] = lap["LapNumber"]
        frames.append(tel)

    if not frames:
        return pd.DataFrame(columns=[
            "Distance", "SessionTime", "Speed", "RPM", "nGear",
            "Throttle", "Brake", "DRS", "X", "Y", "Z", "LapNumber",
        ])

    return pd.concat(frames, ignore_index=True)


def resolve_race_key(engine, season, round_):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT RaceKey FROM dw.DimRace WHERE RaceId = :race_id"),
            {"race_id": f"{season}-{round_}"},
        ).fetchone()
    return row[0] if row else None


def resolve_driver_key(engine, driver_code):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT DriverKey FROM dw.DimDriver WHERE Code = :code"),
            {"code": driver_code},
        ).fetchone()
    return row[0] if row else None


def already_loaded(engine, race_key, driver_key):
    with engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM dw.FactTelemetry WHERE RaceKey = :race_key AND DriverKey = :driver_key"),
            {"race_key": race_key, "driver_key": driver_key},
        ).scalar()
    return count > 0


def transform_telemetry(tel_df, race_key, driver_key):
    return pd.DataFrame({
        "RaceKey": race_key,
        "DriverKey": driver_key,
        "LapNumber": tel_df["LapNumber"],
        "Distance": tel_df["Distance"],
        "SessionTime": tel_df["SessionTime"].dt.total_seconds(),
        "Speed": tel_df["Speed"],
        "RPM": tel_df["RPM"],
        "Gear": tel_df["nGear"],
        "Throttle": tel_df["Throttle"],
        "Brake": tel_df["Brake"],
        "DRS": tel_df["DRS"],
        "X": tel_df["X"],
        "Y": tel_df["Y"],
        "Z": tel_df["Z"],
    })


def main(argv=None):
    parser = argparse.ArgumentParser(description="On-demand FactTelemetry load")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--round", type=int, required=True, dest="round_")
    parser.add_argument("--driver", required=True)
    args = parser.parse_args(argv)

    engine = load.get_engine()

    race_key = resolve_race_key(engine, args.season, args.round_)
    if race_key is None:
        print(f"ERROR: no race found for {args.season}-{args.round_} in dw.DimRace")
        return 2

    driver_key = resolve_driver_key(engine, args.driver)
    if driver_key is None:
        print(f"ERROR: no driver found for code '{args.driver}' in dw.DimDriver")
        return 2

    if already_loaded(engine, race_key, driver_key):
        print(f"Telemetry already loaded for race {args.season}-{args.round_}, driver {args.driver} — skipping")
        return 0

    os.makedirs(config.FASTF1_CACHE_DIR, exist_ok=True)
    fastf1.Cache.enable_cache(config.FASTF1_CACHE_DIR)

    try:
        tel_df = extract_driver_telemetry(args.season, args.round_, args.driver)
    except Exception as exc:
        print(f"ERROR: failed to load telemetry: {exc}")
        return 1

    if tel_df.empty:
        print(f"No telemetry laps found for race {args.season}-{args.round_}, driver {args.driver} — nothing to load")
        return 0

    out_df = transform_telemetry(tel_df, race_key, driver_key)
    out_df.to_sql("FactTelemetry", con=engine, schema="dw", if_exists="append", index=False)
    print(f"Loaded {len(out_df)} telemetry row(s) for race {args.season}-{args.round_}, driver {args.driver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
