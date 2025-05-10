import os
from google import genai
from dotenv import load_dotenv

"""
	pip install google-genai
"""
class GoogleEmbeddingProcessor:
    MODEL_NAME = "gemini-embedding-exp-03-07"
    
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("gemini.api.key")
        if not api_key:
            raise ValueError("gemini.api.key 환경 변수가 설정되지 않았습니다.")
        client = genai.Client(api_key=api_key)
        self.client = client

    def get_embedding(self, content: str) -> list[float]:
        """
        벡터 테이블 생성 쿼리
        """
        return self.client.models.embed_content(
            model=self.MODEL_NAME,
            contents=content,
        ).embeddings[0].values
