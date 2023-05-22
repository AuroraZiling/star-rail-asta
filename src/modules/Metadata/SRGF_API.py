import hashlib
import os
from functools import partial

import requests
import json

from ..constant import SRGF_ITEM_ID_URL, SRGF_MD5_URL
from ..Scripts.Utils.tools import Tools

utils = Tools()


def updateSRGFItemIdList(language, localPath):
    if not os.path.exists(f"{utils.config_dir}/metadata/"):
        os.mkdir(f"{utils.config_dir}/metadata/")
    if not os.path.exists(localPath):
        with open(localPath, 'wb') as f:
            text = json.dumps(getSRGFItemIdList(language), indent=4, ensure_ascii=False).replace('\r\n', '\n')
            f.write(text.encode('utf-8'))
        return True
    with open(localPath, 'rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 1024), b''):
            d.update(buf)
    local_md5 = d.hexdigest()
    api_md5 = requests.get(SRGF_MD5_URL).json()["chs"]
    if not local_md5 == api_md5:
        with open(localPath, 'wb') as f:
            text = json.dumps(getSRGFItemIdList(language), indent=4, ensure_ascii=False).replace('\r\n', '\n')
            f.write(text.encode('utf-8'))
        return True
    return False


def getSRGFItemIdList(language):
    return requests.get(SRGF_ITEM_ID_URL.format(lang=language)).json()