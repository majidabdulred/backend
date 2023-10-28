from typing import Dict, Any


def calculate_tokens(data):
    return 1000
    # if data.get("request_type") == "txt2img":
    #     return _calculate_txt2img(data)
    #
    # elif data.get("request_type") == "img2img":
    #     return _calculate_img2img(data)
    #
    # elif data.get("request_type") == "upscale":
    #     return _calculate_upscale(data)
    #
    # else:
    #     raise ValueError("Invalid request type")
    #


# def get_properties(data: dict) -> dict[str, Any | None] | Any:
#     if data.get("request_type") == "custom":
#         return {"request_type": "custom",
#                 "pixel_height": data.get("height"),
#                 "pixel_width": data.get("width"),
#                 "steps": data.get("steps"),
#                 "batch_size": data.get("batch_size"),
#                 "model": "SD1v4"}
#
#     elif data.get("request_type") == "img2img":
#         return {"request_type": "img2img",
#                 "pixel_height": 512,
#                 "pixel_width": 512,
#                 "steps": 25,
#                 }
#
#     elif data.get("request_type") == "upscale":
#         # todo: need to UPDATE THE VALUES
#         return {"pixel_height": 1024,
#                 "pixel_width": 1024,
#                 "upscale_times": data.get("upscaling_resize"),
#                 "model": data.get("upscaler_1")}
#     else:
#         raise ValueError("Invalid request type")
