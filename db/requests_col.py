import asyncio

import secrets
from datetime import datetime
import random
from typing import Optional, Union, Dict
from app import util
from bson.json_util import dumps
import bson.errors
import pymongo
from bson import ObjectId,Int64
from fastapi import HTTPException
from pymongo import ReturnDocument
from datetime import datetime, timedelta
from app import aws_client,schema
from db.client import db

collection = db.get_collection("requests")


async def create_img2img_request(data):
    """
    Creates a request in the database
    :param data:
    :return:
    """
    # Getting the image.

    img = data.image
    name = secrets.token_hex(10)
    await aws_client.upload_base64_to_aws(img, name)
    data = data.dict()
    del data["image"]

    data.update({"status": "available",
                 "raw_image": name,
                 "discord_id": Int64(data.get("discord_id")),
                 "created_at": datetime.utcnow(),
                 "lastModified": datetime.utcnow()})

    request = await collection.insert_one(data)

    return str(request.inserted_id)


async def create_avatar_request(data: schema.CreateRequestAvatar):
    """
    This is same as creating create_img2img_request request except for this is made for the IOS/Android App, and it takes input email instead of discord_id
    and it also takes input the session_id.
    :param data:
    :return:
    """
    try:
        _id = ObjectId(data.session_id)
    except bson.errors.InvalidBSON:
        raise HTTPException(status_code=400, detail="session_id is invalid make sure its 24 character hex string.")

    img = data.image
    # Getting a random name for the image
    name = secrets.token_hex(10)
    await aws_client.upload_base64_to_aws(img, name)
    data = data.dict()

    # Deleting the image to it doesn't get uploaded to database
    del data["image"]

    data.update({"_id": _id,
                 "request_type":"img2img",
                 "status": "available",
                 "raw_image": name,
                 "testing": True, # To be removed later
                 "created_at": datetime.utcnow(),
                 "lastModified": datetime.utcnow()
                 })
    try:
        await collection.insert_one(data)
    except pymongo.errors.DuplicateKeyError:
        raise HTTPException(status_code=404,detail="Duplicate Key Error")
    return _id

async def create_txt2img_request(data):
    """
    Creates a request in the database
    :param data:
    :return:
    """
    db_data= {"status": "available",
              "request_type": data.request_type,
              "parameters": data.parameters.dict(),
                 "discord_id": Int64(data.discord_id),
                 "created_at": datetime.utcnow(),
                 "lastModified": datetime.utcnow()}
    request = await collection.insert_one(db_data)
    return str(request.inserted_id)

async def create_variation_request(session_id):
    try:
        request = await collection.find_one({"_id": ObjectId(session_id)})
    except bson.errors.InvalidBSON:
        raise HTTPException(status_code=404, detail="Session_id Invalid")

    if request is None:
        raise HTTPException(status_code=404, detail="Session_id not found")
    request["parameters"]["seed"] = random.randint(0, 1000000)
    data = schema.CreateRequestCustom(**request)
    return await create_txt2img_request(data)

async def create_upscale_request(data:schema.CreateUpscaleRequest):
    image = await aws_client.download_file(f"{data.session_id}_{data.image_num}.png")
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    upscale_details = schema.ParametersUPSCALE()
    response = await collection.insert_one({"status": "available",
                                 "request_type": "upscale",
                                 "parameters": upscale_details.dict(exclude={"image"}),
                                 "discord_id": Int64(data.discord_id),
                                 "created_at": datetime.utcnow(),
                                 "lastModified": datetime.utcnow(),
                                 "bucket": "resources-image-ai",
                                 "img_path": f"{data.session_id}_{data.image_num}.png"
                                 })
    return str(response.inserted_id)
async def get_request_data(session_id : str):
    """
    Returns the request with the given session_id
    """
    try:
        request = await collection.find_one({"_id": ObjectId(session_id)})
    except bson.errors.InvalidBSON:
        raise HTTPException(status_code=404, detail="Session_id Invalid")

    if request is None:
        raise HTTPException(status_code=404, detail="Session_id not found")
    return request

