import io
import random
from typing import List
import aiohttp

from PIL import Image
import base64

import qrcode

async def shorten_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ulvis.net/api.php?url={url}") as resp:
            return await resp.text()

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


def get_prompt(prompt):
    parameters = {
        "prompt": prompt[0],
        "width": 512,
        "height": 512,
        "steps": 45,
        "sampler_name": "DPM++ 2M Karras",
        "cfg_scale":7,
        "seed": random.randint(0, 10000000),
        "sd_model_name":"revAnimated_v122EOL",
        "clip_skip":2,
        "negative_prompt": prompt[1],
        "override_settings":{
            "sd_model_checkpoint":"revAnimated_v122EOL.safetensors [4199bcdd14]",
            "CLIP_stop_at_last_layers":2,
        },
        "alwayson_scripts":{
            "controlnet":{
                "args":[
                    {"input_image":"",
                     "module":"inpaint_global_harmonious",
                     "model":"control_v1p_sd15_brightness [5f6aa6ed]",
                     "weight":0.5,
                     "resize_mode":"Resize and Fill",
                     "lowvram":False,
                     "guidance_start":0,
                     "guidance_end":1,
                     "pixel_perfect":False,
                     "control_mode":0,
                     },
                    {"input_image": "",
                     "module": "inpaint_global_harmonious",
                     "model": "control_v11f1e_sd15_tile [a371b31b]",
                     "weight": 0.355,
                     "resize_mode": "Resize and Fill",
                     "lowvram": False,
                     "guidance_start": 0.35,
                     "guidance_end": 0.654,
                     "pixel_perfect": False,
                     "control_mode": 0,
                     }
                ]
            }
        }
    }

    return parameters
def make_qr(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=50,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGBA")


if __name__ == '__main__':
    im = make_qr("https://www.asasmetex.co")
    im.show()