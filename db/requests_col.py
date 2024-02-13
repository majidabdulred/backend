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
                 "created_at": datetime.utcnow(),
                 "lastModified": datetime.utcnow()}

    if data.discord_id is not  None:
        db_data.update({"discord_id": Int64(data.discord_id)})

    if data.user_id is not None:
        db_data.update({"user_id": ObjectId(data.user_id)})

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

prompts = {"library":("staring up into the infinite maelstrom library, endless books, flying books, spiral staircases, nebula, ominous, cinematic atmosphere, negative dark mode, mc escher, art by sensei jaye, matrix atmosphere, digital code swirling, matte painting, laboratory , sharp , raytracing , light tracing , 8k , ultra preset",
            "(worst quality, low quality:1.4), (logo, text, watermask, username), NG_DeepNegative_V1_75T, (bad-hands-5, bad-artist:1.2), human, girl , boy , man , female ,male,(bad-image-v2-39000, bad_prompt_version2, bad-hands-5, EasyNegative, NG_DeepNegative_V1_4T, bad-artist-anime:0.7),(worst quality, low quality:1.3), (depth of field, blurry:1.2), (greyscale, monochrome:1.1), nose, cropped, lowres, text, jpeg artifacts, signature, watermark, username, blurry, artist name, trademark, watermark, title,(tan, muscular, loli, petite, child, infant, toddlers, chibi, sd character:1.1), multiple view, Reference sheet, long neck, unclear lines"),
           "mech-robot":("mecha, robot , war, gundam,1robot, high quality, high resolution. detailed body, detailed, legs , detailed face , detailed metal,8k, ultra realistic, icy background ,explosion in the background, fire  long sword  in right hand, shield in left hand, darker blacks,finely detailed,best quality, extra sharp , 16x anistrophic filtering",
            "noise, haze, low quality, deformed leg, deformed body, extra hands ,extra legs , blurry foot,text, numbers, extra faces in corners, unnecessary objects,deformed fingers, extra fingers"),
          "mountain": ("clouds with beautiful land scenery, high quality, finely detailed , intricate details,8k , sharp , mountains , snowfall, high resolution, 8k resolution, darker blacks",
            "blur , low quality , low resolution, light colors, sunset, yellow lights rays, haze, sun rays"),
           "hogwarts-castle":("Hogwarts castle , dark environment, intricate details, hdr, 8k, detailed  1guy flying on the broom stick magic trail behind, angel of view ocean level,more visible castle, bridge connected to the castle",
                              "(EasyNegative:0.8), (worst quality, low quality:1.2),tight, skin tight, impossible clothes, (ribs:1.2)"),
            "angel-death":("((best quality)),delicate equal wings, otherworldly charm, mystical sky, (Luis Royo:1.2),  ((masterpiece)), (Yoshitaka Amano:1.1), moonlit night, soft colors, (detailed cloudscape:1.3), (high-resolution:1.2),(detailed), alluring succubus, ethereal beauty, perched on a cloud, , enchanting gaze, captivating pose, finely beautiful detailed face, golden ratio face, detailed nose , detailed eyes , detailed lips, finely detailed legs with accurate proportion ,(fantasy illustration:1.3), full body pose, body covering dress, raytracing , light rays",
                           "3d, cartoon, anime, sketches, (worst quality, bad quality, child, cropped:1.4) ((monochrome)), ((grayscale)), (bad-hands-5:1.0), (badhandv4:1.0), (easynegative:0.8), (bad-artist-anime:0.8), (bad-artist:0.8), (bad_prompt:0.8), (bad-picture-chill-75v:0.8), (bad_prompt_version2:0.8), (bad_quality:0.8), open mouth, crouched,"),
           "blood-moon":("(masterpiece, best quality:1.4), cinematic light, colorful, high contrast, mountain, grass, tree, night, (horror (theme):1.2), (mon(masterpiece, best quality:1.4), (captivating digital art), cinematic lighting, colorful, high contrast, eerie mountain landscape, lush grass, twisted trees, night scene, (horror theme:1.2), (menacing monster:1.2) lurking in shadows, dark atmosphere, blood rain pouring down, blood-red river flowing, haunting blood moon in the sky, chilling and intense visual experiencester:1.2), dark, blood rain, blood river, blood moon",
                         "(worst quality:1.2), (low quality:1.2), (lowres:1.1), (monochrome:1.1), (greyscale), multiple views, comic, sketch, (((bad anatomy))), (((deformed))), (((disfigured))), watermark, multiple_views,mutation hands, mutation fingers, extra fingers, missing fingers, watermark"),
           "female-sorcerer" :(" 8k resolution, female sorcerer in a cloak adorned with magical symbols , intricate details , hdr, (hyper detailed:1.2) , cinematic shot , vignette ,centered, high resolution , sharp image, finely detailed body parts covered in a white dress, medium breasts ,ray tracing, long white hair, same pair of eye, formed hands , black witch hat on the head, left and right eyes identical, finely detailed face , finely detailed eyes , darker blacks, back most background environment, antialiasing 16x, texture quality ultra , blue eyes ",
                               "(low quality, worst quality:1.4), skinny hands and body, less fingers , more fingers, interlocked fingers, border, open mouth, different eyes , red eyes ,"),
           "forest-waterfall" : ("fawn drinking water, animals,(masterpiece, ultra quality:1.2), extremely detailed, volumetric lighting, ambient soft lighting, outdoors, nature, forest, trees, grass, plants,  flowers, river, caustics, water flow, ripples, (waterfall:1.2), pond, jungle, lush leaves, fern, clear image ,  8k, raytracing, reflection,  light rays , ultra textured , anistrophic filtered , more greenery,  white flowers near the water, butterflies in front of the view.",
                                 "(EasyNegative:0.8), (worst quality, low quality:1.2), tight, skin tight, impossible clothes, (ribs:1.2)")
}

