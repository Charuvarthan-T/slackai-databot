from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.config import GEMINI_API_KEY
import time

sql_cache = {}
last_call = 0

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0
)

template = """
You are a PostgreSQL SQL generator.

Table: public.sales_daily

Columns:
date
region
category
revenue
orders
created_at

Rules:
- Output ONLY a SQL SELECT query
- No explanations
- No markdown
- Always reference public.sales_daily

Question:
{question}
"""

prompt = PromptTemplate(
    input_variables=["question"],
    template=template
)


def generate_sql(question):

    global last_call

    if question in sql_cache:
        return sql_cache[question]

    if time.time() - last_call < 1:
        time.sleep(1)

    chain = prompt | llm
    result = chain.invoke({"question": question})

    sql = result.content.strip()

    sql_cache[question] = sql
    last_call = time.time()

    return sql