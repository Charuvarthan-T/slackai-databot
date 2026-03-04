from fastapi import APIRouter, Request
import requests

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

            if hasattr(value, "quantize"):  # Decimal support
                formatted_row.append(f"{float(value):,.2f}")
            else:
                formatted_row.append(str(value))

        formatted += " | ".join(formatted_row) + "\n"

    return formatted


def run_query_pipeline(question):

    sql = generate_sql(question)

    # Safety check
    if not sql.lower().strip().startswith("select"):
        raise Exception("Only SELECT queries are allowed.")

    try:

        result = run_query(sql)

        return sql, result

    except Exception as db_error:

        # Ask Gemini to repair SQL
        repair_prompt = f"""
The SQL query failed.

User question:
{question}

SQL:
{sql}

Database error:
{str(db_error)}

Generate a corrected PostgreSQL SELECT query only.
"""

        fixed_sql = generate_sql(repair_prompt)

        if not fixed_sql.lower().strip().startswith("select"):
            raise Exception("Unsafe SQL detected during repair.")

        result = run_query(fixed_sql)

        return fixed_sql, result


@router.post("/ask-data")
async def ask_data(request: Request):

    form = await request.form()

    question = form.get("text")
    response_url = form.get("response_url")

    if not question:
        return {
            "response_type": "ephemeral",
            "text": "Please provide a question."
        }

    # Instant ACK to Slack (prevents timeout)
    ack = {
        "response_type": "ephemeral",
        "text": "Processing your query..."
    }

    # Basic security filter
    danger_words = ["drop", "delete", "update", "insert", "alter"]

    if any(word in question.lower() for word in danger_words):

        requests.post(
            response_url,
            json={
                "response_type": "ephemeral",
                "text": "Unsafe request detected. Only read queries allowed."
            }
        )

        return ack

    try:

        sql, result = run_query_pipeline(question)

        formatted = format_result(result)

        requests.post(
            response_url,
            json={
                "response_type": "in_channel",
                "text": f"*SQL*\n```{sql}```\n\n*Result*\n```{formatted}```"
            }
        )

    except Exception as e:

        requests.post(
            response_url,
            json={
                "response_type": "ephemeral",
                "text": f"Error: {str(e)}"
            }
        )

    return ack