import os
from fastapi import FastAPI

from gh.model import OpenAIEmbeddingProcessor
from gh.search import SearchProcessor
from gh.keyword import RuleBasedKeywordExtractor
from gh.keyword_bert import KeywordExtractorBERT
from gh.model import initClient

app = FastAPI()
# init AI model
client = initClient()
embedding_processor = OpenAIEmbeddingProcessor(client)

search_processor = SearchProcessor()
keyword_processor = RuleBasedKeywordExtractor()
keyword_processor_bert = KeywordExtractorBERT()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"} 

@app.get("/question")
def question(q: str):
    """
    사용자의 질문에 대한 답변을 생성하고 제공
    """
    #TODO pre processing to AI
    # STEP 01: 질문 cleansing

    # STEP 02: extract keywords
    keywords = keyword_processor.extract_keywords(q)
    keywords_bert = keyword_processor_bert.extract_keywords(q)
    keywords.extend(keywords_bert)

    # STEP 03: create embedding vector
    embedding = embedding_processor.get_embedding(q)

    # STEP 04: hybrid search
    documents = search_processor.hybrid_search(" ".join(keywords), embedding)
    
    #TODO documents를 openai에 전송
    # STEP 05: ask to AI
    answer = ""

    return {"question": q, "answer": answer}


# 이하는 그냥 테스트용 API
@app.get("/retrieve")
def retrieve(q: str):
    return {"retrieve": search_processor.hybrid_search(q)}

@app.get("/keyword")
def keyword(q: str):
    return {"keyword": keyword_processor.extract_keywords(q)}

@app.get("/keyword_bert")
def keyword_bert(q: str):
    return {"keyword": keyword_processor_bert.extract_keywords(q)}

@app.get("/embeddings")
def question(q: str):
    return {"embedding": embedding_processor.get_embedding(q)}