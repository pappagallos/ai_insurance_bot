import os
import sys
import json
import time
import cohere
import psycopg2
import pandas as pd
from openai import OpenAI
from google import genai


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from evaluation.queries import queries
from config import GEMINI_API_KEY, OPENAI_API_KEY, COHERE_API_KEY, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST

genai_client = genai.Client(api_key=GEMINI_API_KEY)

cohere_client = cohere.ClientV2(api_key=COHERE_API_KEY)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Connect to the database
conn = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST
)
cursor = conn.cursor()


def get_embedding(content: str, model: str = "gemini-embedding-exp-03-07") -> list[float]:
    """
    벡터 생성
    """
    result = genai_client.models.embed_content(
        model=model,
        contents=content,
    )
    return result.embeddings[0].values


def get_cosine_result(cursor: psycopg2.extensions.cursor, query: str, top_n: int = 20) -> list[str]:
    """
    코사인 결과 반환
    """
    embedding = get_embedding(query)
    cursor.execute("SELECT company_name, category, insurance_name, insurance_type, sales_date, index_title, file_path, chapter_title, article_title, article_content, page_number FROM embedding_article ORDER BY embedding <-> %s::vector LIMIT %s", (embedding, top_n))
    return [{
        "보험회사명": company_name, 
        "보험분류": category, 
        "보험상품명": insurance_name, 
        "보험종류": insurance_type, 
        "판매시작년도": sales_date, 
        "목차명": index_title, 
        "다운로드경로": file_path, 
        "약관명": chapter_title, 
        "조문제목": article_title, 
        "조문내용": article_content, 
        "페이지번호": page_number
        } for [company_name, category, insurance_name, insurance_type, sales_date, index_title, file_path, chapter_title, article_title, article_content, page_number] in cursor.fetchall()]



def get_rerank_result(query: str, documents: list[str], top_n: int = 20, retries: int = 0, max_retries: int = 5) -> list[str]:
    """
    리랭크 결과 반환
    """
    while retries < max_retries:
        try:
            result = cohere_client.rerank(
                model="rerank-v3.5",
                query=query,
                documents=documents,
                top_n=top_n,
            )
            return [json.loads(documents[result.results[i].index]) for i in range(top_n)]
        except cohere.errors.TooManyRequestsError:
            print("429 오류, 60초 후 다시 실행합니다.")
            time.sleep(60)
            retries += 1
            continue
        except Exception as error:
            print("오류가 발생했습니다. 다시 시도합니다.", error)
            retries += 1
            continue


def get_safe_data(data: any) -> str:
    return json.dumps(data, ensure_ascii=False).replace("\\", "")


data = []
rerank_data = []
for query in queries:
    print("Processing: ", query)
    
    #==================== 자신의 Retriever를 사용해주세요. ====================
    documents = get_cosine_result(cursor, query)
    #====================================================================

    for rank, document in enumerate(documents):
        data.append({"query": query, "document": document, "rank": rank, "relevance_score": None, "relevance_reason": None})

cosine_df = pd.DataFrame(columns=["query", "document", "rank", "relevance_score", "relevance_reason"], data=data)
cosine_df.to_csv("dataset.csv", index=True)

cursor.close()
conn.close()