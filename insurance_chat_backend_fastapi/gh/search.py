from elasticsearch import Elasticsearch
from typing import List, Dict, Any
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    id: str
    score: float
    insurance_name: str
    insurance_type: str
    index_title: str
    chapter_title: str
    article_title: str
    content: str

    def to_json(self) -> dict:
        """
        SearchResult 객체를 JSON 형식의 딕셔너리로 변환합니다.
        
        Returns:
            JSON 형식의 딕셔너리
        """
        return {
            "insurance_name": self.insurance_name + "(" + self.insurance_type + ")",
            "title": {
                "main": self.index_title,
                "sub": self.chapter_title,
                "sub_sub": self.article_title
            },
            "content": self.content
        }

class SearchProcessor:
    def __init__(self, es_host: str = "http://localhost:9200"):
        self.es = Elasticsearch(es_host)
        self.index_name = "insurance-data1"
        
    def hybrid_search(self, query: str, embedding_vector: List[float], k: int = 5) -> List[SearchResult]:
        """
        질문과 임베딩 벡터를 사용하여 hybrid search를 수행합니다.
        
        Args:
            query: 사용자의 질문
            embedding_vector: 질문의 임베딩 벡터
            k: 반환할 결과의 수
            
        Returns:
            SearchResult 객체 리스트
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
                                    # "insurance_name",
                                    # "insurance_type",
                                    "index_title^1",
                                    "chapter_title^2",
                                    "article_title^3",
                                    "article_content^0.5"
                                ],
                                "operator": "OR",
                                "boost": 0.005
                            }
                        }
                        # 벡터 기반 검색 (KNN)
                        , {
                            "knn": {
                                "field":"embedding",
                                "query_vector": embedding_vector,
                                "k": k
                            }
                        }
                    ]
                }
            }
        }
        logger.info("[R] search query: {}".format(search_query))
        try:
            response = self.es.search(
                index=self.index_name,
                body=search_query
            )
            #print("query={}".format(search_query))
            # 검색 결과 처리
            results = []
            for hit in response["hits"]["hits"]:
                result = SearchResult(
                    id=hit["_id"],
                    score=hit["_score"],
                    insurance_name=hit["_source"].get("insurance_name", ""),
                    insurance_type=hit["_source"].get("insurance_type", ""),
                    index_title=hit["_source"].get("index_title", ""),
                    chapter_title=hit["_source"].get("chapter_title", ""),
                    article_title=hit["_source"].get("article_title", ""),
                    content=hit["_source"].get("article_content", "")
                )
                results.append(result)
            logger.info("Found {} documents".format(len(results)))
            logger.debug("Search\\n query: {}\\n results: {}".format(search_query, results))
            return results
            
        except Exception as e:
            logger.error(f"검색 중 오류 발생: {e}")
            return []
            