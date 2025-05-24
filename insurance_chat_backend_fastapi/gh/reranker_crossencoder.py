from typing import List, Dict, Any
import numpy as np
from dataclasses import dataclass
from sentence_transformers import CrossEncoder
import logging

logger = logging.getLogger(__name__)

class Reranker:
    def __init__(self, model_name: str = "BM-K/KoMiniLM"):
        """
        Reranker 초기화
        
        Args:
            model_name: 사용할 Cross-Encoder 모델 이름 (기본값: BM-K/KoMiniLM)
        """
        logger.info(f"Loading reranker model: {model_name}")
        self.model = CrossEncoder(model_name)
        self.model_name = model_name
    
    def rerank(
        self, 
        query: str, 
        documents: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        검색 결과를 재정렬합니다.
        
        Args:
            query: 사용자 쿼리
            documents: 재정렬할 문서 리스트 (SearchResult.to_json() 형식)
            top_k: 반환할 상위 문서 수
            
        Returns:
            재정렬된 문서 리스트 (원본 문서 형식 유지)
        """
        if not documents:
            return []
            
        # 문서와 쿼리 쌍 생성
        pairs = []
        for doc in documents:
            # 문서의 모든 텍스트를 하나의 문자열로 결합
            doc_text = " "
            if isinstance(doc, dict):
                # SearchResult.to_json() 형식 처리
                title = doc.get('title', {})
                doc_text = " ".join([
                    title.get('main', ''),
                    title.get('sub', ''),
                    title.get('sub_sub', ''),
                    doc.get('content', '')
                ])
            elif hasattr(doc, 'content'):
                # SearchResult 객체 직접 처리 (필요한 경우)
                doc_text = f"{doc.index_title} {doc.chapter_title} {doc.article_title} {doc.content}"
            
            pairs.append((query, doc_text))
        
        if not pairs:
            return []
            
        # 점수 예측
        try:
            scores = self.model.predict(pairs)
        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            return documents[:top_k]  # 에러 발생 시 원본 순서 반환
        
        # 문서와 점수를 묶고 점수 기준으로 정렬
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 k개 문서 반환 (점수는 제외)
        return [doc for doc, score in scored_docs[:top_k]]
