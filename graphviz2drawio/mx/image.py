from base64 import b64encode
from pathlib import Path

import puremagic


def image_data_for_path(path: str) -> str:
    image_data = Path(path).read_bytes()
    mime_type = puremagic.from_stream(image_data, mime=True, filename=path)
    encoded_string = b64encode(image_data).decode("utf-8")
    return f"data:{mime_type},{encoded_string}"
