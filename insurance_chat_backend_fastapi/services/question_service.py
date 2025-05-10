from abc import ABC, abstractmethod
from typing import List, Dict, Any

class QuestionService(ABC):
    """질문 처리 서비스의 추상 클래스"""
    
    @abstractmethod
    def split_question(self, user_query: str) -> List[str]:
        """복합 질문을 개별 질문으로 분해"""
        pass

    @abstractmethod
    def extract_keywords(self, user_query: str) -> Dict[str, List[str]]:
        """키워드 추출 (규칙 기반 + BERT)"""
        pass

    @abstractmethod
    def search_documents(self, user_query: str) -> List[Dict[str, Any]]:
        """하이브리드 검색 수행"""
        pass

    @abstractmethod
    def generate_answer(self, user_query: str, documents: List[Dict[str, Any]]) -> str:
        """검색 결과를 바탕으로 답변 생성"""
        pass

    @abstractmethod
    def process_question(self, user_query: str) -> Dict[str, str]:
        """전체 질문 처리 파이프라인"""
        pass 