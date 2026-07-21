import argparse
import sys

import pandas as pd
from sqlalchemy import text

from etl import load
from etl.telemetry import resolve_race_key


def _interpolate_boundary(tel_df, boundary_ms):
    tel_df = tel_df.sort_values("SessionTime").reset_index(drop=True)
    lap_start = tel_df["SessionTime"].iloc[0]
    elapsed_ms = (tel_df["SessionTime"] - lap_start) * 1000

    before = elapsed_ms[elapsed_ms <= boundary_ms]
    after = elapsed_ms[elapsed_ms > boundary_ms]

    if before.empty or after.empty:
        nearest_idx = (elapsed_ms - boundary_ms).abs().idxmin()
        row = tel_df.loc[nearest_idx]
        return {"distance": row["Distance"], "x": row["X"], "y": row["Y"]}

    before_idx = before.idxmax()
    after_idx = after.idxmin()
    t0, t1 = elapsed_ms.loc[before_idx], elapsed_ms.loc[after_idx]
    frac = (boundary_ms - t0) / (t1 - t0)
    row0, row1 = tel_df.loc[before_idx], tel_df.loc[after_idx]
    return {
        "distance": row0["Distance"] + frac * (row1["Distance"] - row0["Distance"]),
        "x": row0["X"] + frac * (row1["X"] - row0["X"]),
        "y": row0["Y"] + frac * (row1["Y"] - row0["Y"]),
    }


def find_reference_lap(engine, race_key):
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT TOP 1 DriverKey, LapNumber
                FROM dw.FactLapTimes
                WHERE RaceKey = :race_key AND LapTimeMillis IS NOT NULL
                    AND Sector1Millis IS NOT NULL AND Sector2Millis IS NOT NULL
                ORDER BY LapTimeMillis ASC
            """),
            {"race_key": race_key},
        ).fetchone()
    return (row[0], row[1]) if row else None


def telemetry_available(engine, race_key, driver_key, lap_number):
    with engine.connect() as conn:
        count = conn.execute(
            text("""
                SELECT COUNT(*) FROM dw.FactTelemetry
                WHERE RaceKey = :race_key AND DriverKey = :driver_key AND LapNumber = :lap_number
            """),
            {"race_key": race_key, "driver_key": driver_key, "lap_number": lap_number},
        ).scalar()
    return count > 0


def compute_sector_boundaries(engine, race_key, driver_key, lap_number):
    with engine.connect() as conn:
        lap_row = conn.execute(
            text("""
                SELECT Sector1Millis, Sector2Millis
                FROM dw.FactLapTimes
                WHERE RaceKey = :race_key AND DriverKey = :driver_key AND LapNumber = :lap_number
            """),
            {"race_key": race_key, "driver_key": driver_key, "lap_number": lap_number},
        ).fetchone()

    boundary1_ms = lap_row[0]
    boundary2_ms = lap_row[0] + lap_row[1]

    tel_df = pd.read_sql(
        text("""
            SELECT SessionTime, Distance, X, Y
            FROM dw.FactTelemetry
            WHERE RaceKey = :race_key AND DriverKey = :driver_key AND LapNumber = :lap_number
        """),
        engine,
        params={"race_key": race_key, "driver_key": driver_key, "lap_number": lap_number},
    )

    return {
        1: _interpolate_boundary(tel_df, boundary1_ms),
        2: _interpolate_boundary(tel_df, boundary2_ms),
    }


def tag_sectors(tel_df, boundary1_distance, boundary2_distance):
    def _sector(distance):
        if distance < boundary1_distance:
            return 1
        if distance < boundary2_distance:
            return 2
        return 3

    out = tel_df.copy()
    out["SectorNumber"] = out["Distance"].apply(_sector)
    return out


def already_loaded(engine, race_key):
    with engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM dw.FactTrackSegment WHERE RaceKey = :race_key"),
            {"race_key": race_key},
        ).scalar()
    return count > 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Track-map fastest-sector geometry")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--round", type=int, required=True, dest="round_")
    args = parser.parse_args(argv)

    engine = load.get_engine()

    race_key = resolve_race_key(engine, args.season, args.round_)
    if race_key is None:
        print(f"ERROR: no race found for {args.season}-{args.round_} in dw.DimRace")
        return 2

    if already_loaded(engine, race_key):
        print(f"Track segment already loaded for race {args.season}-{args.round_} — skipping")
        return 0

    reference = find_reference_lap(engine, race_key)
    if reference is None:
        print(f"ERROR: no lap times found for race {args.season}-{args.round_} in dw.FactLapTimes")
        return 1
    driver_key, lap_number = reference

    if not telemetry_available(engine, race_key, driver_key, lap_number):
        with engine.connect() as conn:
            driver_code = conn.execute(
                text("SELECT Code FROM dw.DimDriver WHERE DriverKey = :driver_key"),
                {"driver_key": driver_key},
            ).scalar()
        print(
            f"ERROR: telemetry not loaded for the reference lap (race {args.season}-{args.round_}, "
            f"driver {driver_code}, lap {lap_number}). Run "
            f"'python -m etl.telemetry --season {args.season} --round {args.round_} --driver {driver_code}' first."
        )
        return 1

    boundaries = compute_sector_boundaries(engine, race_key, driver_key, lap_number)

    tel_df = pd.read_sql(
        text("""
            SELECT Distance, X, Y
            FROM dw.FactTelemetry
            WHERE RaceKey = :race_key AND DriverKey = :driver_key AND LapNumber = :lap_number
        """),
        engine,
        params={"race_key": race_key, "driver_key": driver_key, "lap_number": lap_number},
    )
    tagged_df = tag_sectors(tel_df, boundaries[1]["distance"], boundaries[2]["distance"])

    out_df = pd.DataFrame({
        "RaceKey": race_key,
        "DriverKey": driver_key,
        "LapNumber": lap_number,
        "Distance": tagged_df["Distance"],
        "X": tagged_df["X"],
        "Y": tagged_df["Y"],
        "SectorNumber": tagged_df["SectorNumber"],
    })
    out_df.to_sql("FactTrackSegment", con=engine, schema="dw", if_exists="append", index=False)
    print(f"Loaded {len(out_df)} track segment point(s) for race {args.season}-{args.round_}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
