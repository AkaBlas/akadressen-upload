import asyncio
import logging

from uploader import AkaDressenUploader

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def do_upload():
    async with AkaDressenUploader() as uploader:
        await uploader.do_akadressen_upload()


if __name__ == "__main__":
    asyncio.run(do_upload())
