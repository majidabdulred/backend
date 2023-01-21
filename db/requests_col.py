import json
import secrets
from datetime import datetime
import random
from typing import Optional, Union, Dict
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

async def create_custom_request(data):
    """
    Creates a request in the database
    :param data:
    :return:
    """
    data = data.dict()
    data.update({"status": "available",
                 "discord_id": Int64(data.get("discord_id")),
                 "created_at": datetime.utcnow(),
                 "lastModified": datetime.utcnow()})
    request = await collection.insert_one(data)
    return str(request.inserted_id)

async def create_variation_request(session_id):
    """

    :param data:
    :return:
    """

    try:
        request = await collection.find_one({"_id": ObjectId(session_id)})
    except bson.errors.InvalidBSON:
        raise HTTPException(status_code=404, detail="Session_id Invalid")

    if request is None:
        raise HTTPException(status_code=404, detail="Session_id not found")
    request.update({"seed":int(random.random() * 1000000)})
    data = schema.CreateRequestCustom(**request)
    return await create_custom_request(data)
async def get_request_data(session_id : str):
    """
    Returns the request with the given session_id
    :param session_id:
    :return:
    """
    try:
        request = await collection.find_one({"_id": ObjectId(session_id)})
    except bson.errors.InvalidBSON:
        raise HTTPException(status_code=404, detail="Session_id Invalid")

    if request is None:
        raise HTTPException(status_code=404, detail="Session_id not found")
    return json.loads(dumps(request))
async def get_request(session_id: str, retry=5) -> Optional[Dict]:
    """
    Returns the request with the given session_id
    :param retry:
    :param session_id:
    :return:
    """
    try:
        request = await collection.find_one({"_id": ObjectId(session_id)})
    except bson.errors.InvalidBSON:
        raise HTTPException(status_code=404, detail="Session_id Invalid")

    if request is None:
        raise HTTPException(status_code=404, detail="Session_id not found")
    if request.get("status") == "complete":
        base64_str = await aws_client.download_file(session_id + ".png")
        if base64_str is None:
            raise HTTPException(status_code=404, detail="Image not found")
        return {"status": "complete", "image": base64_str}
    # elif retry > 0:
    #     # Using recursion to retry the request for few more times until the image is ready.
    #     await asyncio.sleep(10)
    #     return await get_request(session_id, retry-1)

    # To be removed later
    elif request.get("status") == "available" and request.get("testing") and\
            request.get("created_at") + timedelta(seconds=30) < datetime.utcnow():
        return {"status": "complete", "image": open("app/testimage.txt", "r").read()}
    else:
        # Recursion limit reached.
        return {"status": request.get("status")}


async def create_upscale_request(data:schema.CreateRequestUpscale):
    """
    Creates a request in the database
    :param data:
    :return:
    """
    # Getting the image.
    previous_data = await collection.find_one({"_id": ObjectId(data.prev_session_id)})
    if previous_data is None:
        raise HTTPException(status_code=404, detail="prev_session_id not found")

    # Deleting the _id because this field is in ObjectId form can cannot be sent as json later on while assigning this
    # request.
    del previous_data["_id"]
    previous_data.update({"seed":previous_data.get("seed")+data.image_num})
    data = data.dict()

    data.update({"status": "available",
                 "properties": previous_data,
                 "discord_id": Int64(data.get("discord_id")),
                 "created_at": datetime.utcnow(),
                 "lastModified": datetime.utcnow()})

    request = await collection.insert_one(data)

    return str(request.inserted_id)


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
    request = await collection.find_one_and_update({"status": "available","request_type":{"$in":["img2img","custom","upscale"]}},
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
    if request.get("request_type") == "custom":
        payload = {
            "request_type": str(request.get("request_type")),
            "session_id": str(request["_id"]),
            "prompt": request.get("prompt"),
            "seed": request.get("seed"),
            "sampler_name": request.get("sampler_name"),
            "batch_size": request.get("batch_size"),
            "steps": request.get("steps"),
            "cfg_scale": request.get("cfg_scale"),
            "width": request.get("width"),
            "height": request.get("height"),
            "negative_prompt": request.get("negative_prompt"),
            "restore_faces": request.get("restore_faces"),
            "tiling": request.get("tiling"),
        }
    elif request.get("request_type") == "upscale":
        # base64_str = await aws_client.download_file(request.get("raw_image") + ".png") # Previously used to send the image to the host.
        # Get the previous request ID.
        properties = {key:value for key,value in request.get("properties").items() if type(value) in (int,str,bool)}
        payload = {
            "properties" : properties,
            "session_id": str(request["_id"]),
            "request_type": str(request.get("request_type")),
            "resize_mode": request.get("resize_mode"),
            "show_extras_results": request.get("show_extras_results"),
            "upscaling_resize_w": request.get("upscaling_resize_w"),
            "upscaling_resize_h": request.get("upscaling_resize_h"),
            "upscaling_crop": request.get("upscaling_crop"),
            "upscaler_1": request.get("upscaler_1"),
            "upscaler_2": request.get("upscaler_2"),
            "extras_upscaler_2_visibility": request.get("extras_upscaler_2_visibility"),
            "upscale_first": request.get("upscale_first"),
            "upscaling_resize": request.get("upscaling_resize"),
        }
    elif request.get("request_type") == "img2img":
        print("Hit 191")
        base64 = await aws_client.download_file(request.get("raw_image") + ".png")
        payload = {
            "image": base64,
            "session_id": str(request["_id"]),
            "request_type": "img2img",
            "prompt": request.get("prompt"),
        }
    return payload
