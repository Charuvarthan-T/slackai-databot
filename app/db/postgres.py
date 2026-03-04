import psycopg
from app.config import POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
import os

POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

def run_query(sql: str):
    conn = psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

    with conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            try:
                rows = cur.fetchall()
            except psycopg.ProgrammingError:
                rows = []
    conn.close()
    return rows


def test_connection():
    return run_query("SELECT region, SUM(revenue) FROM sales_daily GROUP BY region;")