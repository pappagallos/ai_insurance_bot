import time
import psycopg2

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from config import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, ES_HOST, ES_PORT, ES_USERNAME, ES_PASSWORD


postgres_connection = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST
)
cursor = postgres_connection.cursor()


cursor.execute("SELECT id FROM embedding_article")
document_ids = [id for [id] in cursor.fetchall()]


def generate_documents(document_ids):
    for index, document_id in enumerate(document_ids):
        print("bulk_count: ", index + 1)
        print("document_id:", document_id)

        cursor.execute(
            """
            SELECT company_name, category, insurance_name, insurance_type, sales_date, index_title, file_path, chapter_title, article_title, article_content, page_number
            FROM embedding_article
            WHERE id = %s
            """,
            (document_id,),
        )
        [company_name, category, insurance_name, insurance_type, sales_date, index_title, file_path, chapter_title, article_title, article_content, page_number] = cursor.fetchone()

        bulk_item = {
            "_index": "insurance_article",
            "_id": document_id,
            "_source": {
                "company_name": company_name,
                "category": category,
                "insurance_name": insurance_name,
                "insurance_type": insurance_type,
                "sales_date": sales_date,
                "index_title": index_title,
                "file_path": file_path,
                "chapter_title": chapter_title,
                "article_title": article_title,
                "article_content": article_content,
                "page_number": page_number,
            },
        }
        print(bulk_item)
        print("--------------------------------")

        if index % 100 == 0:
            time.sleep(1)

        yield bulk_item


def index_company_cases(document_ids):
    if len(document_ids) == 0:
        return

    elasticsearch_client = Elasticsearch(
        "https://" + ES_HOST + ":" + str(ES_PORT),
        ca_certs="~/Desktop/ai_insurance_bot/scripts/http_ca.crt",
        basic_auth=(ES_USERNAME, ES_PASSWORD),
        http_compress=True,
        request_timeout=60,
        max_retries=10,
        retry_on_timeout=True,
    )

    bulk(elasticsearch_client, generate_documents(document_ids))
    elasticsearch_client.indices.refresh(index="insurance_article")


index_company_cases(document_ids);