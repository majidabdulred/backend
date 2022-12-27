from datetime import datetime
from typing import List, Tuple

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import UpdateOne

from app import schema
from db import sqlite
from db.client import db

collection: AsyncIOMotorCollection = db.get_collection("hosts")


async def create_host_session(data: schema.CreateSessionHostRequest) -> str:
    host = await collection.find_one({"gpu_uuid": data.gpu_uuid})
    if host:
        return str(host.get("_id"))
    data = data.dict()
    return str((await collection.insert_one(data)).inserted_id)


async def host_exits(host_session_id: str) -> bool:
    return await collection.find_one({"_id": ObjectId(host_session_id)})


async def set_current_processing(host_session_id, session_id):
    """
    Sets the current request that is assigned to the host
    :param host_session_id:
    :param session_id:
    :return:
    """
    await collection.update_one({"_id": ObjectId(host_session_id)}, {"$set": {"current_processing":
        {
            "$ref": "requests",
            "$db": "backend",
            "$id": ObjectId(session_id)
        }}})


async def set_current_processing_as_none(host_session_id: str):
    """
    Sets the current request that is assigned to the host
    :param host_session_id:
    :return:
    """
    await collection.update_one({"_id": ObjectId(host_session_id)}, {"$set": {"current_processing": None}})


async def update_hosts_status(data: List[Tuple[str, str]]):
    def check_status(last_ping: str):
        last_ping = datetime.strptime(last_ping, "%Y-%m-%d %H:%M:%S")
        if (datetime.utcnow() - last_ping).total_seconds() > 60:
            return "offline"
        return "online"

    """
    Updates the status of all hosts.
    Input: Example data = [("123e4567-e89b-12d3-a456-426614174000","2022-12-25 05:39:42"),("2ab22345-e89b-4b31-a456-141740004266","2022-12-25 05:39:42")]
    :param data:
    :return:
    """

    to_update = []
    for host_id, timestamp in data:
        status = check_status(timestamp)
        to_update.append(UpdateOne({"_id": ObjectId(host_id)}, {"$set": {"status": status, "last_ping": timestamp},
                                                                "$currentDate": {"lastModified": True}}))

    await collection.bulk_write(to_update)


async def ping_host(host_session_id: str):
    await sqlite.ping_host(host_session_id)
