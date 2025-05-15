from typing import List, Dict, Any, Tuple, Optional
import concurrent.futures
from functools import partial
from gh.model import OpenAIAnswerProcessor
from gh.search import SearchProcessor, SearchResult
from gh.keyword import RuleBasedKeywordExtractor
from gh.keyword_bert import KeywordExtractorBERT
from gh.prompts import split_complex_question, question, summary_answers
from gh.reranker import Reranker
from embedding import GoogleEmbeddingProcessor
from .question_service import QuestionService
from gh.openai_keyword_extractor import OpenAIKeywordExtractor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

k = 20

def _process_single_question_worker(query_idx: Tuple[int, str]) -> Tuple[int, Optional[str]]:
    """Worker function for processing a single question in a separate process"""
    idx, split_query = query_idx
    try:
        # Create new instances of all required processors
        embedding_processor = GoogleEmbeddingProcessor()
        search_processor = SearchProcessor()
        answer_processor = OpenAIAnswerProcessor()
        keyword_processor_openai = OpenAIKeywordExtractor()
        
        # Extract keywords using OpenAI
        openai_keywords = keyword_processor_openai.extract_keywords(split_query)
        logger.info(f"[Worker-{idx}] Extracted OpenAI keywords: {openai_keywords}")
        
        # Perform search
        embedding = embedding_processor.get_embedding(split_query)
        documents = search_processor.hybrid_search(" ".join(openai_keywords), embedding, k=k)
        
        if not documents:
            raise Exception("No documents found")
            
        # Generate answer
        documents_json = [doc.to_json() for doc in documents]
        prompt = question(documents_json, split_query)
        answer = answer_processor.question(prompt)
        
        logger.info(f'[Worker-{idx}] Successfully processed question')
        return idx, answer
        
    except Exception as e:
        logger.error(f"Error in worker processing question {idx}: {str(e)}", exc_info=True)
        return idx, None

class GHQuestionService(QuestionService):
    def __init__(self):
        self.embedding_processor = GoogleEmbeddingProcessor()
        self.search_processor = SearchProcessor()
        # self.keyword_processor = RuleBasedKeywordExtractor()
        # self.keyword_processor_bert = KeywordExtractorBERT()
        self.answer_processor = OpenAIAnswerProcessor()
        self.keyword_processor_openai = OpenAIKeywordExtractor()
        self.reranker = Reranker()

    def split_question(self, user_query: str) -> List[str]:
        """복합 질문을 개별 질문으로 분해"""
        split_prompt = split_complex_question(user_query)
        split_answer = self.answer_processor.question(split_prompt).replace("복합 질문", "").replace("분해된 질문", "").replace(":", "")
        logger.info("[R] split raw: {}".format(split_answer))
        split_answer = user_query if (split_answer.strip() == "") else split_answer
        split_questions = []
        if split_answer:
            try:
                questions_text = split_answer.strip('[]').replace('"', '').split(',')
                split_questions = [q.strip() for q in questions_text if q.strip()]
            except Exception as e:
                logger.error(f"Error parsing split_answer: {e}")
                split_questions = []
        logger.info("[R] split user question: {}".format(split_questions))
        return split_questions

    def extract_keywords(self, user_query: str) -> Dict[str, List[str]]:
        """키워드 추출 (규칙 기반 + BERT)"""
        # rule_based_keywords = self.keyword_processor.extract_keywords(user_query)
        # bert_keywords = self.keyword_processor_bert.extract_keywords(user_query)
        # rule_based_keywords.extend(bert_keywords)
        # all_keywords = list(set(rule_based_keywords))
        openai_keywords = self.keyword_processor_openai.extract_keywords(user_query)
        logger.info("[R] openai_keywords: {}".format(openai_keywords))
        # all_keywords.extend(openai_keywords)
        # all_keywords = list(set(all_keywords))
        # print("[R] recognized keywords: {}".format(all_keywords))
        return {
            "keywords": openai_keywords,
            # "rule_based_keywords": rule_based_keywords,
            # "bert_keywords": bert_keywords,
            # "openai_keywords": openai_keywords
        }

    def search_documents(self, user_query: str) -> List[Dict[str, Any]]:
        """
        하이브리드 검색 수행 후 재정렬을 적용합니다.
        
        Args:
            user_query: 사용자 쿼리
            
        Returns:
            재정렬된 문서 리스트 (JSON 형식)
        """
        # 키워드 추출
        keywords = self.extract_keywords(user_query)["keywords"]
        unique_keywords = []
        for k in keywords:
            unique_keywords.extend(k.split(" "))
        unique_keywords = list(set(unique_keywords))
        logger.info("[R] unique_keywords: {}".format(unique_keywords))
        
        # 임베딩 생성
        embedding = self.embedding_processor.get_embedding(user_query)

        # 하이브리드 검색 (기본적으로 더 많은 문서를 가져옴)
        search_k = k * 2  # 재정렬을 위해 더 많은 문서를 가져옴
        documents = self.search_processor.hybrid_search(" ".join(unique_keywords), embedding, k=search_k)
        logger.info("[R] found {} documents before reranking".format(len(documents)))
        
        if not documents:
            return []
            
        # 재정렬 적용
        documents_json = [doc.to_json() for doc in documents]
        reranked_docs = self.reranker.rerank(user_query, documents_json, top_k=k)
        
        logger.info("[R] returned {} documents after reranking".format(len(reranked_docs)))
        return reranked_docs

    def generate_answer(self, user_query: str, documents: List[Dict[str, Any]]) -> str:
        """검색 결과를 바탕으로 답변 생성"""
        logger.info("[R] documents: {}".format(documents))
        last_question = question(documents, user_query)
        return self.answer_processor.question(last_question)

    def process_question(self, user_query: str) -> Dict[str, str]:
        """전체 질문 처리 파이프라인"""
        # STEP 01: 질문 분해
        split_questions = self.split_question(user_query)
        if not split_questions:
            return {"question": user_query, "answer": "죄송합니다. 질문을 이해하지 못했습니다."}
            
        logger.info(f"Processing {len(split_questions)} questions in parallel")
        
        # Process questions in parallel
        answers = [None] * len(split_questions)
        
        # Prepare the work items
        work_items = [(i, q) for i, q in enumerate(split_questions)]
        
        # Use ProcessPoolExecutor with the standalone worker function
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Submit all tasks
            future_to_idx = {executor.submit(_process_single_question_worker, item): item[0] 
                           for item in work_items}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    result_idx, answer = future.result()
                    if answer is not None:
                        answers[result_idx] = answer
                        logger.info(f"Successfully processed question {result_idx}")
                except Exception as e:
                    logger.error(f"Error processing question {idx}: {str(e)}", exc_info=True)
        
        # Filter out None values (failed answers)
        valid_answers = [a for a in answers if a is not None]
        
        if not valid_answers:
            logger.error("No valid answers were generated")
            return {"question": user_query, "answer": "죄송합니다. 연관된 문서를 찾을 수 없습니다."}

        # Combine answers if there are multiple
        try:
            if len(valid_answers) > 1:
                logger.info("Combining multiple answers")
                summary_prompt = summary_answers(valid_answers)
                final_answer = self.answer_processor.question(summary_prompt)
            else:
                final_answer = valid_answers[0]
                
            logger.info("Successfully generated final answer")
            return {"question": user_query, "answer": final_answer}
            
        except Exception as e:
            logger.error(f"Error combining answers: {str(e)}", exc_info=True)
            return {
                "question": user_query, 
                "answer": "죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다."
            }

        return {"question": user_query, "answer": final_answer} 