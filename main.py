"""
/v2/session/create
/v2/session/ping
/v2/request/submit
/v2/request/assign
/v2/config56
"""

import asyncio
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException

from app import schema, aws_client
from db import host_session, requests_col,users_col
from db.sqlite import create_table

app = FastAPI(
    title='Metex ImageAI Request API',
    version="1.0",
    docs_url='/',
)


@app.on_event("startup")
async def startup_event():
    load_dotenv()
    await create_table()


@app.post("/v2/session/create", response_model=schema.CreateSessionHostResponse)
async def create_session(data: schema.CreateSessionHostRequest):
    _id = await host_session.create_host_session(data)
    asyncio.get_event_loop().create_task(host_session.ping_host(_id))
    return {"host_session_id": _id}


@app.post("/v2/session/ping")
async def ping_session(host_session_id=Header(), version=Header()):
    asyncio.get_event_loop().create_task(host_session.ping_host(host_session_id))
    return {"success": True}


@app.post("/v2/request/assign",)
async def assign_request(host_session_id=Header(), version=Header()):
    if not await host_session.host_exists(host_session_id):
        raise HTTPException(status_code=400, detail="Host Session Id does not exist")
    payload = await requests_col.get_available_request(host_session_id)
    asyncio.get_event_loop().create_task(
        host_session.set_current_processing(host_session_id, payload.get("session_id")))
    return payload


@app.post("/v2/request/submit")
async def submit_request(data: schema.SubmitImageRequest, host_session_id=Header(), version=Header()):
    try:
        await aws_client.upload_base64_to_aws(data.file, data.session_id)
        await requests_col.request_completed(data.session_id)
        asyncio.get_event_loop().create_task(host_session.set_current_processing_as_none(host_session_id))
        return {"success": True}
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/v2/request/create-custom", response_model=schema.CreateRequestResponse)
async def create_custom_request(data: schema.CreateRequestCustom):
    _id = await requests_col.create_custom_request(data)
    await users_col.append_request(data.discord_id, _id)
    return {"session_id": _id}


@app.post("/v2/request/create-upscale", response_model=schema.CreateRequestResponse)
async def create_upscale_request(data: schema.CreateRequestUpscale):
    _id = await requests_col.create_upscale_request(data)
    await users_col.append_request(data.discord_id, _id)
    return {"session_id": _id}

@app.post("/v2/request/create-img2img", response_model=schema.CreateRequestResponse)
async def create_img2img_request(data: schema.CreateRequestImg2Img):
    _id = await requests_col.create_img2img_request(data)
    await users_col.append_request(data.discord_id, _id)
    return {"session_id": _id}

@app.post("/v2/request/create-avatar",response_model=schema.CreateRequestResponse)
async def create_avatar_request(data:schema.CreateRequestAvatar):
    _id = await requests_col.create_avatar_request(data)
    return {"session_id":str(_id)}

@app.get("/v2/request/status", response_model=schema.StatusRequestResponse)
async def status_request(session_id: str):
    return await requests_col.get_request(session_id)

@app.get("/v2/users")
async def get_user(discord_id: int):
    data = users_col.get_user_by_id(discord_id)
    if data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return data

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
