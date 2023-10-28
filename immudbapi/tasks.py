import asyncio

from db import requests_col, host_session
from immudbapi.calculate import calculate_tokens
from immudbapi.api_schema import post_transaction

async def create_payment(session_id,recall=0):
    if recall > 5:
        return

    await asyncio.sleep(3)
    data = await requests_col.get_request_data(session_id)
    if data.get("paid") == "DONE":
        return
    if data.get("status") != "complete":
        await create_payment(session_id, recall=recall+1)
        return
    user = await host_session.get_host(str(data.get("assigned_to").id))
    if not user:
        return
    if user.get("wallet_id") is None:
        await requests_col.collection.update_one({"_id": data.get("_id")}, {"$set": {"paid": "NO_WALLET"}})
        return
    payload = {"action_type": "MINE",
               "to_wallet": user.get("wallet_id").lower(),
               "from_wallet": "0x0000000000000000000000000000000000000000",
               "tokens": calculate_tokens(data),
               "session_id": str(data.get("_id"))}

    response = await post_transaction(payload)
    if response:
        await requests_col.collection.update_one({"_id": data.get("_id")}, {"$set": {"paid": "DONE"}})