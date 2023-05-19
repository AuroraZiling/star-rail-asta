from ....Scripts.Utils import tools
from ....constant import COLOR_MAPPING

utils = tools.Tools()


def originalTableDataToComplete(data):
    permanentList = utils.read_metadata("permanent")
    for eachData in ["1", "11", "12"]:
        currentData = data[eachData]
        guaranteeCounter = 0
        for index, unit in enumerate(currentData):
            currentData[index].update({"order": str(len(currentData) - index)})
            currentData[index].update({"gacha_mode": "单抽"})
            currentData[index].update({"color": "#FF0000"})
            currentData[index].update({"guarantee": "0"})
        time_tmp = [i["time"] for i in currentData]
        pos = 0
        while pos < len(time_tmp) - 9:
            if time_tmp[pos] == time_tmp[pos + 1]:
                for index in range(pos, pos + 10):
                    currentData[index].update({"gacha_mode": f"十连-{10 - index + pos}"})
                pos += 9
            pos += 1
        for index in range(len(currentData) - 1, -1, -1):
            eachUnitName = currentData[index]["name"]
            eachUnitRank = currentData[index]["rank_type"]
            guaranteeCounter += 1
            currentData[index]["guarantee"] = str(guaranteeCounter)
            if eachUnitRank == "5" and eachUnitName not in permanentList:
                guaranteeCounter = 0
            if eachUnitName not in permanentList:
                currentData[index]["color"] = COLOR_MAPPING[eachUnitRank]
                currentData[index]["rank_type"] = eachUnitRank
            elif eachUnitName in permanentList:
                currentData[index]["color"] = COLOR_MAPPING["5"]
                currentData[index]["rank_type"] = "5"
    return data
