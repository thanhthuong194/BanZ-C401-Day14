from typing import List, Dict

class RetrievalEvaluator:
    def __init__(self):
        self.name = "retrieval-evaluator"

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        top_retrieved = retrieved_ids[:top_k]
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    async def score(self, test_case: Dict, response: Dict) -> Dict:
        """
        Chấm retrieval metrics cho 1 test case để dùng trực tiếp trong BenchmarkRunner.
        """
        expected_ids = test_case.get("expected_retrieval_ids") or []
        retrieved_ids = response.get("retrieved_ids") or []
        top_k = int(test_case.get("top_k", 3))

        if not expected_ids or not retrieved_ids:
            return {
                "retrieval": {
                    "hit_rate": 0.0,
                    "mrr": 0.0,
                }
            }

        return {
            "retrieval": {
                "hit_rate": self.calculate_hit_rate(expected_ids, retrieved_ids, top_k=top_k),
                "mrr": self.calculate_mrr(expected_ids, retrieved_ids),
            }
        }

    async def evaluate_batch(self, dataset: List[Dict]) -> Dict:
        """
        Chạy eval cho toàn bộ bộ dữ liệu.
        Dataset cần có trường 'expected_retrieval_ids' và Agent trả về 'retrieved_ids'.
        """
        if not dataset:
            return {
                "avg_hit_rate": 0.0,
                "avg_mrr": 0.0,
                "total_cases": 0,
                "valid_cases": 0,
                "skipped_cases": 0
            }

        hit_scores: List[float] = []
        mrr_scores: List[float] = []
        skipped_cases = 0

        for item in dataset:
            expected_ids = item.get("expected_retrieval_ids") or []
            retrieved_ids = item.get("retrieved_ids") or []
            top_k = item.get("top_k", 3)

            if not expected_ids or not retrieved_ids:
                skipped_cases += 1
                continue

            hit_scores.append(
                self.calculate_hit_rate(expected_ids, retrieved_ids, top_k=top_k)
            )
            mrr_scores.append(
                self.calculate_mrr(expected_ids, retrieved_ids)
            )

        valid_cases = len(hit_scores)
        if valid_cases == 0:
            return {
                "avg_hit_rate": 0.0,
                "avg_mrr": 0.0,
                "total_cases": len(dataset),
                "valid_cases": 0,
                "skipped_cases": skipped_cases
            }

        return {
            "avg_hit_rate": sum(hit_scores) / valid_cases,
            "avg_mrr": sum(mrr_scores) / valid_cases,
            "total_cases": len(dataset),
            "valid_cases": valid_cases,
            "skipped_cases": skipped_cases
        }
