from collections import OrderedDict
from threading import Lock
from time import time

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.config import GEMINI_API_KEY, SQL_CACHE_MAX_SIZE, SQL_CACHE_TTL_SECONDS


class TTLRUCache:
    def __init__(self, max_size, ttl_seconds):
        self.max_size = max(1, max_size)
        self.ttl_seconds = max(1, ttl_seconds)
        self._entries = OrderedDict()
        self._lock = Lock()

    def get(self, key):
        now = time()

        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None

            value, expires_at = entry
            if expires_at <= now:
                del self._entries[key]
                return None

            self._entries.move_to_end(key)
            return value

    def set(self, key, value):
        expires_at = time() + self.ttl_seconds

        with self._lock:
            if key in self._entries:
                self._entries.move_to_end(key)

            self._entries[key] = (value, expires_at)
            self._evict_expired_locked()

            while len(self._entries) > self.max_size:
                self._entries.popitem(last=False)

    def _evict_expired_locked(self):
        now = time()
        expired_keys = [
            key for key, (_, expires_at) in self._entries.items()
            if expires_at <= now
        ]

        for key in expired_keys:
            del self._entries[key]


def normalize_question(question):
    return " ".join(question.strip().lower().split())

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
- Return ONLY a PostgreSQL SELECT query
- No explanations
- No markdown
- Single query only

Question:
{question}
"""

prompt = PromptTemplate(
    input_variables=["question"],
    template=template
)

sql_cache = TTLRUCache(
    max_size=SQL_CACHE_MAX_SIZE,
    ttl_seconds=SQL_CACHE_TTL_SECONDS
)


def generate_sql(question):
    cache_key = normalize_question(question)
    cached_sql = sql_cache.get(cache_key)
    if cached_sql is not None:
        return cached_sql

    chain = prompt | llm
    response = chain.invoke({"question": question})
    sql = response.content.strip()
    sql_cache.set(cache_key, sql)
    return sql
