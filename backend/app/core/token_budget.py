from __future__ import annotations

from app.core.config import settings


def estimate_tokens(text: str) -> int:
    """
    Cheap provider-neutral token estimate.

    Exact tokenization depends on the model/provider,
    so this is intentionally an estimate.
    """
    if not text:
        return 0

    chars_per_token = max(
        settings.TOKEN_ESTIMATE_CHARS_PER_TOKEN,
        1.0,
    )

    return max(
        1,
        int(
            (len(text) + chars_per_token - 1)
            / chars_per_token
        ),
    )


def estimate_message_tokens(
    messages: list[dict],
) -> int:
    total = 0

    for message in messages:
        total += estimate_tokens(
            str(message.get("content", ""))
        )

        # Small overhead for role/message framing.
        total += 4

    return total


def trim_messages_to_budget(
    messages: list[dict],
    *,
    max_tokens: int | None = None,
) -> list[dict]:
    """
    Keep the newest messages that fit the input budget.

    A leading system message is preserved when possible.
    """
    budget = (
        max_tokens
        or settings.AI_MAX_INPUT_TOKENS
    )

    if budget <= 0:
        return []

    selected: list[dict] = []
    used = 0

    system_messages = [
        message
        for message in messages
        if message.get("role") == "system"
    ]

    conversation = [
        message
        for message in messages
        if message.get("role") != "system"
    ]

    # Preserve the first system message.
    for message in system_messages[:1]:

        cost = estimate_message_tokens(
            [message]
        )

        if cost <= budget:
            selected.append(message)
            used += cost

    # Newest conversation messages have priority.
    for message in reversed(conversation):

        cost = estimate_message_tokens(
            [message]
        )

        if used + cost > budget:
            break

        selected.append(message)
        used += cost

    system_count = len(
        [
            message
            for message in selected
            if message.get("role") == "system"
        ]
    )

    recent = list(
        reversed(
            selected[system_count:]
        )
    )

    return (
        selected[:system_count]
        + recent
    )