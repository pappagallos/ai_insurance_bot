from ragatouille import RAGPretrainedModel
from typing import List
import logging
from gh.search import SearchResult

logger = logging.getLogger(__name__)

import torch

# Check if MPS is available and use it if possible
if torch.backends.mps.is_available():
    device = torch.device("mps")
    logger.info("Using MPS device")
else:
    device = torch.device("cpu")
    logger.info("Using CPU")

reranker_model = RAGPretrainedModel.from_pretrained("jinaai/jina-colbert-v2")
# Move model to device
# reranker_model.to(device)

def reranker_ranking(docs:List[SearchResult], query:str, k:int=3) -> List[str]:
    # 문서 인덱싱 (한 번만 수행)
    contents = []
    for doc in docs:
        contents.append("{title:" + doc.index_title + "\n" 
        + "sub_title:" + doc.chapter_title + "\n" 
        + "sub_sub_title:" + doc.article_title + "\n"  
        + "content:" + doc.content + "}")
    
    # 검색 및 reranking
    results = reranker_model.rerank(
        query=query,
        documents=contents,
        k=len(contents)
    )[0:k]

    # 결과 출력
    # for r in results:
    #     logger.info("{}".format(r))
      
    return [r['content'] for r in results]
