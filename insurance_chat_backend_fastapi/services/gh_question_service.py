from typing import List, Dict, Any, Tuple, Optional
import concurrent.futures
from functools import partial
import threading
import asyncio
from gh.model import OpenAIAnswerProcessor
from gh.search import SearchProcessor, SearchResult
# from gh.keyword import RuleBasedKeywordExtractor
# from gh.keyword_bert import KeywordExtractorBERT
from gh.prompts import split_complex_question, question, summary_answers, question_json, rerank_documents
from embedding import GoogleEmbeddingProcessor
from .question_service import QuestionService
from gh.openai_keyword_extractor import OpenAIKeywordExtractor
import logging
import time
from gh.reranker_colbert import reranker_ranking
import json
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

k = 20

class QuestionProcessor:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize processors once when the class is instantiated"""
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.embedding_processor = GoogleEmbeddingProcessor()
            self.search_processor = SearchProcessor()
            self.answer_processor = OpenAIAnswerProcessor()
            self.keyword_processor_openai = OpenAIKeywordExtractor()
            self.cache = {
                'embeddings': {},
                'search_results': {},
                'answers': {}
            }
            self.max_cache_size = 1000
            self.cache_ttl = 3600  # 1시간 캐시 유지

    async def process_question(self, query_idx: Tuple[int, str]) -> Tuple[int, Optional[str]]:
        """Process a single question using pre-initialized processors"""
        idx, split_query = query_idx
        try:
            # Measure total processing time
            start_time = time.time()
            
            # Extract keywords using OpenAI
            task_extract = self.keyword_processor_openai.extract_keywords(split_query)
            task_embedding = self.embedding_processor.get_embedding(split_query)
            results = await asyncio.gather(task_extract, task_embedding)
            openai_keywords = results[0]
            embedding = results[1]
            
            logger.info(f"[Worker-{idx}] Extracted OpenAI keywords: {openai_keywords}")        
            documents = self.search_processor.hybrid_search(" ".join(openai_keywords), embedding, k=k)

            logger.info(f"[Worker-{idx}] Found {len(documents)} documents")
            if not documents:
                raise Exception("No documents found")
            # reranked_docs = reranker_ranking(documents, split_query, k=3)
            # Generate answer
            answer_start = time.time()
            documents_json = [doc.to_json() for doc in documents]
            # prompt = question(reranked_docs, split_query)
            prompt = question_json(documents_json, split_query)
            logger.info(f"[Worker-{idx}] Generated prompt: {prompt}")
            answer = self.answer_processor.question(prompt)
            answer_end = time.time()

            # Calculate and log timing information
            total_time = time.time() - start_time
            answer_time = answer_end - answer_start
            
            logger.info(f'[Worker-{idx}] Timing stats: Total={total_time:.2f}s, Answer={answer_time:.2f}s')
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
        # self.reranker = Reranker()

    def split_question(self, user_query: str) -> List[str]:
        """복합 질문을 개별 질문으로 분해"""
        split_prompt = split_complex_question(user_query)
        split_answer = self.answer_processor.question(split_prompt)
        split_answer = split_answer.replace("복합 질문", "").replace("분해된 질문", "").replace(":", "")
        
        split_answer = user_query if (split_answer.strip() == "") else split_answer
        split_questions = []
        if split_answer:
            try:
                questions_text = split_answer.strip('[]').replace('"', '').split(',')
                split_questions = [q.strip() for q in questions_text if q.strip()]
            except Exception as e:
                logger.error(f"Error parsing split_answer: {e}")
                split_questions = []
        
        return split_questions

    async def extract_keywords(self, user_query: str) -> Dict[str, List[str]]:
        """키워드 추출 (규칙 기반 + BERT)"""
        # rule_based_keywords = self.keyword_processor.extract_keywords(user_query)
        # bert_keywords = self.keyword_processor_bert.extract_keywords(user_query)
        # rule_based_keywords.extend(bert_keywords)
        # all_keywords = list(set(rule_based_keywords))
        openai_keywords = await self.keyword_processor_openai.extract_keywords(user_query)
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

    async def search_documents(self, user_query: str) -> List[Dict[str, Any]]:
    # async def search_documents(self, user_query: str) -> List[str]:
        """
        하이브리드 검색 수행 후 재정렬을 적용합니다.
        
        Args:
            user_query: 사용자 쿼리
            
        Returns:
            재정렬된 문서 리스트 (JSON 형식)
        """
        # Extract keywords using OpenAI
        task_extract = self.keyword_processor_openai.extract_keywords(user_query)
        task_embedding = self.embedding_processor.get_embedding(user_query)
        results = await asyncio.gather(task_extract, task_embedding)
        openai_keywords = results[0]
        embedding = results[1]
        
        logger.info(f"Extracted OpenAI keywords: {openai_keywords}")        
        documents = self.search_processor.hybrid_search(" ".join(openai_keywords), embedding, k=k)
        logger.info(" found {} documents before reranking".format(len(documents)))
        
        if not documents:
            return []
            
        # 재정렬 적용
        documents_json = [doc.to_json() for doc in documents]
        # reranked_docs = reranker_ranking(documents, user_query, k=20)

        return documents_json

    async def search_documents_with_split(self, user_query: str) -> List[Dict[str, Any]]:
        split_questions = self.split_question(user_query)
        logger.info("split_questions: {}".format(len(split_questions)))
        doc_count = 0
        documents = []
        for split_question in split_questions:
            docs = await self.search_documents(split_question)
            documents.append(
                {
                    "question": split_question,
                    "documents": docs
                }
            )
            doc_count += len(docs)
        logger.info("doc found: {}".format(doc_count))
        # # documents를 평가하여 연관도가 높은 순서로 재정렬. 이때 상품의 다양성을 확보해야함
        # reranker_prompts = rerank_documents(documents, k=k)
        # reranked_indexes = self.answer_processor.question(reranker_prompts)
        # logger.info("reranked_indexes: {}".format(reranked_indexes))
        # reranked_indexes = json.loads(reranked_indexes)
        
        # # Reorder documents by question and maintain original structure
        # reordered_documents = []
        
        # # Create a mapping of question to its documents
        # question_to_docs = {doc_group["question"]: doc_group["documents"] for doc_group in documents}
        
        # # Process each question in reranked_indexes
        # for question_data in reranked_indexes:
        #     question = question_data["question"]
        #     doc_idx = question_data["doc_idx"]
            
        #     # Get original documents for this question
        #     original_docs = question_to_docs.get(question, [])
            
        #     # Reorder documents for this question
        #     reordered_question_docs = []
        #     for idx in doc_idx:
        #         if 0 <= idx < len(original_docs):
        #             reordered_question_docs.append(original_docs[idx])
            
        #     # Add reordered documents for this question
        #     reordered_documents.append({
        #         "question": question,
        #         "documents": reordered_question_docs
        #     })
        
        # return reordered_documents
        return documents

    def generate_answer(self, user_query: str, documents: List[Dict[str, Any]]) -> str:
        """검색 결과를 바탕으로 답변 생성"""
        last_question = question_json(documents, user_query)
        return self.answer_processor.question(last_question)

    def process_question(self, user_query: str) -> Dict[str, str]:
        """전체 질문 처리 파이프라인"""
        try:

            # Initialize timing dictionary
            timings = {}
            
            # STEP 01: 질문 분해
            start_time = time.time()
            split_questions = self.split_question(user_query)
            timings['split_question'] = time.time() - start_time
            
            if not split_questions:
                return {"question": user_query, "answer": "죄송합니다. 질문을 이해하지 못했습니다."}
                
            logger.info(f"Processing {len(split_questions)} questions in parallel")
            
            # Process questions in parallel
            answers = [None] * len(split_questions)
            
            # Prepare the work items
            work_items = [(i, q) for i, q in enumerate(split_questions)]
            
            # Use ThreadPoolExecutor instead of ProcessPoolExecutor to avoid pickling issues
            start_time = time.time()
            
            # Create a ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Initialize a QuestionProcessor instance
                processor = QuestionProcessor()
                
                # Create a wrapper function to handle async execution
                def process_question_wrapper(query_idx):
                    return asyncio.run(processor.process_question(query_idx))
                
                # Submit all tasks
                futures = [executor.submit(process_question_wrapper, item) for item in work_items]
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(futures):
                    try:
                        idx, answer = future.result()
                        if answer is not None:
                            answers[idx] = answer
                            logger.info(f"Successfully processed question {idx}")
                    except Exception as e:
                        logger.error(f"Error processing question: {str(e)}", exc_info=True)
            timings['parallel_processing'] = time.time() - start_time
            
            # Combine answers
            if len(answers) > 1:
                combined_prompt = summary_answers(split_questions, answers)
                final_answer = self.answer_processor.question(combined_prompt)
            else:
                final_answer = answers[0] if answers[0] else "죄송합니다. 답변을 생성하지 못했습니다."
            
            # Log timing information
            total_time = time.time() - start_time
            timings['total'] = total_time
            logger.info(f"Total processing time: {total_time:.2f}s")
            logger.info(f"Timings: {timings}")
        
            return {"question": user_query, "answer": final_answer}
        except Exception as e:
            logger.error(f"Error combining answers: {str(e)}", exc_info=True)
            return {
                "question": user_query, 
                "answer": "죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다."
            }