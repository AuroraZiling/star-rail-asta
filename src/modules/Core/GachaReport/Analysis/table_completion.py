from ....Scripts.Utils.metadata_utils import readMetaData
from ....constant import COLOR_MAPPING


def findUnitStar(data, unit):
    if unit in data["5"]:
        return "5"
    elif unit in data["4"]:
        return "4"
    elif unit in data["3"]:
        return "3"
    return "X"


def originalTableDataToComplete(data):
    characterList = readMetaData("character")
    weaponList = readMetaData("weapon")
    permanentList = readMetaData("permanent")
    for eachData in ["1", "11", "12"]:
        guaranteeCounter = 0
        for index, unit in enumerate(data[eachData]):
            unit.insert(0, str(len(data[eachData])-index))
            unit.append("单抽")
            unit.append("0")
            unit.append("#FF0000")
            unit.append("X")
        time_tmp = [i[3] for i in data[eachData]]
        pos = 0
        while pos < len(time_tmp) - 9:
            if time_tmp[pos] == time_tmp[pos + 1]:
                for i in range(pos, pos + 10):
                    data[eachData][i][4] = f"十连-{10 - i + pos}"
                pos += 9
            pos += 1
        for index in range(len(data[eachData])-1, -1, -1):
            eachUnitType = data[eachData][index][1]
            eachUnitName = data[eachData][index][2]
            guaranteeCounter += 1
            data[eachData][index][5] = str(guaranteeCounter)
            if eachUnitName in characterList["5"] and eachUnitName not in permanentList and not eachData == "12":
                guaranteeCounter = 0
            elif eachUnitName in weaponList["5"] and eachData == "12":
                guaranteeCounter = 0
            if eachUnitName not in permanentList:
                if eachUnitType == "光锥":
                    data[eachData][index][6] = COLOR_MAPPING[findUnitStar(weaponList, eachUnitName)]
                    data[eachData][index][7] = findUnitStar(weaponList, eachUnitName)
                elif eachUnitType == "角色":
                    data[eachData][index][6] = COLOR_MAPPING[findUnitStar(characterList, eachUnitName)]
                    data[eachData][index][7] = findUnitStar(characterList, eachUnitName)
            elif eachUnitName in permanentList:
                data[eachData][index][6] = COLOR_MAPPING["5"]
                data[eachData][index][7] = "5"
    return data