async def get_request(session_id: str) -> Optional[Dict]:
    try:
        request = await collection.find_one({"_id": ObjectId(session_id)})
    except bson.errors.InvalidBSON:
        raise HTTPException(status_code=404, detail="Session_id Invalid")

    if request is None:
        raise HTTPException(status_code=404, detail="Session_id not found")
    if request.get("status") == "complete":
        if request.get("request_type") == "txt2img":
            return await _get_request_txt2img(request,session_id)
        elif request.get("request_type") == "upscale":
            return await _get_request_upscale(request,session_id)
    else:
        return {"status": request.get("status")}

async def _get_request_txt2img(request,session_id):
    tasks = []
    for i in range(request.get("parameters").get("batch_size")):
        tasks.append(aws_client.download_file(session_id + f"_{i}.png"))
    images = await asyncio.gather(*tasks)
    if images is None:
        print(f"Images not found {session_id}")
        raise HTTPException(status_code=404, detail="Images not found")
    images = [i for i in images if i is not None]
    grid_image = await aws_client.download_file(session_id + f"_grid.png")
    if grid_image is None:
        grid_image = util.create_grid_base64(images)
    return {"status": "complete", "images": images, "grid_image": grid_image}
async def _get_request_upscale(request,session_id):
    image = await aws_client.download_file(f"{session_id}_UPSCALE{request.get('parameters').get('upscaling_resize')}X.png")
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"status": "complete", "image": image}

async def request_completed(session_id: str):
    """
    Updates the status of the request to available.
    {"status":"complete","processed_at":datetime.utcnow()}
    """
    status = await collection.update_one({'_id': ObjectId(session_id)},
                                         {'$set': {"status": 'complete',
                                                   "processed_at": datetime.utcnow()},
                                          "$currentDate": {"lastModified": True}},
                                         )
    if not status.matched_count:
        raise HTTPException(status_code=404, detail="Session_id not found")


async def delete_request(session_id: str):
    """
    Deletes the request with the given session_id
    :param session_id:
    :return:
    """
    status = await collection.delete_one({'_id': ObjectId(session_id)})
    if not status.deleted_count:
        raise HTTPException(status_code=404, detail="Session_id not found")


async def get_available_request(host_session_id) -> Union[None, Dict]:
    """
    Returns the first request that is available for processing.
    Changes its status to processing adds the processing start time and returns the document
    :return:
    """
    request = await collection.find_one_and_update({"status": "available","request_type":{"$in":["txt2img","upscale"]}},
                                                   {'$set': {"status": 'processing',
                                                             "assigned_to": {
                                                                 "$ref": "hosts",
                                                                 "$db": "backend",
                                                                 "$id": ObjectId(host_session_id)
                                                             },
                                                             "processing_start": datetime.utcnow()},
                                                    "$currentDate": {"lastModified": True}
                                                    },
                                                   return_document=ReturnDocument.AFTER)
    if request is None:
        raise HTTPException(status_code=404, detail="No Requests available")
    payload = await __create_payload(request)
    return payload


async def __create_payload(request):
    if request.get("request_type") == "txt2img":
        payload = {
            "request_type": str(request.get("request_type")),
            "session_id": str(request["_id"]),
            "parameters": request.get("parameters"),
        }
    elif request.get("request_type") == "upscale":
        image = await aws_client.download_file(request.get("img_path"))
        if image is None:
            raise HTTPException(status_code=404, detail="Image not found")
        parameters = request.get("parameters")
        parameters.update({"image":image})
        if image is None:
            raise HTTPException(status_code=404, detail="Image not found")
        payload = {
            "request_type": str(request.get("request_type")),
            "session_id": str(request["_id"]),
            "parameters": request.get("parameters"),
        }
    else:
        raise HTTPException(status_code=404, detail="Request Type not found")
    return payload
