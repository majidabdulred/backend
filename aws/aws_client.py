import os
from dotenv import load_dotenv
import aioboto3
import base64
import io

load_dotenv()
ACCESS_KEY = os.getenv("AWS_KEY")
ACCESS_SECRET = os.getenv("AWS_SECRET")
session = aioboto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=ACCESS_SECRET)


async def upload_file(name, file):
    async with session.resource("s3") as s3:
        bucket = await s3.Bucket('test-metex')  #
        await bucket.upload_fileobj(file, name)


async def upload_base64_to_aws(base64_string, name):
    async with session.resource("s3") as s3:
        obj = await s3.Object('test-metex', name + ".png")
        await obj.put(Body=base64.b64decode(base64_string.split(",", 1)[0]))

async def delete_file(name: str):
    async with session.resource("s3") as s3:
        bucket = await s3.Bucket('test-metex')  #
        await bucket.delete_objects(Delete={"Objects": [{"Key": name}]})
async def download_file(name: str) -> str:
    async with session.resource("s3") as s3:
        bucket = await s3.Bucket('test-metex')  #
        try:
            file = io.BytesIO()
            await bucket.download_fileobj(name, file)
            print("File successfully downloaded")
            file.seek(0)
            base64_str = base64.b64encode(file.read()).decode("utf-8")
            return base64_str
        except Exception as e:
            print("AWS File not found")


if __name__ == '__main__':
    import asyncio

    # base64_str = open("../app/testimage.txt", "r").read()
    # asyncio.run(upload_base64_to_aws("testimage.png", base64_str))
    # print("Done")

# server {
#         listen 80;
#         server_name 18.206.126.95;
#         location / {
#               proxy_pass http://127.0.0.1:8000;
#         }
#         }
