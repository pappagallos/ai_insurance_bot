from abc import ABC, abstractmethod
from konlpy.tag import Okt
from collections import Counter
from typing import List, Dict
import re

class KeywordExtractor(ABC):
    """키워드 추출을 위한 추상 기본 클래스"""
    
    @abstractmethod
    def extract_keywords(self, text: str, top_n: int = 5) -> List[Dict[str, any]]:
        """
        텍스트에서 핵심 키워드를 추출합니다.
        
        Args:
            text: 분석할 자연어 텍스트
            top_n: 반환할 키워드의 수
            
        Returns:
            키워드와 점수를 포함한 딕셔너리 리스트
        """
        pass

class RuleBasedKeywordExtractor(KeywordExtractor):
    """규칙 기반 키워드 추출기 (Okt 사용)"""
    
    def __init__(self):
        self.okt = Okt()
        # 일반적인 조사와 접속사만 불용어로 설정
        self.stop_words = {
            '이', '그', '저', '것', '수', '등', '및', '또는', '그리고', '하지만',
            '때문', '위해', '대해', '관련', '대한', '있는', '없는', '하는', '된',
            '있는', '없는', '하는', '된', '될', '될', '되는', '되는', '되는'
        }
        
    def extract_keywords(self, text: str, top_n: int = 5) -> List[Dict[str, any]]:
        """
        Okt를 사용하여 텍스트에서 핵심 키워드를 추출합니다.
        
        Args:
            text: 분석할 자연어 텍스트
            top_n: 반환할 키워드의 수
            
        Returns:
            키워드와 빈도수를 포함한 딕셔너리 리스트
        """
        # 텍스트 전처리
        text = self._preprocess_text(text)
        
        # 형태소 분석
        pos_tags = self.okt.pos(text)
        
        # 명사, 동사, 형용사 추출
        keywords = []
        for word, pos in pos_tags:
            if pos in ['Noun', 'Verb', 'Adjective'] and word not in self.stop_words:
                # 동사, 형용사의 경우 어간 추출
                if pos in ['Verb', 'Adjective']:
                    word = word + '다'
                keywords.append(word)
        
        # 빈도수 계산
        keyword_freq = Counter(keywords)
        
        # 상위 N개 키워드 반환
        result = []
        for word, freq in keyword_freq.most_common(top_n):
            result.append({
                "keyword": word,
                "score": freq
            })
            
        return result
    
    def _preprocess_text(self, text: str) -> str:
        """
        텍스트 전처리를 수행합니다.
        
        Args:
            text: 전처리할 텍스트
            
        Returns:
            전처리된 텍스트
        """
        # 특수문자 제거
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 앞뒤 공백 제거
        text = text.strip()
        
        return text 