import psycopg2
from app.config import (
    POSTGRES_HOST,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_PORT
)

def run_query(sql):

    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT
    )

    cur = conn.cursor()

    cur.execute(sql)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows