from fastapi import HTTPException

from db.client import db
from typing import Optional, Union, Dict
from datetime import datetime
from pymongo import ReturnDocument
from bson import ObjectId

collection = db.get_collection("requests")


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
    payload = __create_payload(request)
    return payload


def __create_payload(request):
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
        payload = {
            "session_id": str(request["_id"]),
            "request_type": str(request.get("request_type")),
            "resize_mode": request.get("resize_mode"),
            "show_extra_results": request.get("show_extra_results"),
            "upscaling_resize_w": request.get("upscaling_resize_w"),
            "upscaling_resize_h": request.get("upscaling_resize_h"),
            "upscaling_crop": request.get("upscaling_crop"),
            "upscaler_1": request.get("upscaler_1"),
            "upscaler_2": request.get("upscaler_2"),
            "extras_upscaler_2_visibility": request.get("extras_upscaler_2_visibility"),
            "upscale_first": request.get("upscale_first"),
        }
    return payload
