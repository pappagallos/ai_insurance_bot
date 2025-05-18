from typing import List, Dict, Any
from gh.model import OpenAIAnswerProcessor
from gh.search import SearchProcessor
from gh.keyword import RuleBasedKeywordExtractor
from gh.keyword_bert import KeywordExtractorBERT
from gh.prompts import split_complex_question, question, summary_answers
from embedding import GoogleEmbeddingProcessor
from .question_service import QuestionService

class GHQuestionService(QuestionService):
    def __init__(self):
        self.embedding_processor = GoogleEmbeddingProcessor()
        self.search_processor = SearchProcessor()
        self.keyword_processor = RuleBasedKeywordExtractor()
        self.keyword_processor_bert = KeywordExtractorBERT()
        self.answer_processor = OpenAIAnswerProcessor()

    def split_question(self, user_query: str) -> List[str]:
        """복합 질문을 개별 질문으로 분해"""
        split_prompt = split_complex_question(user_query)
        split_answer = self.answer_processor.question(split_prompt).replace("분해된 질문", "").replace(":", "")
        print("[R] split raw: {}".format(split_answer))
        split_answer = user_query if (split_answer.strip() == "") else split_answer
        split_questions = []
        if split_answer:
            try:
                questions_text = split_answer.strip('[]').replace('"', '').split(',')
                split_questions = [q.strip() for q in questions_text if q.strip()]
            except Exception as e:
                print(f"Error parsing split_answer: {e}")
                split_questions = []
        print("[R] split user question: {}".format(split_questions))
        return split_questions

    def extract_keywords(self, user_query: str) -> Dict[str, List[str]]:
        """키워드 추출 (규칙 기반 + BERT)"""
        rule_based_keywords = self.keyword_processor.extract_keywords(user_query)
        bert_keywords = self.keyword_processor_bert.extract_keywords(user_query)
        rule_based_keywords.extend(bert_keywords)
        all_keywords = list(set(rule_based_keywords))
        print("[R] recognized keywords: {}".format(all_keywords))
        return {
            "keywords": all_keywords,
            "rule_based_keywords": rule_based_keywords,
            "bert_keywords": bert_keywords
        }

    def search_documents(self, user_query: str) -> List[Dict[str, Any]]:
        """하이브리드 검색 수행"""
        # 키워드 추출
        keywords = self.extract_keywords(user_query)["keywords"]
        
        # 임베딩 생성
        embedding = self.embedding_processor.get_embedding(user_query)

        # 하이브리드 검색
        documents = self.search_processor.hybrid_search(" ".join(keywords), embedding)
        print("[R] found {} documents".format(len(documents)))
        return [doc.to_json() for doc in documents]

    def generate_answer(self, user_query: str, documents: List[Dict[str, Any]]) -> str:
        """검색 결과를 바탕으로 답변 생성"""
        last_question = question(documents, user_query)
        
        return self.answer_processor.question(last_question)

    def process_question(self, user_query: str) -> Dict[str, str]:
        """전체 질문 처리 파이프라인"""
        # STEP 01: 질문 분해
        split_questions = self.split_question(user_query)
        if not split_questions:
            return {"question": user_query, "answer": "죄송합니다. 질문을 이해하지 못했습니다."}

        # 각 분해된 질문에 대해 처리
        answers = []
        i=0
        for split_query in split_questions:
            try:
                # STEP 02-04: 키워드 추출, 임베딩 생성, 검색
                documents = self.search_documents(split_query)
                if len(documents) == 0:
                    raise Exception("document didn't found")
                # STEP 06: 답변 생성
                answer = self.generate_answer(split_query, documents)
                print('[R-{}] answer: {}'.format(i, answer))
                answers.append(answer)
                i+=1
            except Exception as e:
                print(e)
                return {"question": user_query, "answer": "죄송합니다. 연관된 문서를 찾을 수 없습니다."} 

        # 모든 답변을 하나로 합치기
        final_answer = None
        if len(answers) > 1:
            summary_prompt = summary_answers(answers)
            final_answer = self.answer_processor.question(summary_prompt)
        elif len(answer) == 1:
            final_answer = answers[0]
        else:
            final_answer = "죄송합니다. 질문을 이해하지 못했습니다."

        return {"question": user_query, "answer": final_answer} 