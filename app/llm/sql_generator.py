from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.config import GROK_API_KEY


llm = ChatOpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1",
    model="grok-2-latest"
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

Return ONLY a PostgreSQL SELECT query.

Question:
{question}
"""


prompt = PromptTemplate(
    input_variables=["question"],
    template=template
)


def generate_sql(question):
    chain = prompt | llm
    response = chain.invoke({"question": question})
    return response.content.strip()