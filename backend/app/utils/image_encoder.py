import base64

from fastapi import UploadFile


async def encode_image(image: UploadFile) -> str:

    contents = await image.read()

    encoded = base64.b64encode(contents).decode("utf-8")

    await image.seek(0)

    return f"data:{image.content_type};base64,{encoded}"