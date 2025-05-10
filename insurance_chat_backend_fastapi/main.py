from fastapi import FastAPI

from gh.model import OpenAIAnswerProcessor
from gh.search import SearchProcessor
from gh.keyword import RuleBasedKeywordExtractor
from gh.keyword_bert import KeywordExtractorBERT
from gh.prompts import split_complex_question
from gh.prompts import question

from embedding import GoogleEmbeddingProcessor

app = FastAPI()
# init AI model
embedding_processor = GoogleEmbeddingProcessor()

search_processor = SearchProcessor()
keyword_processor = RuleBasedKeywordExtractor()
keyword_processor_bert = KeywordExtractorBERT()

answer_processor = OpenAIAnswerProcessor();

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
    split_prompt = split_complex_question(q)

    split_answer = answer_processor.question(split_prompt)
    
    # 분해된 질문을 번호별로 나누기
    split_questions = []
    if split_answer:
        # "분해된 질문:" 이후의 텍스트만 추출
        questions_text = split_answer.split("분해된 질문:")[-1].strip()
        # 번호로 시작하는 각 줄을 개별 질문으로 분리
        for line in questions_text.split('\n'):
            if line.strip() and line.strip()[0].isdigit():
                # 번호와 점을 제거하고 질문만 추출
                question = line.split('.', 1)[1].strip()
                split_questions.append(question)

    # 각 분해된 질문에 대해 처리
    answers = []
    for split_query in split_questions:
        # STEP 02: extract keywords
        keywords = keyword_processor.extract_keywords(split_query)
        keywords_bert = keyword_processor_bert.extract_keywords(split_query)
        keywords.extend(keywords_bert)

        # STEP 03: create embedding vector
        embedding = embedding_processor.get_embedding(split_query)

        # STEP 04: hybrid search
        documents = search_processor.hybrid_search(" ".join(keywords), embedding)
        
        #TODO reranker
        # STEP 05: rerank

        #TODO documents를 openai에 전송
        # STEP 06: ask to AI
        last_question = question(documents, split_query)
        answer = answer_processor.question(last_question)
        answers.append(answer)

    # 모든 답변을 하나로 합치기
    final_answer = "\n\n".join([f"질문 {i+1}: {split_questions[i]}\n답변: {answers[i]}" for i in range(len(answers))])

    return {"question": q, "answer": final_answer}


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