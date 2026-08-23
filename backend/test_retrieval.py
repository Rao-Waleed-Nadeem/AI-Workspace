from app.database import SessionLocal
from app.services.retrieval_service import RetrievalService


db = SessionLocal()

try:
    service = RetrievalService()

    results = service.retrieve(
        db=db,
        question=(
            "How can we make sure that historical testing does not accidentally give the model access to information that would not have existed when the trade was made?"
        ),
        user_id=1,
        top_k=5,
    )

    print()
    print("SEMANTIC SEARCH RESULTS")
    print("=" * 60)

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(f"Result #{index}")
        print(f"Similarity: {result.similarity:.4f}")
        print(f"Document ID: {result.document_id}")
        print(f"User ID: {result.user_id}")
        print(f"Page: {result.page_number}")
        print(f"Content: {result.content[:300]}")
        print("-" * 60)

finally:
    db.close()