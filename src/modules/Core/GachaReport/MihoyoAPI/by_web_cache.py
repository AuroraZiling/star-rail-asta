import os
import re
from pathlib import Path
from win32api import GetTempFileName, GetTempPath, CopyFile

from ....Scripts.Utils.tools import Tools
from ..gacha_report_utils import extractAPI

utils = Tools()


def getURL(gameDataPath):
    url = None
    version = None
    for i in os.listdir(Path(gameDataPath) / "StarRail_Data/webCaches/"):
        match = re.match(r'^(\d+).(\d+).(\d+).(\d+)$', i)
        if match:
            version = match.group(0)
    if version is None:
        return None
    webCacheData = Path(gameDataPath) / f"StarRail_Data/webCaches/{version}/Cache/Cache_Data/data_2"
    webCacheDataTmp = Path(GetTempFileName(GetTempPath(), f"webCacheData", 0)[0])
    if not os.path.exists(str(webCacheData)):
        return None
    CopyFile(str(webCacheData), str(webCacheDataTmp))
    results = [extractAPI(result) for result in [result.split(b"\x00")[0].decode(errors="ignore") for result in
                                                 webCacheDataTmp.read_bytes().split(b"1/0/")]]
    results = [result for result in results if result]

    if results:
        url = results[-1]

    if webCacheDataTmp.is_file():
        webCacheDataTmp.unlink()

    return url
