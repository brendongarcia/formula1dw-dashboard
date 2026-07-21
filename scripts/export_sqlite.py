"""One-shot snapshot: SQL Server mart views -> dashboard/data/formula1dw.sqlite.

Temporada 2025 fechou (24/24 corridas), dado nao muda mais. Roda isso de novo
so se o banco for atualizado (ex: temporada 2026). O Streamlit le do sqlite
gerado aqui, nao do SQL Server, entao um dashboard publicado nao precisa de
banco nenhum no ar.
"""
from pathlib import Path
from sqlalchemy import create_engine
import pandas as pd

SOURCE = "mssql+pyodbc://localhost/Formula1DW?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
DEST = Path(__file__).resolve().parent.parent / "dashboard" / "data" / "formula1dw.sqlite"
SEASON = 2025  # mart views cover every season loaded (2021-2026); dashboard only shows SEASON

VIEWS = [
    "vw_RaceResults", "vw_DriverStandings", "vw_ConstructorStandings",
    "vw_LapTimesEnriched", "vw_QualifyingResults", "vw_PitStops", "vw_Weather",
    "vw_FastestSectorByDriver", "vw_TrackMapFastestSector",
]
# vw_Telemetry: so as colunas que o dashboard le (SessionTime/RPM/DRS/X/Y/Z
# ficam de fora - nao usadas em nenhuma pagina - cortam ~40% do arquivo).
TELEMETRY_COLS = "Season, Round, RaceName, DriverName, LapNumber, Distance, Speed, Gear, Throttle, Brake"

src = create_engine(SOURCE)
DEST.parent.mkdir(parents=True, exist_ok=True)
DEST.unlink(missing_ok=True)
dst = create_engine(f"sqlite:///{DEST}")

for view in VIEWS:
    df = pd.read_sql(f"SELECT * FROM mart.{view} WHERE Season = {SEASON}", src)
    df.to_sql(view, dst, index=False)
    print(f"{view}: {len(df)} rows")

telemetry = pd.read_sql(f"SELECT {TELEMETRY_COLS} FROM mart.vw_Telemetry WHERE Season = {SEASON}", src)
telemetry.to_sql("vw_Telemetry", dst, index=False)
print(f"vw_Telemetry: {len(telemetry)} rows")

print(f"-> {DEST} ({DEST.stat().st_size / 1_048_576:.1f} MB)")
