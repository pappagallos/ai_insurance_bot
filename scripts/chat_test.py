import json

from utils import get_chat_result, get_rerank_result, get_cosine_result


# query = "그럼 NHe편한암보험에서 암으로 인정하는 내용이나 정의에 대해서 설명해줘"
# query = "건강검진 없이 간편 심사만으로 가입할 수 있는 암보험 상품들이 많나요? 이런 상품은 일반 상품과 비교했을 때 보험료나 보장 내용에 어떤 차이가 있는 경향이 있나요?"
query = "챗봇이 알고 있는 암보험 상품들의 일반암 진단금액은 평균적으로 얼마 정도이며, 상품 간 차이는 큰 편인가요? 가장 높은 진단금과 낮은 진단금은 각각 얼마 수준인가요?"

print("### Query")
print(query)
print("--------------------------------")

documents = get_cosine_result(query)
documents = [json.dumps(document, ensure_ascii=False) for document in documents]

print("### Documents")
for document in documents:
    print(document)
print("--------------------------------")

rerank_result = get_rerank_result(query, documents)

print("### Rerank Result")
for result in rerank_result:
    print(result)
print("--------------------------------")

chat_complete = get_chat_result(query, rerank_result)

print("### Chat Complete")