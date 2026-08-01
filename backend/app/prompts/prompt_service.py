from app.prompts.templates import EXPLAIN_PROMPT
from app.prompts.structured_templates import (
    STRUCTURED_ANALYSIS_PROMPT,
)

def build_explain_prompt(content: str) -> str:
    return EXPLAIN_PROMPT.format(
        content=content,
    )


def build_structured_analysis_prompt(content: str) -> str:
    return STRUCTURED_ANALYSIS_PROMPT.format(
        content=content,
    )
