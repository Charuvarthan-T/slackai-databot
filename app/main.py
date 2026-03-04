from fastapi import FastAPI
from app.slack.handler import router as slack_router
from app.db.postgres import test_connection

app = FastAPI(title="Slack AI Data Bot")

app.include_router(slack_router)

@app.get("/")
def health():
    return {"status": "running"}

@app.get("/db-test")
def db_test():
    rows = test_connection()
    return {"rows": rows}