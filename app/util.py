import base64
import io

from PIL import Image


def base64_to_image(base64_string):
    return Image.open(io.BytesIO(base64.b64decode(base64_string.split(",", 1)[0])))


def image_to_base64(image):
    image_string = io.BytesIO()
    image.save(image_string, format="PNG")
    return base64.b64encode(image_string.getvalue()).decode("utf-8")
