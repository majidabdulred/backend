import asyncio
import secrets

from fastapi import HTTPException

from db.client import db
from typing import Optional, Union, Dict
from datetime import datetime
from pymongo import ReturnDocument
from bson import ObjectId
from aws import aws_client

collection = db.get_collection("requests")


async def create_custom_request(data):
    """
    Creates a request in the database
    :param data:
    :return:
    """
    data = data.dict()
    data.update({"status": "available",
                 "created_at": datetime.utcnow(),
                 "lastModified": datetime.utcnow()})
    request = await collection.insert_one(data)
    return str(request.inserted_id)


async def get_request(session_id: str, retry=5) -> Optional[Dict]:
    """
    Returns the request with the given session_id
    :param retry:
    :param session_id:
    :return:
    """
    request = await collection.find_one({"_id": ObjectId(session_id)})
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
    else:
        # Recursion limit reached.
        return {"status": request.get("status")}


async def create_upscale_request(data):
    """
    Creates a request in the database
    :param data:
    :return:
    """
    # Getting the image.
    if data.image is None and data.prev_session_id is None:
        raise HTTPException(status_code=400, detail="No image or session_id provided")
    if data.image is not None:
        img = data.image
        name = secrets.token_hex(10)
        await aws_client.upload_base64_to_aws(img, name)
        raw_image = name
    else:
        raw_image = data.prev_session_id

    data = data.dict()
    del data["image"]
    del data["prev_session_id"]

    data.update({"status": "available",
                 "raw_image": raw_image,
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
    request = await collection.find_one_and_update({"status": "available"},
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
        }
    elif request.get("request_type") == "upscale":
        base64_str = await aws_client.download_file(request.get("raw_image") + ".png")
        print(len(base64_str))
        payload = {
            "image": base64_str,
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
            "upscaling_resize" : request.get("upscaling_resize"),
        }
    return payload
