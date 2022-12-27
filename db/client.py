import asyncio
from os import getenv

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient

from config import TESTING

load_dotenv()
client: MongoClient = AsyncIOMotorClient(getenv("DB_SRV"))

# Attaches the client to the same loop
client.get_io_loop = asyncio.get_event_loop
db: AsyncIOMotorDatabase = client.get_database("backend" if not TESTING else "backend_test")
