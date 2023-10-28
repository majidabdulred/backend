import base64
import io
from typing import List

from PIL import Image


def base64_to_image(base64_string):
    return Image.open(io.BytesIO(base64.b64decode(base64_string.split(",", 1)[0])))


def image_to_base64(image):
    image_string = io.BytesIO()
    image.save(image_string, format="PNG")
    return base64.b64encode(image_string.getvalue()).decode("utf-8")

def create_grid_base64(images:List[str])->str:
    images = [base64_to_image(img) for img in images]
    return image_to_base64(create_grid(images))
def create_grid(images:List[Image.Image])->Image.Image:
    if len(images) == 1:
        return images[0]
    elif len(images) == 2:
        dst = Image.new("RGB", (images[0].width * 2, images[0].height))
        dst.paste(images[0], (0, 0))
        dst.paste(images[1], (images[0].width, 0))
        return dst
    elif len(images) == 3:
        dst = Image.new("RGB", (images[0].width * 2, images[0].height * 2))
        dst.paste(images[0], (0, 0))
        dst.paste(images[1], (images[0].width, 0))
        dst.paste(images[2], (0, images[0].height))
        dst = dst.resize((images[0].width, images[0].height))
        return dst
    elif len(images) == 4:
        dst = Image.new("RGB", (images[0].width * 2, images[0].height * 2))
        dst.paste(images[0], (0, 0))
        dst.paste(images[1], (images[0].width, 0))
        dst.paste(images[2], (0, images[0].height))
        dst.paste(images[3], (images[0].width, images[0].height))
        dst = dst.resize((images[0].width, images[0].height))
        return dst
