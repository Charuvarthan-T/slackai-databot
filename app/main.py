from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.slack.handler import router as slack_router
import os

app = FastAPI()

os.makedirs("charts", exist_ok=True)
app.include_router(slack_router)
app.mount("/charts", StaticFiles(directory="charts"), name="charts")


# the below one was done to test
# @app.get("/db-test")
# def db_test():
#     rows = test_connection()
#     return {"rows": rows}