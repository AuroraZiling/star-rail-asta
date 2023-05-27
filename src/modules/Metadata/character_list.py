import requests
from ..constant import CHARACTER_URL, PERMANENT_CHARACTER_URL


def getPermanentCharacter():
    return requests.get(PERMANENT_CHARACTER_URL).json()["permanent"]


def categoryCharacterInStar():
    originalData = requests.get(CHARACTER_URL).json()["data"]["list"][0]["list"]
    level_5 = {}
    level_4 = {}
    for eachCharacter in originalData:
        if "开拓者" not in eachCharacter["title"]:
            if "五星" in eachCharacter["ext"]:
                level_5.update({eachCharacter["title"]: eachCharacter["content_id"]})
            elif "四星" in eachCharacter["ext"]:
                level_4.update({eachCharacter["title"]: eachCharacter["content_id"]})
    return {"5": level_5, "4": level_4}
