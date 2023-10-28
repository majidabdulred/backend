from typing import Optional, Dict, List, Union
import random
from typing import Optional

from pydantic import BaseModel,validator


class CreateSessionHostRequest(BaseModel):
    gpu_name: str
    gpu_uuid: str
    gpu_total_memory: int

class SetWalletIDRequest(BaseModel):
    wallet_id: str
class CreateSessionHostResponse(BaseModel):
    host_session_id: str


class PingOnlineRequest(BaseModel):
    pass


class PingOnlineResponse(BaseModel):
    pass


class SubmitImageRequesttxt2img(BaseModel):
    request_type: str
    session_id: str
    grid_image: str
    images: List[str]

class SubmitImageRequestUpscale(BaseModel):
    request_type: str
    session_id: str
    image: str

class AssignImageResponsetxt2img(BaseModel):
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

class CreateUpscaleRequest(BaseModel):
    upscale_times : int = 2
    discord_id: int
    session_id: str
    image_num: int
class ParametersUPSCALE(BaseModel):
    image: str = ""
    resize_mode: int = 0
    show_extras_results: bool = True
    codeformer_visibility: int = 1
    codeformer_weight: int = 0
    upscaling_resize: int = 2
    upscaler_1: str = "R-ESRGAN 4x+"
    extras_upscaler_2_visibility: int = 0
    upscale_first: bool = True

class ParametersTXT2IMG(BaseModel):
    alwayson_scripts: Dict = {}
    batch_size: int = 4
    cfg_scale: float = 7.0
    comments: Optional[str] = None
    denoising_strength: int = 0
    disable_extra_networks: bool = False
    do_not_save_grid: bool = False
    do_not_save_samples: bool = False
    enable_hr: bool = False
    eta: Optional[float] = None
    firstphase_height: int = 0
    firstphase_width: int = 0
    height: int = 512
    hr_checkpoint_name: Optional[str] = None
    hr_negative_prompt: str = ''
    hr_prompt: str = ''
    hr_resize_x: int = 0
    hr_resize_y: int = 0
    hr_sampler_name: Optional[str] = None
    hr_scale: float = 2.0
    hr_second_pass_steps: int = 0
    hr_upscaler: Optional[str] = None
    n_iter: int = 1
    negative_prompt: str = ''
    override_settings: Dict = {'sd_model_checkpoint': 'dreamshaper_8.safetensors [879db523c3]'}
    override_settings_restore_afterwards: bool = True
    prompt: str = 'A Man'
    refiner_checkpoint: Optional[str] = None
    refiner_switch_at: Optional[Union[str, int, float]] = None
    restore_faces: bool = True
    s_churn: Optional[float] = None
    s_min_uncond: Optional[float] = None
    s_noise: Optional[float] = None
    s_tmax: Optional[float] = None
    s_tmin: Optional[float] = None
    sampler_index: str = 'Euler'
    sampler_name: Optional[str] = None
    save_images: bool = False
    script_args: List = []
    script_name: Optional[str] = None
    seed: int = 1096141474
    seed_resize_from_h: int = -1
    seed_resize_from_w: int = -1
    send_images: bool = True
    steps: int = 25
    styles: Optional[Union[str, List[str]]] = None
    subseed: int = -1
    subseed_strength: int = 0
    tiling: bool = False
    width: int = 512


class CreateRequestCustom(BaseModel):
    request_type = "txt2img"
    discord_id: int
    parameters: ParametersTXT2IMG
    class Config:
        validate_assignment = True



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

    @validator('session_id')
    def session_id_must_be_valid(cls, v):
        if len(v) != 24:
            raise ValueError('session_id must be 12 digits long')
        try:
            int(v, 16)
        except ValueError:
            raise ValueError('session_id must be a valid hex string')
        return v


class StatusRequestRequest(BaseModel):
    session_id: str


class StatusRequestResponse(BaseModel):
    status: str
    images: Optional[List[str]]
    grid_image: Optional[str]


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
