import json
from time import sleep
import psycopg2
import argparse

from google import genai

from config import GEMINI_API_KEY, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST


parser = argparse.ArgumentParser()
parser.add_argument("--file", type=str, required=True)

args = parser.parse_args()
file_path = args.file


client = genai.Client(api_key=GEMINI_API_KEY)


"""
[벡터 테이블]
create table embedding_article (
	id int primary key generated always as identity,
	insurance_name varchar(255),
	article_title varchar(255),
	article_content text,
	embedding vector(3072)
)
"""
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


def insert_embedding_article(insurance_name: str, article_title: str, article_content: str, embedding: list[float]):
    """
    INSERT 쿼리 함수
    """
    cursor.execute("INSERT INTO embedding_article (insurance_name, article_title, article_content, embedding) VALUES (%s, %s, %s, %s)", (insurance_name, article_title, article_content, embedding))
    postgres_connection.commit()


with open(file_path, "r") as f:
    data = f.read()


def get_next_article(data: json):
    for item in json.loads(data):
        yield item


continue_flag = True
current_article = get_next_article(data)
while True:
    if continue_flag:
        item = next(current_article, None)
    if item is None:
        break
        
    """
    [json 예시]
    {"insurance_name": "369 뉴테크 NH 암보험_무배당_2404_주계약_약관", "article_title": "제1관 목적 및 용어의 정의", "content": "", "page_number": 45}
    """
    try:
        continue_flag = True
        insert_embedding_article(item["insurance_name"], item["article_title"], item["content"], get_embedding(item["content"]))
    except Exception as e:
        continue_flag = False
        print("Sleep...")
        sleep(5)
        print(e)
