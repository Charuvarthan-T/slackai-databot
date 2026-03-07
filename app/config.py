import os
from dotenv import load_dotenv

load_dotenv()


def get_int_env(name, default):
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SQL_CACHE_MAX_SIZE = get_int_env("SQL_CACHE_MAX_SIZE", 200)
SQL_CACHE_TTL_SECONDS = get_int_env("SQL_CACHE_TTL_SECONDS", 1800)
