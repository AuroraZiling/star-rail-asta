import json
import time
import requests

from ..Utils import log_recorder as log


def downloadFromJson(url, dstDir, dstName):
    timeStart = time.time()
    log.infoWrite(f"[Downloader] Trying to get JSON file from {url} in sync mode")
    jsonData = requests.get(url)
    if jsonData:
        log.infoWrite(
            f"[Downloader] The JSON file has been successfully downloaded and stored in {dstDir}/{dstName} (Time consumption: {time.time() - timeStart}s)")
        return open(f"{dstDir}/{dstName}", "w", encoding="utf-8").write(
            json.dumps(jsonData.json(), indent=4, ensure_ascii=False))
    log.errorWrite(f"[Downloader] JSON file download failed ({url})")
    return open(f"{dstDir}/{dstName}", "w", encoding="utf-8")


def downloadFromImage(url, dstDir, dstName):
    timeStart = time.time()
    log.infoWrite(f"[Downloader] Trying to get image from {url} in sync mode")
    imageData = requests.get(url)
    if imageData:
        log.infoWrite(
            f"[Downloader] The image has been successfully downloaded and stored in {dstDir}/{dstName} (Time consumption: {time.time() - timeStart}s)")
        return open(f"{dstDir}/{dstName}", "wb").write(imageData.content)
    log.errorWrite(f"[Downloader] image download failed ({url})")
    return None