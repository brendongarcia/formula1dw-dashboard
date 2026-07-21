# Formula1DW ETL

Extracts F1 data (Jolpica-F1 via `fastf1.ergast`, FastF1 for lap/weather
detail) and loads it into the `Formula1DW` SQL Server database built in
Fase 1.

## Setup

```bash
pip install -r requirements.txt
```

Requires the `Formula1DW` database already created (see `database/README.md`)
and ODBC Driver 18 for SQL Server installed.

## Usage

```bash
python -m etl.run                          # checkpoint mode (normal use)
python -m etl.run --season 2024 --round 1  # force one specific race
python -m etl.run --full-reload            # ignore checkpoint, reprocess START_SEASON..current year
```

Checkpoint mode queries `dw.DimRace`/`dw.FactResults` for races already
loaded and only processes what's missing, plus refreshes the most recently
loaded race while the pipeline is caught up (covers post-race penalty
corrections).

## Exit codes

- `0` — clean run
- `1` — one or more races failed extraction (see `etl/logs/etl_<run_id>.log`)
- `2` — the load orchestrator (`dw.usp_RunETL_LoadAll`) reported a failure;
  check `etl.LoadLog` in the database for the `BatchId` printed in the log

## Telemetria sob demanda

`dw.FactTelemetry` is not part of the main batch pipeline (volume too large
for blind loading). Loads on demand by driver + race:

```bash
python -m etl.telemetry --season 2025 --round 1 --driver VER
```

Requires the race to have already been processed by `etl/run.py` (dimensions
must exist). If already loaded for that driver + race, skips without error.

Exit codes: `0` success/skip, `1` FastF1 load failure, `2` race or driver
not found in dimensions.

## Running tests

```bash
pytest tests/etl -v
```

Tests in `test_load.py` and `test_checkpoint.py` run against the real local
`Formula1DW` database (no ORM/mocking layer at this stage) and clean up
after themselves.
