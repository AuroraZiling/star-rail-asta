import json
import os
import logging

from ..Utils import tools

utils = tools.Tools()


def assetsCheck():
    logging.info("[File Verification] Running Assets Check")
    try:
        filesList = \
            json.loads(
                open(f"{utils.working_dir}/assets/configs/files_verification.json", 'r', encoding="utf-8").read())[
                "files"]
        for file in filesList:
            if not os.path.exists(f"{utils.working_dir}{file[0]}"):
                logging.error(f"[File Verification] 素材({file})文件不存在")
    except FileNotFoundError:
        logging.error("[File Verification] 素材索引文件不存在")
