import json
from pathlib import Path

from app.database import SessionLocal
from evaluation.models import RAGEvaluationCase
from evaluation.rag_evaluator import (
    evaluate_retrieval,
    calculate_retrieval_metrics,
)
from app.services.retrieval_service import RetrievalService


DATASET_PATH = (
    Path(__file__).parent
    / "rag_dataset.json"
)


def load_dataset() -> list[RAGEvaluationCase]:

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        raw_cases = json.load(file)

    return [
        RAGEvaluationCase(
            id=item["id"],
            question=item["question"],
            document_id=item["document_id"],
            expected_pages=item["expected_pages"],
            expected_facts=item["expected_facts"],
            should_answer=item["should_answer"],
        )
        for item in raw_cases
    ]


def main():

    cases = load_dataset()

    db = SessionLocal()

    retrieval_service = RetrievalService()

    evaluations = []

    try:

        for case in cases:

            results = retrieval_service.retrieve(
                db=db,
                question=case.question,
                user_id=1,
                document_id=case.document_id,
                top_k=5,
                min_similarity=0.35,
            )

            evaluation = evaluate_retrieval(
                case_id=case.id,
                expected_pages=case.expected_pages,
                results=results,
            )

            evaluations.append(
                evaluation
            )

            print("=" * 60)
            print(f"Case: {case.id}")
            print(f"Question: {case.question}")
            print(
                f"Expected pages: "
                f"{case.expected_pages}"
            )
            print(
                f"Retrieved pages: "
                f"{evaluation.retrieved_pages}"
            )
            print(
                f"Relevant: "
                f"{evaluation.relevant}"
            )

        metrics = calculate_retrieval_metrics(
            evaluations,
        )

        print("\n")
        print("=" * 60)
        print("RAG RETRIEVAL EVALUATION")
        print("=" * 60)

        for name, value in metrics.items():
            print(
                f"{name}: "
                f"{value:.2%}"
            )

    finally:

        db.close()


if __name__ == "__main__":
    main()