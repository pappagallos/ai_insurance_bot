import cohere
import psycopg2
from openai import OpenAI
from google import genai

from config import GEMINI_API_KEY, OPENAI_API_KEY, COHERE_API_KEY, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST

genai_client = genai.Client(api_key=GEMINI_API_KEY)

cohere_client = cohere.ClientV2(api_key=COHERE_API_KEY)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

postgres_connection = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST
)
cursor = postgres_connection.cursor()


def get_embedding(content: str, model: str = "gemini-embedding-exp-03-07") -> list[float]:
    """
    벡터 테이블 생성 쿼리
    """
    result = genai_client.models.embed_content(
        model=model,
        contents=content,
    )
    return result.embeddings[0].values


def get_cosine_result(query: str, top_n: int = 5) -> list[str]:
    """
    코사인 결과 반환
    """
    embedding = get_embedding(query)
    cursor.execute("SELECT id, insurance_name, article_title, article_content FROM embedding_article ORDER BY embedding <-> %s::vector LIMIT %s", (embedding, top_n))
    return [{"id": id, "insurance_name": insurance_name, "article_title": article_title, "article_content": article_content} for [id, insurance_name, article_title, article_content] in cursor.fetchall()]


def get_rerank_result(query: str, documents: list[str], top_n: int = 3) -> list[str]:
    """
    리랭크 결과 반환
    """
    result = cohere_client.rerank(
        model="rerank-v3.5",
        query=query,
        documents=documents,
        top_n=top_n,
    )
    return [documents[result.results[i].index] for i in range(top_n)]


def get_chat_result(query: str, documents: list[str]) -> list[str]:
    """
    챗 결과 반환
    """
    stream_result = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful insurance expert. answer user's queries in Korean."},
            {"role": "assistant", "content": "Here are the documents: " + "\n".join(documents)},
            {"role": "user", "content": query},
        ],
        stream=True,
    )
    full_text = ""
    for chunk in stream_result:
        chunk_text = chunk.choices[0].delta.content
        full_text += chunk_text
        print(chunk_text, end="", flush=True)
    return full_text
