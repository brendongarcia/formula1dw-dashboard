import os
from datetime import datetime

DB_CONNECTION_URL = (
    "mssql+pyodbc://@localhost/Formula1DW"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&trusted_connection=yes&TrustServerCertificate=yes"
)

START_SEASON = 2021
END_SEASON = datetime.now().year

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FASTF1_CACHE_DIR = os.path.join(_BASE_DIR, ".fastf1_cache")
LOG_DIR = os.path.join(_BASE_DIR, "logs")
