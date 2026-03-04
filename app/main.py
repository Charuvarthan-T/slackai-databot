from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Slack AI Data Bot running"}