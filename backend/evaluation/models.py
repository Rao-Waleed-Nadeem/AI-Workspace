from dataclasses import dataclass


@dataclass(frozen=True)
class RAGEvaluationCase:
    id: str
    question: str
    document_id: int
    expected_pages: list[int]
    expected_facts: list[str]
    should_answer: bool