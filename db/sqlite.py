import aiosqlite as sql

conn = sql.connect('new.db')

CREATE_TABLE_HOSTS = """
CREATE TABLE IF NOT EXISTS HOSTS(
    UUID VARCHAR(36) NOT NULL PRIMARY KEY,
    LAST_UPDATE TIMESTAMP default CURRENT_TIMESTAMP
);
"""

INSERT_UPDATE_HOST = """
INSERT INTO HOSTS (UUID, LAST_UPDATE) VALUES ('{}', CURRENT_TIMESTAMP)
ON CONFLICT (UUID) DO UPDATE SET LAST_UPDATE = CURRENT_TIMESTAMP;
"""

QUERY_HOSTS = """
SELECT * FROM HOSTS WHERE LAST_UPDATE < DATETIME('now', '{}');
"""


async def create_table():
    await conn.__aenter__()
    async with conn.execute(CREATE_TABLE_HOSTS) as c:
        await c.fetchall()


async def ping_host(uuid):
    async with conn.execute(INSERT_UPDATE_HOST.format(uuid)) as c:
        await c.fetchall()


async def get_offline_hosts(time="-1 minute"):
    async with conn.execute(QUERY_HOSTS.format(time)) as c:
        return await c.fetchall()


async def get_all_hosts():
    async with conn.execute("SELECT * FROM HOSTS;") as c:
        return await c.fetchall()


