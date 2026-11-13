"""Optional independent ID metrics. Invoke in the separate RAGAS environment."""

import asyncio
import json
import os
import sys
from importlib.metadata import version
from pathlib import Path
from statistics import mean

os.environ["RAGAS_DO_NOT_TRACK"] = "true"
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import IDBasedContextPrecision, IDBasedContextRecall


async def score(path: Path):
    snapshot = json.loads(path.read_text())
    gold = json.loads((Path(__file__).resolve().parents[1] / "data/evaluation.json").read_text())
    by_case = {(c["company"], c["question"]): c for c in snapshot["cases"]}
    recall = IDBasedContextRecall()
    precision = IDBasedContextPrecision()
    result = []
    for reference in gold:
        row = by_case[(reference["company"], reference["question"])]
        sample = SingleTurnSample(
            retrieved_context_ids=row["retrieved_ids"], reference_context_ids=reference["expected"]
        )
        result.append(
            {
                "company": row["company"],
                "question": row["question"],
                "recall": await recall.single_turn_ascore(sample),
                "precision": await precision.single_turn_ascore(sample),
            }
        )
    return {
        "evaluation": snapshot["id"],
        "ragas_version": version("ragas"),
        "cases": result,
        "mean_context_recall": mean(c["recall"] for c in result),
        "mean_context_precision": mean(c["precision"] for c in result),
    }


if __name__ == "__main__":
    print(json.dumps(asyncio.run(score(Path(sys.argv[1]))), indent=2))
