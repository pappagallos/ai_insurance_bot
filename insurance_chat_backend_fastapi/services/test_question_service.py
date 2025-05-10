from typing import List, Dict, Any
from .question_service import QuestionService

class TestQuestionService(QuestionService):
    """테스트용 질문 처리 서비스"""
    
    def split_question(self, user_query: str) -> List[str]:
        """테스트용 질문 분해 - 단순히 입력을 리스트로 반환"""
        return [user_query]

    def extract_keywords(self, user_query: str) -> Dict[str, List[str]]:
        """테스트용 키워드 추출 - 단순히 입력을 키워드로 사용"""
        return {
            "keywords": [user_query],
            "rule_based_keywords": [user_query],
            "bert_keywords": []
        }

    def search_documents(self, user_query: str) -> List[Dict[str, Any]]:
        """테스트용 문서 검색 - 더미 데이터 반환"""
        return [{
            "insurance_name": "테스트 보험",
            "title": "테스트 제목",
            "content": "테스트 내용"
        }]

    def generate_answer(self, user_query: str, documents: List[Dict[str, Any]]) -> str:
        """테스트용 답변 생성 - 더미 답변 반환"""
        return f"테스트 답변: {user_query}"

    def process_question(self, user_query: str) -> Dict[str, str]:
        """테스트용 전체 처리 - 더미 응답 반환"""
        return {
            "question": user_query,
            "answer": f"테스트 응답: {user_query}"
        }