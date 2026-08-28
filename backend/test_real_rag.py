from app.database import SessionLocal
from app.services.retrieval_service import RetrievalService


DOCUMENT_ID = 12
USER_ID = 1


questions = [
    "What data sources should the AI trading system use?",
    "What risk management controls are mentioned?",
    "What features should be used by the trading system?",
    "What is the proposed roadmap for developing the trading system?",
]


def main():

    db = SessionLocal()

    retrieval_service = RetrievalService()

    try:

        for question in questions:

            print("=" * 70)
            print(f"QUESTION: {question}")
            print("=" * 70)

            results = retrieval_service.retrieve(
                db=db,
                question=question,
                user_id=USER_ID,
                document_id=DOCUMENT_ID,
                top_k=5,
                min_similarity=0.0,
            )

            if not results:
                print("NO RELEVANT RESULTS")
                continue

            for index, result in enumerate(
                results,
                start=1,
            ):

                print(f"\nResult #{index}")
                print(
                    f"Similarity: "
                    f"{result.similarity:.4f}"
                )
                print(
                    f"Chunk ID: "
                    f"{result.chunk_id}"
                )
                print(
                    f"Page: "
                    f"{result.page_number}"
                )
                print(
                    f"Content:\n"
                    f"{result.content[:500]}"
                )

    finally:

        db.close()


if __name__ == "__main__":
    main()