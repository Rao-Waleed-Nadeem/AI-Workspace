IMAGE_GENERATION_INSTRUCTIONS = """
Create a visually detailed image based on the user's request.

Preserve the user's intended subject, setting, style,
and important visual details.

Do not add unrelated subjects or change the user's intent.
""".strip()


def build_image_prompt(
    user_prompt: str,
) -> str:

    return (
        f"{IMAGE_GENERATION_INSTRUCTIONS}\n\n"
        f"User request:\n"
        f"{user_prompt.strip()}"
    )