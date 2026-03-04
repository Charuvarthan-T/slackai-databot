from fastapi import APIRouter, Request, BackgroundTasks
from app.llm.sql_generator import generate_sql
from app.db.postgres import run_query
import requests
import uuid
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

router = APIRouter(prefix="/slack")

NGROK_URL = "https://overdestructively-shareable-dwayne.ngrok-free.dev"


def format_rows(rows):

    if not rows:
        return "No results."

    formatted = ""

    for row in rows:
        line = []
        for value in row:
            try:
                value = float(value)
                line.append(f"{value:,.2f}")
            except:
                line.append(str(value))

        formatted += " | ".join(line) + "\n"

    return formatted


def generate_csv(rows):

    filename = f"result_{uuid.uuid4().hex}.csv"
    path = f"charts/{filename}"

    os.makedirs("charts", exist_ok=True)

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return f"{NGROK_URL}/{path}"


def generate_chart(rows):

    try:

        if len(rows[0]) != 2:
            return None

        labels = [str(r[0]) for r in rows]
        values = [float(r[1]) for r in rows]

        plt.figure(figsize=(6,4))
        plt.bar(labels, values)

        os.makedirs("charts", exist_ok=True)

        filename = f"chart_{uuid.uuid4().hex}.png"
        path = f"charts/{filename}"

        plt.savefig(path)
        plt.close()

        return f"{NGROK_URL}/{path}"

    except:
        return None


def process_query(question, response_url):

    try:

        sql = generate_sql(question)

        if not sql.lower().startswith("select"):
            requests.post(response_url, json={
                "response_type": "ephemeral",
                "text": "Only SELECT queries allowed."
            })
            return

        rows = run_query(sql)

        formatted = format_rows(rows)

        csv_url = generate_csv(rows)

        chart_url = generate_chart(rows)

        blocks = [
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
                    "text": f"*Result*\n```{formatted}```"
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
                        "url": csv_url
                    }
                ]
            }
        ]

        if chart_url:
            blocks.append({
                "type": "image",
                "image_url": chart_url,
                "alt_text": "chart"
            })

        requests.post(response_url, json={
            "response_type": "in_channel",
            "blocks": blocks
        })

    except Exception as e:

        requests.post(response_url, json={
            "response_type": "ephemeral",
            "text": f"Error:\n```{str(e)}```"
        })


@router.post("/ask-data")
async def ask_data(request: Request, background_tasks: BackgroundTasks):

    form = await request.form()

    question = form.get("text")
    response_url = form.get("response_url")

    background_tasks.add_task(process_query, question, response_url)

    return {
        "response_type": "ephemeral",
        "text": "Running query..."
    }