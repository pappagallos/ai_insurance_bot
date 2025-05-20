import json
import cohere
from typing import Callable, Generator
from elasticsearch import Elasticsearch
from openai import OpenAI
from google import genai
import psycopg2


from config import GEMINI_API_KEY, OPENAI_API_KEY, COHERE_API_KEY, ES_HOST, ES_PORT, ES_USERNAME, ES_PASSWORD, ES_CA_CERT


genai_client = genai.Client(api_key=GEMINI_API_KEY)

cohere_client = cohere.ClientV2(api_key=COHERE_API_KEY)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

elasticsearch_client = Elasticsearch(
        "https://" + ES_HOST + ":" + str(ES_PORT),
        ca_certs=ES_CA_CERT,
        basic_auth=(ES_USERNAME, ES_PASSWORD),
        http_compress=True,
        request_timeout=60,
        max_retries=10,
        retry_on_timeout=True,
    )


def get_embedding(content: str, model: str = "gemini-embedding-exp-03-07") -> list[float]:
    """
    벡터 생성
    """
    result = genai_client.models.embed_content(
        model=model,
        contents=content,
    )
    return result.embeddings[0].values


def get_cosine_result(cursor: psycopg2.extensions.cursor, query: str, top_n: int = 5) -> list[str]:
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


def get_es_result(keyword: str, top_n: int = 5) -> list[str]:
    """
    ES 결과 반환
    """
    query = {
        "bool": {
            "should": [
                {
                "multi_match": {
                    "query": keyword,
                    "fields": [
                        "chapter_title^5",
                        "article_title^4",
                        "article_content^3",
                        "index_title^1.2",
                        "insurance_type^1.5"
                    ],
                    "type": "most_fields",
                    "operator": "AND",
                    "fuzziness": "AUTO"
                }
                }
            ],
            "minimum_should_match": 1
        }
    }
    
    result = elasticsearch_client.search(index="insurance_article", query=query, size=top_n)
    sources = [result["hits"]["hits"][i]["_source"] for i in range(top_n)]

    documents = []
    for source in sources:
        documents.append({
            "보험회사명": source["company_name"], 
            "보험분류": source["category"], 
            "보험상품명": source["insurance_name"], 
            "보험종류": source["insurance_type"], 
            "판매시작년도": source["sales_date"], 
            "목차명": source["index_title"], 
            "다운로드경로": source["file_path"], 
            "약관명": source["chapter_title"], 
            "조문제목": source["article_title"], 
            "조문내용": source["article_content"], 
            "페이지번호": source["page_number"]
        })

    return documents


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


def get_keyword_in_query(query: str) -> list[str]:
    """
    질문에서 키워드 추출
    """
    system_prompt = "사용자의 Query에서 키워드를 추출하세요. 키워드는 배열로 반환하세요.: "
    completion = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        stream=False
    )
    return json.loads(completion.choices[0].message.content)


def get_chat_result(query: str, documents: list[str]) -> str:
    """
    챗 결과 반환
    """
    system_prompt = \
    """
    ### 목표
    당신은 농협생명보험 영업 전문가 코리입니다. 사용자의 질문에 대해 보험 약관을 참고하여 답변하세요.

    ### 조건
    1. 문장 사이에 쉼표(,)를 사용하지 말고 마침표(.)로 문장을 분리해 주세요.
    2. 제공된 Documents를 참고하여 답변하세요.
    3. 답변은 최대한 친절하고 상세하고 명확하게 하세요. 그리고 가독성을 신경써서 구조화하여 한국어로 답변하세요.
    4. 어느 조문을 인용해서 답변했는지 반드시 표기하세요. 표기할 때는 insurance_name, article_title, page_number를 답변에 포함하여 제공하세요.
    5. Documents에 없는 내용이어서 모른다고 하는 답변은 사용자에게 관심없는 내용입니다. 사용자가 궁금해하지 않는 내용은 답변에 포함시키지 말고 질문에 사실로만 답변하세요.
    6. 관련 Documents가 없을 경우 모른다고 하세요.
    7. 관련 Doucments로 제공된 데이터를 기반으로만 답변하세요.
    """
    stream_result = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": "### Documents: " + "\n".join(documents)},
            {"role": "user", "content": "### Query: " + query},
        ],
        stream=True,
        top_p=0.9,
    )
    full_text = ""
    for chunk in stream_result:
        chunk_text = chunk.choices[0].delta.content
        if chunk_text:  
            full_text += chunk_text
            print(chunk_text, end='', flush=True)
    
    return full_text


def get_stream_chat(query: str, documents: list[str], get_stream_id: Callable[[], int]) -> Generator[str, None, None]:
    """
    챗 결과 반환
    """
    system_prompt = \
    """
    ### 목표
    당신은 농협생명보험 영업 전문가 코리입니다. 사용자의 질문에 대해 보험 약관을 참고하여 답변하세요.

    ### 조건
    1. 문장 사이에 쉼표(,)를 사용하지 말고 마침표(.)로 문장을 분리해 주세요.
    2. 제공된 Documents를 참고하여 답변하세요.
    3. 답변은 최대한 친절하고 상세하고 명확하게 하세요. 그리고 가독성을 신경써서 구조화하여 한국어로 답변하세요.
    4. 어느 조문을 인용해서 답변했는지 반드시 표기하세요. 표기할 때는 insurance_name, article_title, page_number를 답변에 포함하여 제공하세요.
    5. Documents에 없는 내용이어서 모른다고 하는 답변은 사용자에게 관심없는 내용입니다. 사용자가 궁금해하지 않는 내용은 답변에 포함시키지 말고 질문에 사실로만 답변하세요.
    6. 관련 Documents가 없을 경우 모른다고 하세요.
    7. 관련 Doucments로 제공된 데이터를 기반으로만 답변하세요.
    """
    stream_result = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": "### Documents: " + "\n".join(documents)},
            {"role": "user", "content": "### Query: " + query},
        ],
        stream=True,
        top_p=0.9,
    )
    full_text = ""
    for chunk in stream_result:
        chunk_text = chunk.choices[0].delta.content
        if chunk_text:  
            full_text += chunk_text
            print(chunk_text, end='', flush=True)
            st4 = json.dumps({"type": "processing", "code": "3", "message": chunk_text})
            yield f"id: {get_stream_id()}\n"
            yield f"data: {st4}\n\n"
    
    return full_text