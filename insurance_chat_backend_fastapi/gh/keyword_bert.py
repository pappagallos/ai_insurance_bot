from keybert import KeyBERT
from transformers import BertTokenizer, BertModel
from typing import List, Dict
import torch
import numpy as np
from .keyword import KeywordExtractor

class KeywordExtractorBERT(KeywordExtractor):
    """BERT 기반 키워드 추출기 (monologg KoBERT 사용)"""
    
    def __init__(self):
        # monologg KoBERT 모델 로드
        model_name = "monologg/kobert"
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name, trust_remote_code=True)
        
        # KeyBERT 초기화
        self.keybert = KeyBERT(model=self.model)
        
    def extract_keywords(self, text: str, top_n: int = 5, 
                        min_ngram: int = 1, max_ngram: int = 2) -> List[str]:
        """
        monologg KoBERT와 KeyBERT를 사용하여 텍스트에서 핵심 키워드를 추출합니다.
        
        Args:
            text: 분석할 자연어 텍스트
            top_n: 반환할 키워드의 수
            min_ngram: 최소 n-gram 길이
            max_ngram: 최대 n-gram 길이
            
        Returns:
            키워드와 유사도 점수를 포함한 딕셔너리 리스트
        """
        try:
            # KeyBERT를 사용하여 키워드 추출
            keywords = self.keybert.extract_keywords(
                text,
                keyphrase_ngram_range=(min_ngram, max_ngram),
                stop_words=[
                    '이', '그', '저', '것', '수', '등', '및', '또는', '그리고', '하지만',
                    '때문', '위해', '대해', '관련', '대한', '있는', '없는', '하는', '된',
                    '있는', '없는', '하는', '된', '될', '될', '되는', '되는', '되는'
                ],
                top_n=top_n,
                diversity=0.5  # 키워드 다양성 조절
            )
            
            # 결과 포맷 변환
            result = []
            for keyword, score in keywords:
                result.append(keyword)
                # result.append({
                #     "keyword": keyword,
                #     "score": float(score)  # numpy float를 Python float로 변환
                # })
            
            return result
            
        except Exception as e:
            print(f"키워드 추출 중 오류 발생: {e}")
            return []
            
    def get_embedding(self, text: str) -> List[float]:
        """
        텍스트의 KoBERT 임베딩을 반환합니다.
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
        """
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
            return embeddings.numpy().tolist()
        except Exception as e:
            print(f"임베딩 생성 중 오류 발생: {e}")
            return [] 