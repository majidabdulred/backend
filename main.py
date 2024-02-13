"""
/v2/session/create
/v2/session/ping
/v2/request/submit
/v2/request/assign
/v2/config56
"""

import asyncio
import json
import traceback

from bson import ObjectId
from bson.json_util import dumps as bson_dumps
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException,Body

from app import schema, aws_client
from db import host_session, requests_col,users_col
from db.sqlite import create_table
# from immudbapi.tasks import create_payment
app = FastAPI(
    title='Metex ImageAI Request API',
    version="1.0",
)


@app.on_event("startup")
async def startup_event():
    load_dotenv()
    await create_table()


@app.post("/v3/host/create", response_model=schema.CreateSessionHostResponse)
async def create_session(data: schema.CreateSessionHostRequest):
    _id = await host_session.create_host_session(data)
    asyncio.get_event_loop().create_task(host_session.ping_host(_id))
    return {"host_session_id": _id}


@app.post("/v3/host/ping")
async def ping_session(host_session_id=Header(), version=Header()):
    asyncio.get_event_loop().create_task(host_session.ping_host(host_session_id))
    return {"success": True}


@app.post("/v3/host/assign",)
async def assign_request(host_session_id=Header(), version=Header()):
    if not await host_session.host_exists(host_session_id):
        raise HTTPException(status_code=400, detail="Host Session Id does not exist")
    payload = await requests_col.get_available_request(host_session_id)
    asyncio.get_event_loop().create_task(
        host_session.set_current_processing(host_session_id, payload.get("session_id")))
    return payload


@app.post("/v3/host/submit")
async def submit_request(data: Union[schema.SubmitImageRequesttxt2img,schema.SubmitImageRequestUpscale],
                         host_session_id=Header(), version=Header()):
    if data.request_type == "txt2img":
        locations,grid_location = await aws_client.upload_submitted_images(data)
        await requests_col.request_completed_txt2img(data.session_id,locations,grid_location)
    elif data.request_type == "upscale":
        response = await requests_col.collection.find_one({"_id": ObjectId(data.session_id)})
        upscaling_resize = response.get("parameters").get("upscaling_resize")
        location = await aws_client.upload_base64_to_aws2(data.image,  f"{data.session_id}_UPSCALE{upscaling_resize}X.png",)
        await requests_col.request_completed_single_output(data.session_id,location)
    elif data.request_type == "qr1":
        location = await aws_client.upload_base64_to_aws2(data.image,  f"{data.session_id}_QR1.png",)
        await requests_col.request_completed_single_output(data.session_id,location)
    print("Creating Payment")
    asyncio.get_event_loop().create_task(host_session.set_current_processing_as_none(host_session_id))
    return {"success": True}



@app.post("/v3/user/create-txt2img", response_model=schema.CreateRequestResponse)
async def create_txt2img_request(data: schema.CreateRequestCustom):
    _id = await requests_col.create_txt2img_request(data)
    if data.discord_id:
        await users_col.append_request(data.discord_id, _id)
    return {"session_id": _id}


# @app.post("/v2/request/create-img2img", response_model=schema.CreateRequestResponse)
# async def create_img2img_request(data: schema.CreateRequestImg2Img):
#     _id = await requests_col.create_img2img_request(data)
#     await users_col.append_request(data.discord_id, _id)
#     return {"session_id": _id}
#
# @app.post("/v2/request/create-avatar",response_model=schema.CreateRequestResponse)
# async def create_avatar_request(data:schema.CreateRequestAvatar):
#     _id = await requests_col.create_avatar_request(data)
#     return {"session_id":str(_id)}

@app.post("/v3/user/create-upscale")
async def create_upscale_request(data: schema.CreateUpscaleRequest):
    _id = await requests_col.create_upscale_request(data)
    await users_col.append_request(data.discord_id, _id)
    return {"session_id": _id}

@app.post("/v3/user/create-qr1")
async def create_qr1_request(data: schema.CreateQR1Request):
    _id = await requests_col.create_qr1_request(data)
    await users_col.append_request(data.discord_id, _id)
    return {"session_id": _id}

@app.post("/v3/user/create-variation")
async def create_variation_request(session_id: str):
    _id = await requests_col.create_variation_request(session_id)
    return {"session_id": _id}

# @app.get("/v3/user/status")
# async def status_request(session_id: str):
#     return await requests_col.get_request(session_id)
#
# @app.get("/v3/user/image")
# async def get_image(session_id:str,image_num:int):
#     return {"image": await aws_client.download_file(session_id + f"_{image_num}.png")}

@app.get("/v3/user/data")
async def get_request_data(session_id: str):
    request_data = await requests_col.get_request_data(session_id)
    return json.loads(bson_dumps(request_data))

@app.get("/v2/users")
async def get_user(discord_id: int):
    data = users_col.get_user_by_id(discord_id)
    if data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return data

@app.get("/v2/host")
async def get_host(host_session_id=Header(), version=Header()):
    response =  await host_session.get_host(host_session_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Host not found")
    del response["_id"]
    return response

@app.post("/v2/host/set-wallet-id")
async def set_wallet_id(data :schema.SetWalletIDRequest, host_session_id=Header(), version=Header()):
    await host_session.set_wallet_id(host_session_id, data.wallet_id)
    return {"success": True}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1",port=8000, reload=True)
