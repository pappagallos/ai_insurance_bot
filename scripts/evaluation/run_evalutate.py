import os
import sys
import json
import time
import openai
import pandas as pd


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from openai import OpenAI
from prompt import get_prompt
from score_function import ndcg_at_k
from evaluation.queries import queries
from requests.exceptions import HTTPError
from config import OPENAI_API_KEY


openai_client = OpenAI(api_key=OPENAI_API_KEY)


def get_evaluation(prompt_name: str, query: str, document: str, retries: int = 0, max_retries: int = 5) -> dict:
    while retries < max_retries:
        try:
            response = openai_client.chat.completions.create(
                model="o1-mini",
                messages=[{"role": "user", "content": get_prompt(prompt_name, query, document)}]
            )
            llm_response = response.choices[0].message.content.strip()
            print("Response: ", llm_response)

            evaluation = json.loads(llm_response)
            if evaluation["score"] is None:
                print("LLM 응답이 올바르지 않습니다. 다시 시도합니다.(score가 없습니다.)")
                continue
            if evaluation["reason"] is None:
                print("LLM 응답이 올바르지 않습니다. 다시 시도합니다.(reason가 없습니다.)")
                continue
            return evaluation
        except json.JSONDecodeError as error:
            print("LLM 응답이 올바르지 않습니다. 다시 시도합니다.")
            retries += 1
            continue
        except openai.APIError as error:
            if error.code == "context_length_exceeded":
                print("지원 가능한 콘텍스트 범위를 벗어났습니다.", document)
                break
            retries += 1
            continue
        except HTTPError as error:
            if error.response.status_code == 429:
                print("429 오류, 30초 후 다시 실행합니다.")
                time.sleep(30)
                retries += 1
            else:
                raise error


ndcg_score = []
testset = pd.read_csv("query_document.csv")
testset = testset.to_dict(orient="records")
for index, query in enumerate(queries):
    print(f"Processing query: {query}")
    dcg = []
    data = []
    for test in list(filter(lambda x: x["query"] == query, testset)):
        print("Document: ", test["document"])
        evaluate_prompt = "rulebase_0.0_to_1.0"
        evaluation = get_evaluation(evaluate_prompt, query, test["document"])
        dcg.append(evaluation.get("score"))
        data.append({"query": query, "document": test["document"], "score": evaluation.get("score"), "reason": evaluation.get("reason")})
    ndcg = ndcg_at_k(dcg, 20)
    ndcg_score.append(ndcg)
    df = pd.DataFrame(columns=["query", "document", "score", "reason"], data=data)
    df.to_csv(f"{evaluate_prompt}_result_{index}.csv", index=True)

ndcg_score = [score * 100 for score in ndcg_score]
avg_ndcg_score = sum(ndcg_score) / len(ndcg_score)

print("================================================")
print("전체 질문에 대한 관련 문서 검색 평균 점수는 ", avg_ndcg_score, "점 입니다.")
print("================================================")