import os
from dotenv import load_dotenv
import aioboto3
import base64

load_dotenv()
ACCESS_KEY = os.getenv("AWS_KEY")
ACCESS_SECRET = os.getenv("AWS_SECRET")
session = aioboto3.Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=ACCESS_SECRET)


async def upload_file(name, file):
    async with session.resource("s3") as s3:
        bucket = await s3.Bucket('test-metex')  #
        await bucket.upload_fileobj(file, name)


async def upload_base64(base64_string, name):
    async with session.resource("s3") as s3:
        obj = await s3.Object('test-metex', name+".png")
        await obj.put(Body=base64.b64decode(base64_string.split(",", 1)[0]))


if __name__ == '__main__':
    import asyncio
    base64_str = open("../app/testimage.txt", "r").read()
    asyncio.run(upload_base64("testimage.png", base64_str))
    print("Done")

# server {
#         listen 80;
#         server_name 18.206.126.95;
#         location / {
#               proxy_pass http://127.0.0.1:8000;
#         }
#         }

