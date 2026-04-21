import asyncio
import json
import os
import time
from engine.runner import BenchmarkRunner
from engine.retrieval_eval import RetrievalEvaluator
from engine.llm_judge import LLMJudge
from agent.main_agent import MainAgent

def resolve_dataset_path() -> str | None:
    candidates = [
        "data/golden_set.jsonl",
        "data/data/golden_set.jsonl",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

async def run_benchmark_with_results(
    agent_version: str,
    agent: MainAgent | None = None,
    evaluator: RetrievalEvaluator | None = None,
    judge: LLMJudge | None = None,
):
    print(f"🚀 Khởi động Benchmark cho {agent_version}...")

    dataset_path = resolve_dataset_path()
    if not dataset_path:
        print("❌ Thiếu data/golden_set.jsonl. Hãy chạy 'python data/synthetic_gen.py' trước.")
        return None, None

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print("❌ File data/golden_set.jsonl rỗng. Hãy tạo ít nhất 1 test case.")
        return None, None

    case_limit_env = os.getenv("BENCHMARK_LIMIT", "0")
    try:
        case_limit = int(case_limit_env)
    except ValueError:
        case_limit = 0
    if case_limit > 0:
        dataset = dataset[:case_limit]
        print(f"ℹ️ Đang chạy benchmark với {case_limit} cases đầu tiên (BENCHMARK_LIMIT={case_limit}).")

    batch_size_env = os.getenv("BENCHMARK_BATCH_SIZE", "5")
    try:
        batch_size = max(1, int(batch_size_env))
    except ValueError:
        batch_size = 5

    runner = BenchmarkRunner(
        agent or MainAgent(),
        evaluator or RetrievalEvaluator(),
        judge or LLMJudge(),
    )
    results = await runner.run_all(dataset, batch_size=batch_size)

    total = len(results)
    if total == 0:
        print("❌ Không có kết quả benchmark hợp lệ.")
        return None, None

    summary = {
        "metadata": {"version": agent_version, "total": total, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")},
        "metrics": {
            "avg_score": sum(r["judge"]["final_score"] for r in results) / total,
            "hit_rate": sum(r["ragas"]["retrieval"]["hit_rate"] for r in results) / total,
            "avg_mrr": sum(r["ragas"]["retrieval"].get("mrr", 0.0) for r in results) / total,
            "agreement_rate": sum(r["judge"]["agreement_rate"] for r in results) / total,
        }
    }
    return results, summary

async def run_benchmark(version):
    _, summary = await run_benchmark_with_results(version)
    return summary

async def main():
    shared_agent = MainAgent()
    shared_evaluator = RetrievalEvaluator()
    shared_judge = LLMJudge()

    _, v1_summary = await run_benchmark_with_results(
        "Agent_V1_Base",
        agent=shared_agent,
        evaluator=shared_evaluator,
        judge=shared_judge,
    )
    
    # Giả lập V2 có cải tiến (để test logic)
    v2_results, v2_summary = await run_benchmark_with_results(
        "Agent_V2_Optimized",
        agent=shared_agent,
        evaluator=shared_evaluator,
        judge=shared_judge,
    )
    
    if not v1_summary or not v2_summary:
        print("❌ Không thể chạy Benchmark. Kiểm tra lại data/golden_set.jsonl.")
        return

    print("\n📊 --- KẾT QUẢ SO SÁNH (REGRESSION) ---")
    delta = v2_summary["metrics"]["avg_score"] - v1_summary["metrics"]["avg_score"]
    print(f"V1 Score: {v1_summary['metrics']['avg_score']}")
    print(f"V2 Score: {v2_summary['metrics']['avg_score']}")
    print(f"Delta: {'+' if delta >= 0 else ''}{delta:.2f}")

    os.makedirs("reports", exist_ok=True)
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(v2_summary, f, ensure_ascii=False, indent=2)
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v2_results, f, ensure_ascii=False, indent=2)

    if delta > 0:
        print("✅ QUYẾT ĐỊNH: CHẤP NHẬN BẢN CẬP NHẬT (APPROVE)")
    else:
        print("❌ QUYẾT ĐỊNH: TỪ CHỐI (BLOCK RELEASE)")

if __name__ == "__main__":
    asyncio.run(main())
