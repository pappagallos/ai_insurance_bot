import json
import psycopg2
from google import genai
from utils import get_chat_result, get_rerank_result, get_cosine_result
from config import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, GEMINI_API_KEY


genai_client = genai.Client(api_key=GEMINI_API_KEY)


postgres_connection = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST
)
cursor = postgres_connection.cursor()


# query = "챗봇이 알고 있는 암보험 상품들의 일반암 진단금액은 평균적으로 얼마 정도이며, 상품 간 차이는 큰 편인가요? 가장 높은 진단금과 낮은 진단금은 각각 얼마 수준인가요?"
# query = "여러 개의 암보험에 가입했을 경우, 진단금이나 수술비, 입원비를 각각의 보험에서 모두 받을 수 있나요? 아니면 일부만 지급(비례보상 등)하는 경우도 있나요? 약관의 일반적인 규정은 어떤가요?"
# query = "건강검진 없이 간편 심사만으로 가입할 수 있는 암보험 상품들이 많나요? 이런 상품은 일반 상품과 비교했을 때 보험료나 보장 내용에 어떤 차이가 있는 경향이 있나요?"
# query = "갱신형 암보험의 경우, 갱신 시 보험료는 보통 얼마나 오르나요? 갱신 주기는 몇 년이 일반적인가요?"
query = "약관에서 정의하는 '입원'의 기준은 어떤가요? (예: 병원에 머무는 최소 시간, 입원 인정 장소 등) 상품마다 큰 차이가 있나요?"
# query = "암 수술비 지급 시, 동일한 암으로 여러 번 수술받는 경우에도 계속 지급되나요? 아니면 횟수 제한이 있는 경우가 많나요?"
# query = "암보험 가입 후 면책기간(예: 90일)이 지나기 전에 암 진단을 받으면, 보험금을 전혀 받을 수 없나요? 예외적인 경우가 있는 상품도 있나요?"
# query = "'보험료 납입 면제' 조건에 대해 약관에서 어떻게 설명하고 있는지, 관련 조항들을 찾아서 보여주세요."

print("### Query")
print(query)
print("--------------------------------")

documents = get_cosine_result(cursor, query)
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

chat_complete = get_chat_result(query, rerank_result, None)

print("### Chat Complete")