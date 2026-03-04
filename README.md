# slackai-databot

A Slack bot that uses LLMs to generate SQL queries and interact with a PostgreSQL database.

## Project Structure

- `app/` - Main application code
  - `main.py` - Entry point
  - `config.py` - Configuration
  - `slack/handler.py` - Slack event handler
  - `db/postgres.py` - Database logic
  - `llm/sql_generator.py` - LLM SQL generation
  - `prompts/sql_prompt.txt` - LLM prompt template
- `scripts/seed_db.sql` - DB seed script
- `docker-compose.yml` - Docker Compose setup
- `.env` - Environment variables
- `requirements.txt` - Python dependencies

## Usage

1. Copy `.env.example` to `.env` and fill in values.
2. Run `docker-compose up` to start services.
