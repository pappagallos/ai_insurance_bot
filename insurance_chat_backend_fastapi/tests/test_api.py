from fastapi.testclient import TestClient
import pytest
from main import app

client = TestClient(app)

def test_split_question():
    """복합 질문 분해 API 테스트"""
    response = client.post(
        "/split-question",
        json={"question": "암보험 가입 나이 제한과 보장 내용, 그리고 가입 방법을 알려줘"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert isinstance(data["questions"], list)
    assert len(data["questions"]) > 0

def test_extract_keywords():
    """키워드 추출 API 테스트"""
    response = client.post(
        "/keywords",
        json={"question": "암보험 가입 나이 제한과 보장 내용, 그리고 가입 방법을 알려줘"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "keywords" in data
    assert "rule_based_keywords" in data
    assert "bert_keywords" in data
    assert isinstance(data["keywords"], list)
    assert isinstance(data["rule_based_keywords"], list)
    assert isinstance(data["bert_keywords"], list)
    assert len(data["keywords"]) > 0
    # 중복 제거 확인
    assert len(data["keywords"]) <= len(data["rule_based_keywords"]) + len(data["bert_keywords"])

def test_search():
    """하이브리드 검색 API 테스트"""
    response = client.post(
        "/search",
        json={"question": "암보험 가입 나이 제한과 보장 내용, 그리고 가입 방법을 알려줘"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    if len(data["results"]) > 0:
        result = data["results"][0]
        assert "insurance_name" in result
        assert "title" in result
        assert "content" in result

def test_generate_answer():
    """답변 생성 API 테스트"""
    response = client.post(
        "/generate-answer",
        json={"question": "암보험 가입 나이 제한과 보장 내용, 그리고 가입 방법을 알려줘"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0

def test_question_endpoint():
    """전체 질문 처리 파이프라인 API 테스트"""
    response = client.post(
        "/question",
        json={"question": "암보험 가입 나이 제한과 보장 내용, 그리고 가입 방법을 알려줘"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0

def test_error_handling():
    """에러 처리 테스트"""
    # 잘못된 요청 형식
    response = client.post(
        "/question",
        json={"invalid_field": "test"}
    )
    assert response.status_code == 422  # Validation Error

    # 빈 질문
    response = client.post(
        "/question",
        json={"question": ""}
    )
    assert response.status_code == 200  # 빈 질문은 허용되지만 답변은 "이해하지 못했습니다" 메시지
    data = response.json()
    assert "죄송합니다. 질문을 이해하지 못했습니다." in data["answer"] 