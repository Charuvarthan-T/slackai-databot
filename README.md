# Slack AI Data Bot

A Slack-integrated analytics bot that converts natural language questions into SQL queries and returns database results — including formatted tables, CSV exports, and auto-generated charts — directly inside Slack.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup &amp; Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Slack Configuration](#slack-configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Screenshots](#screenshots)

---

## Overview

Users run a single Slack slash command (`/ask-data`) with a plain English question. The bot translates it into SQL using Google Gemini, executes it against a PostgreSQL database, and responds inside Slack with:

- The generated SQL query
- A formatted result table
- A downloadable CSV export link
- An auto-generated bar chart (for 2-column label + numeric results)

---

## Architecture

```
Slack User
    │
    │  /ask-data <question>
    ▼
FastAPI (app/main.py)
    │
    ├──► LangChain + Gemini 2.5 Flash  →  SQL generation (SELECT only)
    │         (app/llm/sql_generator.py)
    │
    ├──► SQL Safety Gate  →  Rejects non-SELECT queries
    │
    ├──► PostgreSQL Query Execution
    │         (app/db/postgres.py)
    │
    └──► Slack Response Builder (app/slack/handler.py)
              │
              ├── Formatted result table (Slack blocks)
              ├── CSV export link
              └── Bar chart image (2-column results)
```

---

## Features

- **Slack slash command** — `/ask-data` triggers the full pipeline
- **Natural language to SQL** — Powered by Gemini 2.5 Flash via LangChain
- **Prompt-constrained SQL generation** — Scoped to `public.sales_daily` schema
- **SQL safety gate** — Rejects any non-`SELECT` query before execution
- **PostgreSQL query execution** — Live analytics against a seeded database
- **Result formatting** — Human-readable numeric formatting in Slack blocks
- **CSV export** — Generates a downloadable CSV with a shareable link
- **Auto bar chart** — Automatically renders a chart when the result has exactly 2 columns (label + numeric)
- **Async/background processing** — Slash command responds immediately; result is posted asynchronously
- **Static file hosting** — FastAPI serves chart images and CSV files via static routes
- **Seed script** — Realistic `sales_daily` data included for local development

---

## Project Structure

```
slackai-databot/
├── app/
│   ├── main.py                  # FastAPI app entry point, static file mounts
│   ├── slack/
│   │   └── handler.py           # Slash command handler, Slack response builder
│   ├── llm/
│   │   └── sql_generator.py     # LangChain + Gemini SQL generation
│   └── db/
│       └── postgres.py          # PostgreSQL connection and query execution
├── scripts/
│   └── seed_db.sql              # Database seed with sample sales data
├── docker-compose.yml           # PostgreSQL container setup
├── requirements.txt
├── .env.example
└── README.md
```

---

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- [ngrok](https://ngrok.com/) (for exposing the local server to Slack)
- A [Slack App](https://api.slack.com/apps) with slash command permissions
- A [Google Gemini API Key](https://aistudio.google.com/app/apikey)

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd slackai-databot
```

### 2. Create and activate a Python virtual environment

```bash
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```env
POSTGRES_HOST=localhost
POSTGRES_DB=analytics
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5433

GEMINI_API_KEY=your_gemini_api_key_here
SLACK_SIGNING_SECRET=your_slack_signing_secret_here
```

> **Note:** Never commit your `.env` file. Add it to `.gitignore`.

---

## Running the Application

### 1. Start PostgreSQL with Docker

```bash
docker-compose up -d
```

### 2. Seed the database

**Option A — using a local `psql` client:**

```bash
psql -h localhost -p 5433 -U postgres -d analytics -f scripts/seed_db.sql
```

**Option B — using Docker exec:**

```bash
docker exec -i slack-ai-postgres psql -U postgres -d analytics < scripts/seed_db.sql
```

### 3. Start the FastAPI server

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Expose the server publicly with ngrok

```bash
ngrok http 8000
```

Copy the generated `https://` URL and update the `NGROK_URL` constant in `app/slack/handler.py`:

```python
NGROK_URL = "https://<your-ngrok-subdomain>.ngrok.io"
```

> The ngrok URL is required so that Slack can reach your local server and users can download CSV/chart files.

---

## Slack Configuration

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps) and open your app (or create one).
2. Navigate to **Slash Commands** → **Create New Command**:
   - **Command:** `/ask-data`
   - **Request URL:** `https://<your-ngrok-url>/slack/ask-data`
   - **Short Description:** Ask a data question in plain English
3. Under **OAuth & Permissions**, ensure the `chat:write` and `commands` scopes are granted.
4. Reinstall the app to your workspace if prompted.
5. Copy the **Signing Secret** from **Basic Information** into your `.env`.

---

## Usage

In any Slack channel where the bot is present, type:

```
/ask-data show total revenue by region
/ask-data which region has the lowest revenue?
/ask-data what is the average revenue per category?
/ask-data show all sales data
```

The bot will reply with the generated SQL, the result table, a CSV export link, and a bar chart where applicable.

### Safety Behavior

Any query attempting to modify data will be blocked:

```
/ask-data delete all records
→ "Unsafe request detected. Only read queries allowed."
```

---

## How It Works

1. **Slash command received** — FastAPI accepts the POST from Slack and immediately returns HTTP 200 to avoid timeout.
2. **Background processing** — The query is handled asynchronously so Slack doesn't time out.
3. **SQL generation** — LangChain passes the user's question and the `public.sales_daily` schema context to Gemini 2.5 Flash, which returns a `SELECT` statement.
4. **Safety check** — The generated SQL is inspected; any non-`SELECT` statement is rejected and an error message is sent back to Slack.
5. **Query execution** — The validated SQL runs against PostgreSQL and returns rows.
6. **Response formatting** — Results are formatted into Slack `blocks` with numeric formatting applied to revenue/order columns.
7. **CSV export** — Results are written to a temporary CSV file served at `/slack/export-csv?id=<uuid>`.
8. **Chart generation** — If the result has exactly 2 columns where the second is numeric, a bar chart PNG is generated with `matplotlib` and served as a static file.

---

## Database Schema

The bot is pre-configured to query the `public.sales_daily` table:

```sql
CREATE TABLE public.sales_daily (
    date        DATE,
    region      TEXT,
    category    TEXT,
    revenue     NUMERIC,
    orders      INTEGER,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

Sample data covers regions (North, South, East, West) and categories (Electronics, Grocery, Fashion).

---

## Example Queries & Results

| Question                             | Generated SQL                                                                               | Result                                      |
| ------------------------------------ | ------------------------------------------------------------------------------------------- | ------------------------------------------- |
| Show total revenue by region         | `SELECT region, SUM(revenue) FROM public.sales_daily GROUP BY region`                     | North: 257,500.50\| South: 54,000.00 \| ... |
| Which region has the lowest revenue? | `SELECT region FROM public.sales_daily GROUP BY region ORDER BY SUM(revenue) ASC LIMIT 1` | South                                       |
| Average revenue per category         | `SELECT category, AVG(revenue) FROM public.sales_daily GROUP BY category`                 | Electronics: 128,750.25\| ...               |

---

## Screenshots

![Screenshot 1](./assets/screenshots/WhatsApp%20Image%202026-03-04%20at%204.49.32%20PM.jpeg)
![Screenshot 2](./assets/screenshots/WhatsApp%20Image%202026-03-04%20at%204.50.44%20PM.jpeg)
![Screenshot 3](./assets/screenshots/WhatsApp%20Image%202026-03-04%20at%204.51.30%20PM.jpeg)
![Screenshot 4](./assets/screenshots/WhatsApp%20Image%202026-03-04%20at%205.15.18%20PM.jpeg)
![Screenshot 5](./assets/screenshots/WhatsApp%20Image%202026-03-04%20at%205.24.35%20PM.jpeg)
![Screenshot 6](./assets/screenshots/WhatsApp%20Image%202026-03-04%20at%205.43.57%20PM.jpeg)
![Screenshot 7](./assets/screenshots/WhatsApp%20Image%202026-03-04%20at%205.44.07%20PM.jpeg)
![Chart 1](./charts/chart_36a607b312e449e392a7e580a431c77a.png)
![Chart 2](./charts/chart_4082c076fbcc45798e86bf929ba63fd8.png)
