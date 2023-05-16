import requests
from ...constant import UPDATE_URL


def findLatestVersion():
    return requests.get(UPDATE_URL).json()[0]["name"]


def compareVersion(current, target):
    if "Dev" in current and "Dev" in target:
        return True if int(target.split(' ')[-1]) > int(current.split(' ')[-1]) else False
    elif "Dev" not in current and "Dev" not in target:
        return True if int(target.split(' ')[-1]) > int(current.split(' ')[-1]) else False
    else:
        return False
