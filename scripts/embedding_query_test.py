import cohere
import psycopg2
from google import genai

from config import GEMINI_API_KEY, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, OPENAI_API_KEY, COHERE_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

cohere_client = cohere.ClientV2(api_key=COHERE_API_KEY)


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
    result = client.models.embed_content(
        model=model,
        contents=content,
    )
    return result.embeddings[0].values


query = "암을 정의하는 조항에 대해서 설명해줘"
embedding = get_embedding(query)

print("query", query)
print("embedding", embedding)

# embedding 리스트를 PostgreSQL vector 타입으로 명시적 캐스팅
cursor.execute("SELECT * FROM embedding_article ORDER BY embedding <-> %s::vector LIMIT 5", (embedding,))

print("id", "\t", "insurance_name", "\t", "article_title", "\t", "article_content")
for [id, insurance_name, article_title, article_content, embedding] in cursor.fetchall():
    print(id, "\t", insurance_name, "\t", article_title, "\t", article_content)

