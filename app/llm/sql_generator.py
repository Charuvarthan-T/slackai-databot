import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.config import GEMINI_API_KEY

# expose key to langchain/google sdk
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
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
    chain = prompt | llm
    response = chain.invoke({"question": question})
    return response.content.strip()