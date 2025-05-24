import os
from openai import OpenAI
from typing import List
import time
from dotenv import load_dotenv
import tiktoken
import logging
import threading

logger = logging.getLogger(__name__)
class OpenAIAnswerProcessor:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            load_dotenv()
            api_key = os.getenv("openai.api.key")
            if not api_key:
                raise ValueError("openai.api.key 환경 변수가 설정되지 않았습니다.")
            client = OpenAI(api_key=api_key)
            print("Open AI is ready")
            self.client = client
            
    def question(self, query: str) -> str:
        response = self.client.chat.completions.create(
            model="o4-mini",  # 사용할 OpenAI 모델
            messages=[
                {"role": "user", "content": query}
            ],
        )
        logger.info("[R] response: {}".format(response.choices[0].message.content))
        return response.choices[0].message.content


class OpenAIEmbeddingProcessor:
    MODEL_NAME = "text-embedding-3-small"
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            load_dotenv()
            api_key = os.getenv("openai.api.key")
            if not api_key:
                raise ValueError("openai.api.key 환경 변수가 설정되지 않았습니다.")
            client = OpenAI(api_key=api_key)
            print("Open AI is ready")
            self.client = client
            self.encoding = tiktoken.encoding_for_model(self.MODEL_NAME)

    async def get_embedding(self, text: str) -> List[float]:
        """OpenAI API를 사용하여 텍스트를 임베딩합니다."""
        try:
            # 텍스트가 너무 길면 청크로 나누어 처리
            if self._get_token_count(text) > 8000:
                chunks = self._split_text_into_chunks(text)
                embeddings = []
                for chunk in chunks:
                    embedding = self.client.embeddings.create(
                        input=chunk,
                        model=self.MODEL_NAME
                    ).data[0].embedding
                    embeddings.append(embedding)
                    time.sleep(0.1)  # API 호출 제한을 위한 대기
                # 청크들의 임베딩을 평균하여 하나의 임베딩으로 통합
                if embeddings:
                    return [sum(x) / len(x) for x in zip(*embeddings)]
                return []
            else:
                embedding = self.client.embeddings.create(
                    input=text,
                    model=self.MODEL_NAME
                ).data[0].embedding
                return embedding
        except Exception as e:
            print(f"임베딩 생성 중 오류 발생: {e}")
            return []

    def _get_token_count(self, text: str) -> int:
        """텍스트의 토큰 수를 계산합니다."""
        return len(self.encoding.encode(text))

    def _split_text_into_chunks(self, text: str, max_tokens: int = 8000, overlap: int = 200) -> List[str]:
        """텍스트를 최대 토큰 수를 기준으로 청크로 나눕니다."""
        tokens = self.encoding.encode(text)
        chunks = []
        current_chunk = []
        current_length = 0
        overlap_buffer = []
        for i, token in enumerate(tokens):
            if current_length + 1 <= max_tokens:
                current_chunk.append(token)
                current_length += 1
                if len(overlap_buffer) < overlap:
                    overlap_buffer.append(token)
                else:
                    overlap_buffer.pop(0)
                    overlap_buffer.append(token)
            else:
                chunks.append(self.encoding.decode(current_chunk))
                current_chunk = overlap_buffer.copy()
                current_length = len(overlap_buffer)
                current_chunk.append(token)
                current_length += 1
        if current_chunk:
            chunks.append(self.encoding.decode(current_chunk))
        return chunks