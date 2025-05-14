import numpy as np


def dcg_at_k(relevances, k):
    relevances = np.array(relevances)[:k]
    discounts = np.log2(np.arange(2, len(relevances) + 2))
    return np.sum(relevances / discounts)


def idcg_at_k(relevances, k):
    sorted_relevances = sorted(relevances, reverse=True)
    return dcg_at_k(sorted_relevances, k)


def ndcg_at_k(relevances, k):
    dcg = dcg_at_k(relevances, k)
    idcg = idcg_at_k(relevances, k)
    return dcg / idcg if idcg > 0 else 0


def ndcg_rerank_at_k(relevances, rerank_relevances, k):
    dcg = dcg_at_k(rerank_relevances, k)
    idcg = idcg_at_k(relevances, k)
    return dcg / idcg if idcg > 0 else 0
