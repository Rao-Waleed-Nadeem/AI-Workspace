import re
from dataclasses import dataclass


@dataclass(frozen=True)
class AnswerEvaluation:
    case_id: str
    grounded: bool
    hallucinated: bool
    missing_information: bool
    matched_facts: int
    expected_facts: int


REFUSAL_PHRASES = (
    "i don't know",
    "not available",
    "not provided",
    "not contain",
    "does not contain",
    "cannot determine",
    "can't determine",
    "cannot answer",
    "can't answer",
    "insufficient information",
    "not enough information",
)


def normalize_text(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        text.lower(),
    ).strip()


def fact_is_supported(
    answer: str,
    fact: str,
) -> bool:

    normalized_answer = normalize_text(answer)
    normalized_fact = normalize_text(fact)

    if not normalized_fact:
        return False

    fact_terms = [
        term
        for term in normalized_fact.split()
        if len(term) > 4
    ]

    if not fact_terms:
        return False

    matched_terms = sum(
        term in normalized_answer
        for term in fact_terms
    )

    required_matches = max(
        1,
        (len(fact_terms) + 1) // 2,
    )

    return matched_terms >= required_matches


def evaluate_answer(
    *,
    case_id: str,
    answer: str,
    expected_facts: list[str],
    should_answer: bool,
) -> AnswerEvaluation:

    normalized_answer = normalize_text(answer)

    if not should_answer:

        refused = any(
            phrase in normalized_answer
            for phrase in REFUSAL_PHRASES
        )

        return AnswerEvaluation(
            case_id=case_id,
            grounded=refused,
            hallucinated=not refused,
            missing_information=False,
            matched_facts=0,
            expected_facts=0,
        )

    matched_facts = sum(
        fact_is_supported(
            answer,
            fact,
        )
        for fact in expected_facts
    )

    grounded = (
        matched_facts == len(expected_facts)
        if expected_facts
        else False
    )

    missing_information = (
        matched_facts < len(expected_facts)
    )

    return AnswerEvaluation(
        case_id=case_id,
        grounded=grounded,
        hallucinated=False,
        missing_information=missing_information,
        matched_facts=matched_facts,
        expected_facts=len(expected_facts),
    )


def calculate_answer_metrics(
    evaluations: list[AnswerEvaluation],
) -> dict:

    if not evaluations:
        return {
            "grounding_rate": 0.0,
            "hallucination_rate": 0.0,
            "missing_information_rate": 0.0,
        }

    total = len(evaluations)

    grounded = sum(
        evaluation.grounded
        for evaluation in evaluations
    )

    hallucinated = sum(
        evaluation.hallucinated
        for evaluation in evaluations
    )

    missing = sum(
        evaluation.missing_information
        for evaluation in evaluations
    )

    return {
        "grounding_rate": grounded / total,
        "hallucination_rate": hallucinated / total,
        "missing_information_rate": missing / total,
    }