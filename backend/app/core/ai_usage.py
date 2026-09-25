import logging

from app.core.token_budget import (
    estimate_message_tokens,
)


logger = logging.getLogger(__name__)


def log_estimated_input_usage(
    messages: list[dict],
    *,
    operation: str,
) -> None:

    tokens = estimate_message_tokens(
        messages
    )

    logger.info(
        "AI usage operation=%s "
        "estimated_input_tokens=%s",
        operation,
        tokens,
    )


def log_provider_usage(
    usage,
    *,
    operation: str,
) -> None:

    if usage is None:
        return

    logger.info(
        "AI usage operation=%s "
        "prompt_tokens=%s "
        "completion_tokens=%s "
        "total_tokens=%s",
        operation,
        getattr(
            usage,
            "prompt_tokens",
            None,
        ),
        getattr(
            usage,
            "completion_tokens",
            None,
        ),
        getattr(
            usage,
            "total_tokens",
            None,
        ),
    )