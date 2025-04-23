import json

from utils import get_chat_result, get_rerank_result, get_cosine_result


query = "보험에서 암으로 인정하는 내용이나 정의에 대해서 설명해줘"
print("query", query)

documents = get_cosine_result(query)
documents = [json.dumps(document, ensure_ascii=False) for document in documents]
print("documents", documents)

rerank_result = get_rerank_result(query, documents)

chat_complete = get_chat_result(query, rerank_result)