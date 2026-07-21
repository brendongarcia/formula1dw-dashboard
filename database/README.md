# Formula1DW — Database Setup

Layered SQL Server database for the Formula1DW project. Run scripts in
this exact order against `localhost` (Windows Authentication):

```bash
sqlcmd -S localhost -E -C -i create_database.sql
sqlcmd -S localhost -E -C -i schemas.sql
sqlcmd -S localhost -E -C -d Formula1DW -i staging.sql
sqlcmd -S localhost -E -C -d Formula1DW -i dimensions.sql
sqlcmd -S localhost -E -C -d Formula1DW -i facts.sql
sqlcmd -S localhost -E -C -d Formula1DW -i indexes.sql
sqlcmd -S localhost -E -C -d Formula1DW -i procedures.sql
sqlcmd -S localhost -E -C -d Formula1DW -i views.sql
sqlcmd -S localhost -E -C -d Formula1DW -Q "EXEC dw.usp_Seed_DimDate"
```

All scripts are idempotent — safe to re-run.

## Loading data

1. Python ETL (later phase) loads source rows into the `stg` schema.
2. Run `EXEC dw.usp_RunETL_LoadAll` to MERGE `stg` into `dw` (dimensions
   before facts, FK-safe order).
3. Check `SELECT * FROM etl.LoadLog ORDER BY LoadLogKey DESC` for the
   result of the most recent run.

## Schema layers

- `raw` — landing zone, mirrors source shape (used by later ETL phase)
- `stg` — typed staging, natural keys only
- `dw` — star schema, surrogate keys, `Dim*`/`Fact*`
- `mart` — views only, for Power BI consumption
- `etl` — `LoadLog` operational table

See `docs/superpowers/specs/2026-07-04-db-modelagem-design.md` for the
full design rationale (including why there's no separate `DimTeam`, and
why `FactTelemetry` has no load procedure yet).
