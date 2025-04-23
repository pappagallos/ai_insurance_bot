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
	company_name varchar(255),
	category varchar(255),
	insurance_name varchar(255),
	insurance_type varchar(255),
	sales_date varchar(255),
	index_title varchar(255),
	file_path text,
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


def insert_embedding_article(company_name: str, category: str, insurance_name: str, insurance_type: str, sales_date: str, index_title: str, file_path: str, article_title: str, article_content: str, embedding: list[float]):
    """
    INSERT 쿼리 함수
    """
    cursor.execute("INSERT INTO embedding_article (company_name, category, insurance_name, insurance_type, sales_date, index_title, file_path, article_title, article_content, embedding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (company_name, category, insurance_name, insurance_type, sales_date, index_title, file_path, article_title, article_content, embedding))
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
    {
        "company_name": "농협생명보험", 
        "category": "암보험", 
        "insurance_name": "369뉴테크NH암보험", 
        "insurance_type": "무배당", 
        "sales_date": "2025-01", 
        "index_title": "제1관 목적 및 용어의 정의", 
        "file_path": "/Users/woojinlee/Desktop/ai_insurance_bot/김백현_농협생명보험_흥국생명보험_KB라이프생명보험/농협생명보험/369뉴테크NH암보험(무배당)/저용량-369뉴테크NH암보험(무배당)_2404_최종_241220.pdf", 
        "article_title": "제1관 목적 및 용어의 정의", 
        "content": "", 
        "page_number": 45
    }
    """
    try:
        insert_embedding_article(item["company_name"], item["insurance_name"], item["insurance_type"], item["sales_date"], item["index_title"], item["file_path"], item["article_title"], item["article_content"], get_embedding(item["article_content"]))
        continue_flag = True
    except Exception as e:
        continue_flag = False
        print("Sleep...")
        sleep(5)
        print(e)
