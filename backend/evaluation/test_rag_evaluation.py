import argparse
import json
from pathlib import Path

from app.database import SessionLocal
from app.core.config import settings
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.services.retrieval_service import RetrievalService

from evaluation.models import RAGEvaluationCase
from evaluation.rag_evaluator import (
    evaluate_retrieval,
    calculate_retrieval_metrics,
)
from evaluation.answer_evaluator import (
    evaluate_answer,
    calculate_answer_metrics,
)


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


def evaluate_retrieval_cases(
    cases: list[RAGEvaluationCase],
) -> tuple[list, dict]:

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
                top_k=settings.RAG_TOP_K,
                min_similarity=settings.RAG_MIN_SIMILARITY,
            )

            evaluation = evaluate_retrieval(
                case_id=case.id,
                expected_pages=case.expected_pages,
                results=results,
            )

            evaluations.append(evaluation)

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
                f"Retrieved: "
                f"{evaluation.retrieved}"
            )
            print(
                f"Relevant: "
                f"{evaluation.relevant}"
            )

            for result in results:
                print(
                    f"  similarity={result.similarity:.4f} "
                    f"page={result.page_number}"
                )

        metrics = calculate_retrieval_metrics(
            evaluations,
        )

        return evaluations, metrics

    finally:
        db.close()


def evaluate_answers(
    cases: list[RAGEvaluationCase],
) -> tuple[list, dict]:

    db = SessionLocal()

    chat_service = ChatService()

    evaluations = []

    try:

        for case in cases:

            request = ChatRequest(
                message=case.question,
                document_id=case.document_id,
            )

            try:

                response = chat_service.generate_response(
                    db=db,
                    request=request,
                    user_id=1,
                )

                answer = response.message

            except Exception as error:

                db.rollback()

                answer = str(error)

            evaluation = evaluate_answer(
                case_id=case.id,
                answer=answer,
                expected_facts=case.expected_facts,
                should_answer=case.should_answer,
            )

            evaluations.append(evaluation)

            print("=" * 60)
            print(f"Case: {case.id}")
            print(f"Question: {case.question}")
            print(f"Answer: {answer}")
            print(
                f"Grounded: "
                f"{evaluation.grounded}"
            )
            print(
                f"Hallucinated: "
                f"{evaluation.hallucinated}"
            )
            print(
                f"Missing information: "
                f"{evaluation.missing_information}"
            )
            print(
                f"Matched facts: "
                f"{evaluation.matched_facts}/"
                f"{evaluation.expected_facts}"
            )

        metrics = calculate_answer_metrics(
            evaluations,
        )

        return evaluations, metrics

    finally:
        db.close()


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--answers",
        action="store_true",
        help="Run end-to-end RAG answer evaluation.",
    )

    args = parser.parse_args()

    cases = load_dataset()

    _, retrieval_metrics = evaluate_retrieval_cases(
        cases,
    )

    print()
    print("=" * 60)
    print("RETRIEVAL EVALUATION")
    print("=" * 60)

    for name, value in retrieval_metrics.items():
        print(
            f"{name}: "
            f"{value:.2%}"
        )

    if args.answers:

        _, answer_metrics = evaluate_answers(
            cases,
        )

        print()
        print("=" * 60)
        print("ANSWER EVALUATION")
        print("=" * 60)

        for name, value in answer_metrics.items():
            print(
                f"{name}: "
                f"{value:.2%}"
            )


if __name__ == "__main__":
    main()