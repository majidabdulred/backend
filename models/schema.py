import random
from typing import Literal, Optional,Union
from datetime import datetime
from pydantic import BaseModel, Extra, EmailStr
from uuid import uuid4
from time import time


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
    session_id : str
    file : str


class AssignImageRequest(BaseModel):
    pass


class AssignImageResponseCustom(BaseModel):
    session_id : str
    request_type : str
    prompt : str
    seed : int
    sampler_name: str
    batch_size: int
    steps: int
    cfg_scale: int
    width: int
    height: int
    negative_prompt: str


class AssignImageResponseUpscale(BaseModel):
    session_id : str
    request_type : str
    resize_mode : str
    show_extra_results : bool
    upscaling_resize_w : int
    upscaling_resize_h : int
    upscaling_resize : int
    upscaling_crop : bool
    upscaler_1 : str
    upscaler_2 : str
    extras_upscaler_2_visibility : int
    upscale_first : bool


