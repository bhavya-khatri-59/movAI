import numpy as np

class MetricsEvaluator:
    """
    Module 15: Evaluation and Metrics
    Calculates operational metrics like Precision@K, Recall@K, NDCG, and Average RL Reward.
    """
    @staticmethod
    def precision_at_k(recommended_ids: list, relevant_ids: set, k: int = 10) -> float:
        """Percentage of recommended items in Top-K that are relevant."""
        if not recommended_ids or k <= 0: return 0.0
        top_k = set(recommended_ids[:k])
        hits = len(top_k.intersection(relevant_ids))
        return hits / min(k, len(top_k))

    @staticmethod
    def recall_at_k(recommended_ids: list, relevant_ids: set, k: int = 10) -> float:
        """Percentage of total relevant items retrieved in Top-K."""
        if not relevant_ids or k <= 0: return 0.0
        top_k = set(recommended_ids[:k])
        hits = len(top_k.intersection(relevant_ids))
        return hits / len(relevant_ids)

    @staticmethod
    def average_reward(rewards: list) -> float:
        """Rolling average of RL rewards over a session."""
        if not rewards: return 0.0
        return float(np.mean(rewards))

    @staticmethod
    def click_through_rate(clicks: int, impressions: int) -> float:
        """CTR metric."""
        if impressions == 0: return 0.0
        return clicks / impressions

metrics_evaluator = MetricsEvaluator()
