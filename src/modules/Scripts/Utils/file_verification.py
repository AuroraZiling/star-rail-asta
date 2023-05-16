import json
import os
import pathlib

from ..Utils import tools, log_recorder as log

utils = tools.Tools()


def create_directory(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    log.infoWrite(f"[File Verification] Directory {path} created")


def find_directory(path):
    if not os.path.exists(path):
        return False
    return True


def assetsCheck():
    try:
        filesList = \
            json.loads(
                open(f"{utils.workingDir}/assets/configs/files_verification.json", 'r', encoding="utf-8").read())[
                "files"]
        for file in filesList:
            if not os.path.exists(f"{utils.workingDir}{file[0]}"):
                log.errorWrite(f"[File Verification] 素材({file})文件不存在")
    except FileNotFoundError:
        log.errorWrite("[File Verification] 素材索引文件不存在")
