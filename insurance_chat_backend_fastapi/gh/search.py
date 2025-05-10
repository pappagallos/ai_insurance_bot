from elasticsearch import Elasticsearch
from typing import List, Dict, Any
import numpy as np

class SearchProcessor:
    def __init__(self, es_host: str = "http://localhost:9200"):
        self.es = Elasticsearch(es_host)
        self.index_name = "insurance-data"
        
    def hybrid_search(self, query: str, embedding_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """
        질문과 임베딩 벡터를 사용하여 hybrid search를 수행합니다.
        
        Args:
            query: 사용자의 질문
            embedding_vector: 질문의 임베딩 벡터
            k: 반환할 결과의 수
            
        Returns:
            검색 결과 리스트
        """
        # Hybrid search 쿼리 구성
        search_query = {
            "size": k,
            "query": {
                "bool": {
                    "should": [
                        # BM25F 기반 검색
                        {
                            "multi_match": {
                                "query": query,
                                "type": "most_fields",
                                "fields": [
                                    "insurance_name^3",
                                    "insurance_type^2",
                                    "index_title^2",
                                    "chapter_title^2",
                                    "article_title^2"
                                ],
                                "boost": 0.3
                            }
                        },
                        # 벡터 기반 검색 (KNN)
                        {
                            "knn": {
                                "field":"embedding",
                                "query_vector": embedding_vector,
                                "k": 10
                            },
                            "boost":0.7
                        }
                        # {
                        #     "script_score": {
                        #         "query": {"match_all": {}},
                        #         "script": {
                        #             "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        #             "params": {"query_vector": embedding_vector}
                        #         },
                        #         "boost": 0.7
                        #     }
                        # }
                    ]
                }
            }
        }
        
        try:
            response = self.es.search(
                index=self.index_name,
                body=search_query
            )
            
            # 검색 결과 처리
            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "id": hit["_id"],
                    "score": hit["_score"],
                    "insurance_name": hit["_source"].get("insurance_name", ""),
                    "insurance_type": hit["_source"].get("insurance_type", ""),
                    "index_title": hit["_source"].get("index_title", ""),
                    "chapter_title": hit["_source"].get("chapter_title", ""),
                    "article_title": hit["_source"].get("article_title", ""),
                    "content": hit["_source"].get("content", "")
                })
            
            return results
            
        except Exception as e:
            print(f"검색 중 오류 발생: {e}")
            return []
            