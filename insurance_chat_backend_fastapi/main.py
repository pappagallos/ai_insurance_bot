from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import traceback
from services.question_service import QuestionService
from services.gh_question_service import GHQuestionService
import asyncio

class QuestionRequest(BaseModel):
    question: str

class SplitQuestionResponse(BaseModel):
    questions: List[str]

class KeywordResponse(BaseModel):
    keywords: List[str]
    # rule_based_keywords: List[str]
    # bert_keywords: List[str]
    # openai_keywords: List[str]

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]

class AnswerResponse(BaseModel):
    answer: str

class FinalAnswerResponse(BaseModel):
    question: str
    answer: str

app = FastAPI()
question_service: QuestionService = GHQuestionService() # --> 이 부분만 개별로 바꾸면 됨

@app.get("/")
def read_root():
    return {"message": "Hello, World!"} 

@app.get("/question")
def question(q: str):
    """
    사용자의 질문에 대한 답변을 생성하고 제공
    """
    try:
        return question_service.process_question(q)
    except Exception as e:
        print(f"[ERROR] /question API 호출 중 오류 발생")
        print(f"질문: {q}")
        print(f"에러 메시지: {str(e)}")
        print(f"상세 스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/split-question", response_model=SplitQuestionResponse)
def split_question(q: str):
    """
    복합 질문을 개별 질문으로 분해
    """
    try:
        questions = question_service.split_question(q)
        return SplitQuestionResponse(questions=questions)
    except Exception as e:
        print(f"[ERROR] /split-question API 호출 중 오류 발생")
        print(f"질문: {q}")
        print(f"에러 메시지: {str(e)}")
        print(f"상세 스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/keywords", response_model=KeywordResponse)
def extract_keywords_only(q: str):
    """
    질문에서 키워드만 추출 (규칙 기반 + BERT)
    """
    try:
        keywords = question_service.extract_keywords(q)
        return KeywordResponse(**keywords)
    except Exception as e:
        print(f"[ERROR] /keywords API 호출 중 오류 발생")
        print(f"질문: {q}")
        print(f"에러 메시지: {str(e)}")
        print(f"상세 스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search", response_model=SearchResponse)
def search(q: str):
    """
    키워드와 임베딩을 사용한 하이브리드 검색
    """
    try:
        documents = question_service.search_documents(q)
        return SearchResponse(results=documents)
    except Exception as e:
        print(f"[ERROR] /search API 호출 중 오류 발생")
        print(f"질문: {q}")
        print(f"에러 메시지: {str(e)}")
        print(f"상세 스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate-answer", response_model=AnswerResponse)
def generate_answer(q: str):
    """
    검색 결과를 바탕으로 답변 생성
    """
    try:
        documents = question_service.search_documents(q)
        answer = question_service.generate_answer(q, documents)
        return AnswerResponse(answer=answer)
    except Exception as e:
        print(f"[ERROR] /generate-answer API 호출 중 오류 발생")
        print(f"질문: {q}")
        print(f"에러 메시지: {str(e)}")
        print(f"상세 스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# 이하는 그냥 테스트용 API
@app.get("/retrieve")
def retrieve(q: str):
    try:
        return {"retrieve": question_service.search_processor.hybrid_search(q)}
    except Exception as e:
        print(f"[ERROR] /retrieve API 호출 중 오류 발생")
        print(f"질문: {q}")
        print(f"에러 메시지: {str(e)}")
        print(f"상세 스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/embeddings")
def get_embeddings(q: str):
    try:
        return {"embedding": question_service.embedding_processor.get_embedding(q)}
    except Exception as e:
        print(f"[ERROR] /embeddings API 호출 중 오류 발생")
        print(f"질문: {q}")
        print(f"에러 메시지: {str(e)}")
        print(f"상세 스택 트레이스:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))