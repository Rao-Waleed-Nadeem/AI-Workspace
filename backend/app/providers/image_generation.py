from dataclasses import dataclass


@dataclass
class GeneratedImage:
    url: str | None = None
    b64_json: str | None = None
    revised_prompt: str | None = None