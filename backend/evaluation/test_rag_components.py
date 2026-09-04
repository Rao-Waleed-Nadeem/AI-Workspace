from app.services.rag_context_service import (
    RetrievedChunk,
    build_rag_context,
)
from app.services.rag_validation_service import (
    validate_retrieval_results,
)
from app.services.rag_exceptions import (
    NoRelevantContextError,
)
from app.prompts.rag import build_rag_prompt


def test_empty_context():

    context = build_rag_context([])

    assert context == ""


def test_context_contains_source_metadata():

    chunks = [
        RetrievedChunk(
            document_id=12,
            page_number=2,
            content="Alternative data is discussed here.",
        )
    ]

    context = build_rag_context(
        chunks,
    )

    assert "Document ID: 12" in context
    assert "Page 2" in context
    assert "Alternative data" in context


def test_prompt_separates_context_and_question():

    prompt = build_rag_prompt(
        context="The system uses risk controls.",
        question="What does the system use?",
    )

    assert "DOCUMENT CONTEXT" in prompt
    assert "USER QUESTION" in prompt
    assert "The system uses risk controls." in prompt
    assert "What does the system use?" in prompt


def test_no_retrieval_results():

    try:

        validate_retrieval_results([])

    except NoRelevantContextError:
        return

    raise AssertionError(
        "Expected NoRelevantContextError"
    )