from fastapi import APIRouter, Request
from app.llm.sql_generator import generate_sql
from app.db.postgres import run_query

router = APIRouter(prefix="/slack")

def format_result(rows):

    if not rows:
        return "No results found."

    formatted = ""

    for row in rows:
        formatted_row = []
        for value in row:
            if hasattr(value, "quantize"):  # Decimal
                formatted_row.append(f"{float(value):,.2f}")
            else:
                formatted_row.append(str(value))
        formatted += " | ".join(formatted_row) + "\n"
    return formatted


@router.post("/ask-data")
async def ask_data(request: Request):
    form = await request.form()
    question = form.get("text")

    if not question:
        return {
            "response_type": "ephemeral",
            "text": "Please provide a question."
        }

    try:
        sql = generate_sql(question)

        # this is d safety measure :), to not trust llms
        if not sql.lower().strip().startswith("select"):
            return {
              "response_type": "ephemeral",
              "text": "Only SELECT queries are allowed."
            }
        result = run_query(sql)
        formatted_result = format_result(result)

        return {
            "response_type": "in_channel",
            "text": f"*Query Result*\n\n{formatted_result}"
        }

    except Exception as e:

        return {
            "response_type": "ephemeral",
            "text": f"Error: {str(e)}"
        }