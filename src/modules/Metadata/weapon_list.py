import requests
from ..constant import WEAPON_URL


def categoryWeaponInStar():
    originalData = requests.get(WEAPON_URL).json()["data"]["list"][0]["list"]
    level_5 = {}
    level_4 = {}
    level_3 = {}
    for eachCharacter in originalData:
        if "五星" in eachCharacter["ext"]:
            level_5.update({eachCharacter["title"]: eachCharacter["content_id"]})
        elif "四星" in eachCharacter["ext"]:
            level_4.update({eachCharacter["title"]: eachCharacter["content_id"]})
        elif "三星" in eachCharacter["ext"]:
            level_3.update({eachCharacter["title"]: eachCharacter["content_id"]})
    return {"5": level_5, "4": level_4, "3": level_3}