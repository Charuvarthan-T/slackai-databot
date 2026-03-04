import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
GROK_API_KEY = os.getenv("GROK_API_KEY")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")