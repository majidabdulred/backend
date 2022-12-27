import asyncio

from db import host_session
from db import sqlite


async def update_hosts_data(interval: int = 60):
    """
    Updates the status of the host from sqlite database to the mongodb database per interval (secs)
    :param interval:
    :return:
    """

    async def task():
        hosts = await sqlite.get_all_hosts()
        await host_session.update_hosts_status(hosts)

    while True:
        await asyncio.sleep(interval)
        asyncio.get_event_loop().create_task(task())


async def host_went_offline(host_id: str):
    pass
