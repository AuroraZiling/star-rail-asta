import json
import os

from .tools import Tools
from ...Metadata import character_list, weapon_list
from ...Scripts.Utils import log_recorder as log


utils = Tools()


def updateMetaData(dataType, data=None):
    if dataType == "character" and not data:
        data = character_list.categoryCharacterInStar()
    elif dataType == "weapon" and not data:
        data = weapon_list.categoryWeaponInStar()
    elif dataType == "permanent" and not data:
        data = character_list.getPermanentCharacter()
    if not os.path.exists(f"{utils.getConfigPath()}/metadata/"):
        os.mkdir(f"{utils.getConfigPath()}/metadata/")
    open(f"{utils.getConfigPath()}/metadata/{dataType}.json", 'w', encoding="utf-8").write(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))
    log.infoWrite(f"[Metadata_utils] Metadata updated: {dataType}")


def readMetaData(dataType):
    if os.path.exists(f"{utils.getConfigPath()}/metadata/{dataType}.json"):
        return json.loads(open(f"{utils.getConfigPath()}/metadata/{dataType}.json", 'r', encoding="utf-8").read())
    else:
        return None
