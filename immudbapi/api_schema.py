from aiohttp import request
from config import IMMUDB_API_URL

async def post_transaction(data):
    async with request("POST", IMMUDB_API_URL + "/transaction", json=data) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            raise Exception("Error posting transaction" )

