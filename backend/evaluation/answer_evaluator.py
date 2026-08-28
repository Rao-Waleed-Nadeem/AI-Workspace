from dataclasses import dataclass


@dataclass(frozen=True)
class AnswerEvaluation:
    case_id: str
    grounded: bool
    hallucinated: bool
    missing_information: bool


def evaluate_answer(
    *,
    case_id: str,
    answer: str,
    expected_facts: list[str],
    should_answer: bool,
) -> AnswerEvaluation:

    normalized_answer = answer.lower()

    if not should_answer:

        hallucinated = (
            "i don't know" not in normalized_answer
            and "not available" not in normalized_answer
            and "not contain" not in normalized_answer
            and "cannot" not in normalized_answer
        )

        return AnswerEvaluation(
            case_id=case_id,
            grounded=not hallucinated,
            hallucinated=hallucinated,
            missing_information=False,
        )

    matched_facts = 0

    for fact in expected_facts:

        key_terms = [
            word.lower()
            for word in fact.split()
            if len(word) > 4
        ]

        if key_terms and any(
            term in normalized_answer
            for term in key_terms
        ):
            matched_facts += 1

    grounded = matched_facts > 0

    missing_information = (
        matched_facts < len(expected_facts)
    )

    return AnswerEvaluation(
        case_id=case_id,
        grounded=grounded,
        hallucinated=False,
        missing_information=missing_information,
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