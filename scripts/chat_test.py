from utils import get_chat_result, get_rerank_result, get_cosine_result


query = "보험에서 암으로 인정하는 내용이나 정의에 대해서 설명해줘"
print("query", query)

documents = get_cosine_result(query)
documents = [document["article_content"] for document in documents]
print("documents", documents)

rerank_result = get_rerank_result(query, documents)
print("rerank_result", rerank_result)

chat_complete = get_chat_result(query, rerank_result)
print("chat_complete", chat_complete)