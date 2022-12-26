
"""
/v2/session/create
/v2/session/ping
/v2/request/submit
/v2/request/assign
/v2/config56
"""

import asyncio
from models import schema
from db import host_session,requests_col
from fastapi import FastAPI, UploadFile, Form, Header,HTTPException
from dotenv import load_dotenv
from typing import Union
from aws import aws_client
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


@app.post("/v2/session/create",response_model=schema.CreateSessionHostResponse)
async def create_session(data:schema.CreateSessionHostRequest):
    _id = await host_session.create_host_session(data)
    asyncio.get_event_loop().create_task(host_session.ping_host(_id))
    return {"host_session_id": _id}


@app.post("/v2/session/ping")
async def ping_session(host_session_id=Header(),version=Header()):
    asyncio.get_event_loop().create_task(host_session.ping_host(host_session_id))
    return {"success": True}


@app.post("/v2/request/assign",response_model=Union[schema.AssignImageResponseCustom,schema.AssignImageResponseUpscale])
async def assign_request(host_session_id=Header(),version=Header()):
    if not await host_session.host_exits(host_session_id):
        raise HTTPException(status_code=400, detail="Host Session Id does not exist")
    payload = await requests_col.get_available_request(host_session_id)
    asyncio.get_event_loop().create_task(host_session.set_current_processing(host_session_id,payload.get("session_id")))
    return payload


@app.post("/v2/request/submit")
async def submit_request(data:schema.SubmitImageRequest,host_session_id=Header(),version=Header()):
    try:
        await aws_client.upload_base64(data.file,data.session_id)
        await requests_col.request_completed(data.session_id)
        asyncio.get_event_loop().create_task(host_session.set_current_processing_as_none(host_session_id))
        return {"success":True}
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail="Internal Server Error")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)