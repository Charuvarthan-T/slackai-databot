from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.config import GEMINI_API_KEY
import time

# Cache to avoid repeated Gemini calls
sql_cache = {}

# Rate limit control
last_call_time = 0

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0
)

template = """
You are a SQL generator.

Table: public.sales_daily

Columns:
date
region
category
revenue
orders
created_at

Rules:
- Return ONLY a PostgreSQL SELECT query.
- No explanations.
- No markdown.

Question:
{question}
"""

prompt = PromptTemplate(
    input_variables=["question"],
    template=template
)


def generate_sql(question):
    global last_call_time

    # Return cached SQL if available
    if question in sql_cache:
        return sql_cache[question]

    # Rate limit (avoid burning API quota)
    if time.time() - last_call_time < 2:
        time.sleep(2)

    chain = prompt | llm
    response = chain.invoke({"question": question})

    sql = response.content.strip()

    # Save to cache
    sql_cache[question] = sql

    last_call_time = time.time()

    return sql