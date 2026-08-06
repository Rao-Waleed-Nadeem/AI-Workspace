import shutil
import tempfile
from pathlib import Path
from fastapi import UploadFile


def save_temp_image(image: UploadFile) -> Path:

    suffix = Path(image.filename).suffix

    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    )

    with temp:

        shutil.copyfileobj(
            image.file,
            temp,
        )

    return Path(temp.name)

def delete_temp_image(path: Path):

    if path.exists():

        path.unlink()