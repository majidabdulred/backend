from typing import Union, Dict

from motor.motor_asyncio import AsyncIOMotorCollection

from db.client import db

collection: AsyncIOMotorCollection = db.get_collection("users")
async def get_user_by_id(user_id: int) -> Union[Dict, None]:
    """
    Gets a user by their id.
    :param user_id:
    :return:
    """
    return await collection.find_one({"discord_id": user_id})
async def append_request(discord_id,session_id):
    """
    Adds a request to the user's list of requests.
    If user doesn't exist then it creates a new user.
    :param discord_id:
    :param session_id:
    :return:
    """
    await collection.update_one({"discord_id": discord_id}, {"$push": {"requests": session_id}},upsert=True)
