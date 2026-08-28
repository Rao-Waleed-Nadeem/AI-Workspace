from dataclasses import dataclass

from app.services.retrieval_service import (
    RetrievalResult,
)


@dataclass(frozen=True)
class RetrievalEvaluation:
    case_id: str
    retrieved: bool
    relevant: bool
    expected_pages: list[int]
    retrieved_pages: list[int]


def evaluate_retrieval(
    *,
    case_id: str,
    expected_pages: list[int],
    results: list[RetrievalResult],
) -> RetrievalEvaluation:

    retrieved_pages = [
        result.page_number
        for result in results
        if result.page_number is not None
    ]

    relevant = any(
        page in expected_pages
        for page in retrieved_pages
    )

    return RetrievalEvaluation(
        case_id=case_id,
        retrieved=bool(results),
        relevant=relevant,
        expected_pages=expected_pages,
        retrieved_pages=retrieved_pages,
    )


def calculate_retrieval_metrics(
    evaluations: list[RetrievalEvaluation],
) -> dict:

    if not evaluations:
        return {
            "retrieval_recall": 0.0,
            "retrieval_success_rate": 0.0,
        }

    relevant_count = sum(
        evaluation.relevant
        for evaluation in evaluations
    )

    retrieved_count = sum(
        evaluation.retrieved
        for evaluation in evaluations
    )

    total = len(evaluations)

    return {
        "retrieval_recall": (
            relevant_count / total
        ),
        "retrieval_success_rate": (
            retrieved_count / total
        ),
    }