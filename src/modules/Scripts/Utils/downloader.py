import json
import time
import requests
import logging


def downloadFromJson(url, dstDir, dstName):
    timeStart = time.time()
    logging.info(f"[Downloader] Trying to get JSON file from {url} in sync mode")
    jsonData = requests.get(url)
    if jsonData:
        logging.info(
            f"[Downloader] The JSON file has been successfully downloaded and stored in {dstDir}/{dstName} (Time consumption: {time.time() - timeStart}s)")
        return open(f"{dstDir}/{dstName}", "w", encoding="utf-8").write(
            json.dumps(jsonData.json(), indent=4, ensure_ascii=False))
    logging.error(f"[Downloader] JSON file download failed ({url})")
    return open(f"{dstDir}/{dstName}", "w", encoding="utf-8")


def downloadFromImage(url, dstDir, dstName):
    timeStart = time.time()
    logging.info(f"[Downloader] Trying to get image from {url} in sync mode")
    imageData = requests.get(url)
    if imageData:
        logging.info(
            f"[Downloader] The image has been successfully downloaded and stored in {dstDir}/{dstName} (Time consumption: {time.time() - timeStart}s)")
        return open(f"{dstDir}/{dstName}", "wb").write(imageData.content)
    logging.error(f"[Downloader] image download failed ({url})")
    return None
