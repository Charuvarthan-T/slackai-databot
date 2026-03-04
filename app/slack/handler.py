from fastapi import APIRouter, Request, BackgroundTasks
import requests
import csv
import io

from app.llm.sql_generator import generate_sql
from app.db.postgres import run_query

router = APIRouter(prefix="/slack")


def format_result(rows):

    if not rows:
        return "No results found."

    formatted = ""

    for row in rows:

        values = []

        for v in row:

            if hasattr(v, "quantize"):
                values.append(f"{float(v):,.2f}")
            else:
                values.append(str(v))

        formatted += " | ".join(values) + "\n"

    return formatted


def generate_csv(rows):

    output = io.StringIO()
    writer = csv.writer(output)

    for row in rows:
        writer.writerow(row)

    return output.getvalue()


def process_query(question, response_url):

    try:

        sql = generate_sql(question)

        if not sql.lower().startswith("select"):
            raise Exception("Only SELECT queries allowed")

        rows = run_query(sql)

        result = format_result(rows)

        csv_data = generate_csv(rows)

        requests.post(
            response_url,
            json={
                "response_type": "in_channel",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*SQL*\n```{sql}```"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Result*\n```{result}```"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Export CSV"
                                },
                                "url": "https://example.com"
                            }
                        ]
                    }
                ]
            }
        )

    except Exception as e:

        requests.post(
            response_url,
            json={
                "response_type": "ephemeral",
                "text": f"Error\n```{str(e)}```"
            }
        )


@router.post("/ask-data")
async def ask_data(request: Request, background_tasks: BackgroundTasks):

    form = await request.form()

    question = form.get("text")
    response_url = form.get("response_url")

    if not question:

        return {
            "response_type": "ephemeral",
            "text": "Please provide a query."
        }

    background_tasks.add_task(process_query, question, response_url)

    return {
        "response_type": "ephemeral",
        "text": "Running query..."
    }