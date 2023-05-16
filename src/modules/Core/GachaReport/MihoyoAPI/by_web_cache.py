from pathlib import Path
from urllib import parse
from win32api import GetTempFileName, GetTempPath, CopyFile

from ....Scripts.Utils.tools import Tools
from ..gacha_report_utils import extractAPI

utils = Tools()


def getURL(gameDataPath):
    url = None
    webCacheData = Path(gameDataPath) / "webCaches/Cache/Cache_Data/data_2"
    webCacheDataTmp = Path(GetTempFileName(GetTempPath(), f"webCacheData", 0)[0])
    CopyFile(str(webCacheData), str(webCacheDataTmp))
    results = [extractAPI(result) for result in [result.split(b"\x00")[0].decode(errors="ignore") for result in webCacheDataTmp.read_bytes().split(b"1/0/")]]
    results = [result for result in results if result]

    if results:
        url = results[-1]

    if webCacheDataTmp.is_file():
        webCacheDataTmp.unlink()


    return url
