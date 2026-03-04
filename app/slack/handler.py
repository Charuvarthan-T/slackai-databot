from fastapi import APIRouter, Request
from app.llm.sql_generator import generate_sql
from app.db.postgres import run_query

router = APIRouter(prefix="/slack")


@router.post("/ask-data")
async def ask_data(request: Request):
    form = await request.form()
    question = form.get("text")
    sql = generate_sql(question)

    try:
        result = run_query(sql)
        return {
            "response_type": "in_channel",
            "text": f"SQL:\n```{sql}```\n\nResult:\n```{result}```"
        }

    except Exception as e:
        return {
            "response_type": "ephemeral",
            "text": f"Error:\n```{str(e)}```"
        }