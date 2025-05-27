import base64


def encode_image(file_path: str) -> str:
    """Encodes an image to base64."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()
