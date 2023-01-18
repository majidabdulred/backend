from typing import Optional
import random
from typing import Optional

from pydantic import BaseModel


class CreateSessionHostRequest(BaseModel):
    gpu_name: str
    gpu_uuid: str
    gpu_total_memory: int


class CreateSessionHostResponse(BaseModel):
    host_session_id: str


class PingOnlineRequest(BaseModel):
    pass


class PingOnlineResponse(BaseModel):
    pass


class SubmitImageRequest(BaseModel):
    session_id: str
    file: str


class AssignImageResponseCustom(BaseModel):
    session_id: str
    request_type: str
    prompt: str
    seed: int
    sampler_name: str
    batch_size: int
    steps: int
    cfg_scale: int
    width: int
    height: int
    negative_prompt: str


class CreateRequestCustom(BaseModel):
    request_type = "custom"
    discord_id: int
    prompt: str
    seed: Optional[int] = int(random.random() * 1000000)
    sampler_name: Optional[str] = "Euler a"
    batch_size: Optional[int] = 1
    steps: Optional[int] = 25
    cfg_scale: Optional[int] = 7
    width: Optional[int] = 512
    height: Optional[int] = 512
    tiling: Optional[bool] = True
    negative_prompt: Optional[str] = ""
    restore_faces: Optional[bool] = True


class CreateRequestUpscale(BaseModel):
    request_type = "upscale"
    discord_id: int
    resize_mode: Optional[int] = 1
    show_extras_results = False
    upscaling_resize_w: Optional[int] = 2048
    upscaling_resize_h: Optional[int] = 2048
    upscaling_resize: Optional[int] = 4
    upscaling_crop: Optional[bool] = False
    upscaler_1: Optional[str] = "R-ESRGAN 4x+"
    upscaler_2: Optional[str] = "R-ESRGAN 4x+"
    extras_upscaler_2_visibility: Optional[int] = 1
    upscale_first: Optional[bool] = True
    prev_session_id: Optional[str]

class CreateRequestImg2Img(BaseModel):
    request_type = "img2img"
    discord_id: int
    prompt: str
    image: str

class CreateRequestResponse(BaseModel):
    session_id: str

class CreateRequestAvatar(BaseModel):
    session_id: str
    prompt: str
    image : str
    email : str
class StatusRequestRequest(BaseModel):
    session_id: str


class StatusRequestResponse(BaseModel):
    status: str
    image: Optional[str]


class AssignImageResponseUpscale(BaseModel):
    image: str
    session_id: str
    request_type: str
    resize_mode: int
    show_extras_results: bool
    upscaling_resize_w: int
    upscaling_resize_h: int
    upscaling_resize: int
    upscaling_crop: bool
    upscaler_1: str
    upscaler_2: str
    extras_upscaler_2_visibility: int
    upscale_first: bool
