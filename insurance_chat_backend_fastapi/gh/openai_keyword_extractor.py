import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
import threading
from .keyword import KeywordExtractor

class OpenAIKeywordExtractor(KeywordExtractor):
    """
    OpenAI API를 사용하여 텍스트에서 SEO에 최적화된 키워드를 추출하는 클래스입니다.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model: str = "o1-mini"):
        """
        초기화 메서드
        
        Args:
            model: 사용할 OpenAI 모델 (기본값: "o1-mini")
        """
        if not hasattr(self, 'initialized'):
            self.initialized = True
            load_dotenv()
            api_key = os.getenv("openai.api.key")
            if not api_key:
                raise ValueError("openai.api.key 환경 변수가 설정되지 않았습니다.")
                
            self.client = OpenAI(api_key=api_key)
            self.model = model
            print(f"OpenAI Keyword Extractor initialized with model: {model}")
    
    async def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """
        OpenAI API를 사용하여 텍스트에서 SEO에 최적화된 키워드를 추출합니다.
        
        Args:
            text: 분석할 자연어 텍스트
            top_n: 반환할 키워드의 수 (기본값: 5)
            
        Returns:
            추출된 키워드 리스트
        """
        if not text.strip():
            return []
        
        
        # 사용자 프롬프트 설정
        user_prompt = f"""
        Temperature: 0.3
        당신은 SEO 전문가입니다. 주어진 텍스트에서 웹 검색에 최적화된 키워드를 추출해주세요.
        키워드는 검색량이 많고, 경쟁이 적으며, 사용자의 검색 의도와 일치해야 합니다.
        키워드는 쉼표로 구분된 문자열로 반환해주세요.
        다음 텍스트에서 가장 적합한 {top_n}개의 SEO 키워드를 추출해주세요.
        키워드는 검색량이 많고 경쟁이 적어야 하며, 사용자의 검색 의도와 일치해야 합니다.
        
        텍스트: {text}
        
        키워드 (쉼표로 구분):
        """
        
        try:
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
            )
            
            # 결과 파싱
            result = response.choices[0].message.content.strip()
            keywords = [k.strip() for k in result.split(",") if k.strip()]
            
            # 상위 N개 키워드만 반환
            return keywords[:top_n]
            
        except Exception as e:
            print(f"OpenAI 키워드 추출 중 오류 발생: {e}")
            return []
    
    def __call__(self, text: str, top_n: int = 5) -> List[str]:
        """
        클래스를 함수처럼 호출할 수 있도록 합니다.
        
        Args:
            text: 분석할 자연어 텍스트
            top_n: 반환할 키워드의 수 (기본값: 5)
            
        Returns:
            추출된 키워드 리스트
        """
        return self.extract_keywords(text, top_n)
