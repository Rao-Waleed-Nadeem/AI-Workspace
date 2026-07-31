from app.prompts.templates import EXPLAIN_PROMPT


def build_explain_prompt(content: str) -> str:
    return EXPLAIN_PROMPT.format(
        content=content,
    )
