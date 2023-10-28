import json
import secrets
from random import choice

address = ["0xb58457bb1c2a03686735f966f11f52fa432ff124", "0x07fe1d1f995a21d1fce0cbb3257ab6e866350be3",
           "0x47a270e0acd5571e47e677f587eb96c698f1c9ee", "0x35b2ba1b4c74d4f1e22883c2fb2a13ae651a862c",
           "0xd29377846259f667e722ccc311fe168e761c4ee4"]
pixel = [512, 1024, 2048]


def create_transaction_body_upscale():
    return {
        "action_type": "MINE",
        "to_wallet": choice(address),
        "from_wallet": "0x0000000000000000000000000000000000000000",
        # "properties": {
        #     "request_type": "upscale",
        #     "pixel_height": choice(pixel),
        #     "pixel_width": choice(pixel),
        #     "upscale_times": choice([2, 4]),
        #     "model": "R-ESRGAN 4x+"
        # },
        "tokens": choice([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]),
        "session_id": secrets.token_hex(12)
    }


def create_transaction_body_txt2img():
    return {
        "action_type": "MINE",
        "to_wallet": choice(address),
        "from_wallet": "0x0000000000000000000000000000000000000000",
        # "properties": {
        #     "request_type": "txt2img",
        #     "pixel_height": choice(pixel),
        #     "pixel_width": choice(pixel),
        #     "steps": choice([10, 20, 30, 40, 50, 60]),
        #     "batch_size": choice([1, 2, 4]),
        #     "model": "sd1v5"
        # },
        "tokens": choice([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]),
        "session_id": secrets.token_hex(12)
    }


def create_transaction_body_img2img():
    return {
        "action_type": "MINE",
        "to_wallet": choice(address),
        "from_wallet": "0x0000000000000000000000000000000000000000",
        # "properties": {
        #     "request_type": "img2img",
        #     "pixel_height": choice(pixel),
        #     "pixel_width": choice(pixel),
        #     "steps": choice([10, 20, 30, 40, 50, 60])
        # },
        "tokens": choice([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]),
        "session_id": secrets.token_hex(12)
    }


def dm():
    ch = [1, 2, 3]
    if ch == 1:
        print(json.dumps(create_transaction_body_img2img()))
    elif ch == 2:
        print(json.dumps(create_transaction_body_txt2img()))
    else:
        print(json.dumps(create_transaction_body_upscale()))
