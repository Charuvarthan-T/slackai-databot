from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.config import GEMINI_API_KEY


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0
)


template = """
You are an expert PostgreSQL SQL generator.

Database Schema:

Table: public.sales_daily

Columns:
- date
- region
- category
- revenue
- orders
- created_at

Rules:
- Use ONLY the table public.sales_daily
- Return ONLY a PostgreSQL SELECT query
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include ```sql blocks

User Question:
{question}
"""


prompt = PromptTemplate(
    input_variables=["question"],
    template=template
)


def generate_sql(question: str) -> str:

    chain = prompt | llm

    response = chain.invoke({
        "question": question
    })

    sql = response.content.strip()

    return sql