async def create_qr1_request(data: schema.CreateQR1Request):
    url = data.url
    if data.prompt not in list(prompts.keys()):
        raise HTTPException(status_code=404,detail="Prompt not available")
    parameters = util.get_prompt(prompts[data.prompt])

    response = await collection.insert_one({"status": "available",
                                            "request_type": "qr1",
                                            "url": url,
                                            "discord_id": Int64(data.discord_id),
                                            "created_at": datetime.utcnow(),
                                            "lastModified": datetime.utcnow(),
                                            "parameters": parameters,
                                            })
    return str(response.inserted_id)


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
        elif request.get("request_type") == "qr1":
            return await _get_request_qr1(request,session_id)
    else:
        return {"status": request.get("status")}
async def _get_request_qr1(request,session_id):
    image = await aws_client.download_file(f"{session_id}_QR1.png")
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"status": "complete", "image": image}
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

async def request_completed_single_output(session_id: str,location):
    """
    Updates the status of the request to available.
    {"status":"complete","processed_at":datetime.utcnow()}
    """
    status = await collection.update_one({'_id': ObjectId(session_id)},
                                         {'$set': {"status": 'complete',
                                                   "processed_at": datetime.utcnow(),
                                                   "output":{"images":[location]}},
                                          "$currentDate": {"lastModified": True}},
                                         )
    if not status.matched_count:
        raise HTTPException(status_code=404, detail="Session_id not found")
async def request_completed_txt2img(session_id: str,locations,grid_location):
    """
    Updates the status of the request to available.
    {"status":"complete","processed_at":datetime.utcnow()}
    """
    status = await collection.update_one({'_id': ObjectId(session_id)},
                                         {'$set': {"status": 'complete',
                                                   "processed_at": datetime.utcnow(),
                                                   "output":{"images":locations,"grid_image":grid_location}},
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
    request = await collection.find_one_and_update({"status": "available","request_type":{"$in":["txt2img","upscale","qr1"]}},
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
    elif request.get("request_type") == "qr1":
        url = request.get("url")
        parameters = request.get("parameters")
        if len(url) > 22:
            url = await util.shorten_url(url)

        print(url)

        qr = util.make_qr(url)
        qr = util.image_to_base64(qr)

        parameters["alwayson_scripts"]["controlnet"]["args"][0]["input_image"] = qr
        parameters["alwayson_scripts"]["controlnet"]["args"][1]["input_image"] = qr
        payload = {
            "request_type": str(request.get("request_type")),
            "session_id": str(request["_id"]),
            "parameters": request.get("parameters"),
        }
    else:
        raise HTTPException(status_code=404, detail="Request Type not found")
    return payload
