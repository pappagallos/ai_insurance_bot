import pytest
from rerankers import Reranker
from ragatouille import RAGPretrainedModel

# import rerankers
# def tt():
#     from colbert.infra import ColBERTConfig
#     from colbert.modeling.checkpoint import Checkpoint

#     ckpt = Checkpoint("jinaai/jina-colbert-v2", colbert_config=ColBERTConfig())
#     docs = [
#         "ColBERT is a novel ranking model that adapts deep LMs for efficient retrieval.",
#         "Jina-ColBERT is a ColBERT-style model but based on JinaBERT so it can support both 8k context length, fast and accurate retrieval.",
#     ]
#     query_vectors = ckpt.queryFromText(docs, bsize=2)
#     return query_vectors
# ColBERT v2 모델 로드
RAG = RAGPretrainedModel.from_pretrained("jinaai/jina-colbert-v2")
def tt2():
    # 인덱싱할 문서 리스트
    docs = [
        "도쿄의 인구는 1400만 명이 넘습니다.",
        "서울의 인구는 2023년 기준 약 950만 명입니다.",
        "서울은 대한민국의 수도입니다."
    ]

    # 문서 인덱싱 (한 번만 수행)
    RAG.index(docs, index_name="demo")

    # 쿼리 입력
    query = "서울의 인구는 얼마인가요?"

    # 검색 및 reranking
    results = RAG.search(query)

    # 결과 출력
    for r in results:
        print(r)
        print(f"{r['score']} : {r['content']}")
    return results

def test_reranker_ranking():
    docs = tt2()
    print(docs)
    assert True

if __name__ == '__main__':
    print(tt2())