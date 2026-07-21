from pathlib import Path

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DB_PATH = Path(__file__).resolve().parent / "data" / "formula1dw.sqlite"
CONN_STRING = f"sqlite:///{DB_PATH}"


@st.cache_resource
def get_engine() -> Engine:
    return create_engine(CONN_STRING)


@st.cache_data(ttl=300)
def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})
