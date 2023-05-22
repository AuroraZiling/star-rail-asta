import os
import pickle
import time

from ...Scripts.Utils.tools import Tools

utils = Tools()


def getUIDList():
    return os.listdir(f"{utils.working_dir}/data/")


def getDataFromUID(uid):
    if os.path.exists(f"{utils.working_dir}/data/{uid}") and uid:
        return pickle.load(open(f"{utils.working_dir}/data/{uid}/{uid}_data.pickle", 'rb'))
    else:
        return None


def sortDataByTime(data):
    opt = [i for i in sorted(data, key=lambda unit: unit["timestamp"])][::-1]
    index = 0
    while index < len(opt)-10:
        if opt[index]["timestamp"] == opt[index+1]["timestamp"]:
            for innerIndex in range(0, 5):
                opt[index+innerIndex], opt[index + 9 - innerIndex] = opt[index + 9 - innerIndex], opt[index+innerIndex]
            index += 9
        index += 1
    return opt


def convertDataToTable(data):
    categories = {"1": [], "2": [], "11": [], "12": []}
    copied_categories = {"1": [], "2": [], "11": [], "12": []}
    for unit in data["list"]:
        eachUnit = {
            "item_type": unit["item_type"],
            "name": unit["name"],
            "time": unit["time"],
            "rank_type": unit["rank_type"]
        }
        categories[unit["gacha_type"]].append(eachUnit)
        eachUnit.update({"timestamp": time.mktime(time.strptime(unit["time"], "%Y-%m-%d %H:%M:%S"))})
        copied_categories[unit["gacha_type"]].append(eachUnit)
    categories["1"] = sortDataByTime(copied_categories["1"])
    categories["2"] = sortDataByTime(copied_categories["2"])
    categories["11"] = sortDataByTime(copied_categories["11"])
    categories["12"] = sortDataByTime(copied_categories["12"])
    return categories
