from evaluation.rag_evaluator import (
    calculate_retrieval_metrics,
)


def print_evaluation_report(
    retrieval_metrics: dict,
    answer_metrics: dict,
) -> None:

    print()
    print("=" * 60)
    print("RAG EVALUATION REPORT")
    print("=" * 60)

    print("\nRetrieval")
    print("-" * 60)

    for name, value in retrieval_metrics.items():

        print(
            f"{name}: {value:.2%}"
        )

    print("\nAnswer Quality")
    print("-" * 60)

    for name, value in answer_metrics.items():

        print(
            f"{name}: {value:.2%}"
        )

    print()