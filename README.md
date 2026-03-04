Slack AI Data Bot

A minimal Slack application that converts natural language questions into SQL queries, executes them on a PostgreSQL database, and returns the results directly inside Slack.

The system uses LangChain for NL → SQL translation, enabling non-technical users to query structured data using plain English.

System Overview

The bot works through a Slack slash command that sends the user’s question to a backend service. The backend uses LangChain to generate SQL, runs the query on Postgres, and sends the results back to Slack.

Pipeline

Slack User
   │
   ▼
/ask-data "question"
   │
   ▼
Slack API
   │
   ▼
Backend Server (FastAPI / Node)
   │
   ▼
LangChain NL → SQL
   │
   ▼
PostgreSQL Database
   │
   ▼
Query Results
   │
   ▼
Slack Response
Architecture
Components
Slack Slash Command

Receives the user query.

Example:

/ask-data "What were the top selling products last week?"
Backend API

Handles:

Slack request validation

NL → SQL conversion

Database query execution

Response formatting

LangChain

Responsible for translating natural language into SQL.

Example:

Input:
"What were the top selling products last week?"

Generated SQL:
SELECT product_name, SUM(sales)
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY product_name
ORDER BY SUM(sales) DESC
LIMIT 5;
PostgreSQL

Stores the dataset queried by the bot.

Project Structure
slack-ai-data-bot/

backend/
│
├── app/
│   ├── main.py
│   ├── slack_handler.py
│   ├── sql_agent.py
│   └── db.py
│
├── requirements.txt
├── config.py
│
.env.example
README.md
Setup Instructions
1. Clone Repository
git clone https://github.com/YOUR_USERNAME/slack-ai-data-bot.git
cd slack-ai-data-bot
2. Create Environment File

Create a .env file using the template.

cp .env.example .env

Fill in the required credentials.

Example:

SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
OPENAI_API_KEY=
DATABASE_URL=
3. Install Dependencies
pip install -r requirements.txt
4. Run the Server
uvicorn app.main:app --reload

The backend will start on:

http://localhost:8000
Slack App Setup

Create a Slack App

Enable Slash Commands

Add:

/ask-data

Request URL:

https://your-server-url/slack/ask-data
Example Usage

User enters:

/ask-data "Show the top 5 customers by revenue"

Bot responds:

Top Customers by Revenue

1. Customer A — $24,000
2. Customer B — $19,200
3. Customer C — $17,500
4. Customer D — $15,900
5. Customer E — $14,100
Screenshots
Slack Command Example

(Add screenshot here)

docs/images/slack-command.png

Query Result in Slack

(Add screenshot here)

docs/images/slack-response.png

System Architecture Diagram

(Optional but recommended)

docs/images/architecture.png

Example SQL Generation

Natural Language:

"What were the highest revenue products last month?"

Generated SQL:

SELECT product_name, SUM(revenue)
FROM sales
WHERE sale_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
GROUP BY product_name
ORDER BY SUM(revenue) DESC
LIMIT 10;
Assumptions

The LLM generates a single SQL query

No SQL validation or guardrails are implemented

The database schema is known to the LangChain agent

Queries are read-only

Limitations

No query sanitization

No authentication layer

No SQL safety checks

No multi-table reasoning optimizations

These can be added in future versions.

Future Improvements

Possible extensions:

SQL validation layer

Query cost estimation

Schema-aware prompting

Slack interactive blocks

Result visualization

Caching frequent queries

Role-based access

Tech Stack

Backend

Python

FastAPI

LangChain

Database

PostgreSQL

Integration

Slack API
