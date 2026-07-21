import logging

from sqlalchemy import create_engine, text

from etl import config

logger = logging.getLogger("etl.load")


class ETLLoadError(Exception):
    pass


def get_engine():
    return create_engine(config.DB_CONNECTION_URL, fast_executemany=True)


def truncate_and_load(engine, schema, table, df):
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {schema}.{table}"))
        if not df.empty:
            df.to_sql(table, con=conn, schema=schema, if_exists="append", index=False)
    logger.info("Loaded %d row(s) into %s.%s", len(df), schema, table)


def run_orchestrator(engine, proc_name="dw.usp_RunETL_LoadAll"):
    with engine.begin() as conn:
        raw_conn = conn.connection.dbapi_connection
        cursor = raw_conn.cursor()
        cursor.execute(f"EXEC {proc_name}")
        row = cursor.fetchone()
        batch_id = row[0] if row else None
        try:
            cursor.nextset()
        except Exception as exc:
            raise ETLLoadError(
                f"Orchestrator reported failure(s) in batch {batch_id}: {exc}"
            ) from exc
    logger.info("Orchestrator completed successfully, BatchId=%s", batch_id)
    return batch_id
