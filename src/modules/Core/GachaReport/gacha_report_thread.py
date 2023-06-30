import datetime
import json
import os
import pathlib
import pickle
import time
import requests

from PySide6.QtCore import QThread, Signal

from ...constant import SRGF_VERSION, SRGF_DATA_MODEL, GACHATYPE
from ..SRGF.converter import originalToSRGFListUnit
from .gacha_report_utils import updateAPI
from ...Scripts.Utils.tools import Tools

utils = Tools()
gachaTarget = ""


class GachaReportThread(QThread):
    trigger = Signal(tuple)
    isAdditional = False

    def __init__(self, gachaUrl, parent=None, isAdd=False):
        super(GachaReportThread, self).__init__(parent)
        self.uid = ""
        self.region_time_zone = ""
        self.gachaUrl = gachaUrl
        self.isAdditional = isAdd

    def run(self):
        if not self.isAdditional:
            SRGFExportJsonData = SRGF_DATA_MODEL
            gachaList = []
            for key in GACHATYPE.keys():
                end_id = "0"
                page = 0
                while True:
                    apiPerUnit = updateAPI(self.gachaUrl, GACHATYPE[key], 20, page, end_id)
                    responsePerUnit = json.loads(requests.get(apiPerUnit).content.decode("utf-8"))
                    if responsePerUnit["data"]:
                        gachaPerResponse = responsePerUnit["data"]["list"]
                        if not len(gachaPerResponse):
                            break
                        self.uid = responsePerUnit['data']["list"][0]['uid']
                        self.region_time_zone = str(responsePerUnit['data']["region_time_zone"])
                        self.trigger.emit((0, f"正在获取第{str(page + 1)}页 | {key}", self.uid))
                        for i in gachaPerResponse:
                            gachaList.append(originalToSRGFListUnit(i))
                        end_id = responsePerUnit["data"]["list"][-1]["id"]
                        page += 1
                        self.msleep(300)
                    else:
                        self.trigger.emit((-1, f"数据获取失败", "请检查:\n你输入URL是否可用\n距离上一次在游戏内打开跃迁记录的时间间隔在一天以内"))
                        return
            pathlib.Path(f"{utils.working_dir}/data/{self.uid}").mkdir(parents=True, exist_ok=True)
            SRGFExportJsonData["info"]["export_timestamp"] = int(time.mktime(datetime.datetime.now().timetuple()))
            SRGFExportJsonData["info"]["export_app"] = "asta"
            SRGFExportJsonData["info"]["export_app_version"] = utils.app_version
            SRGFExportJsonData["info"]["srgf_version"] = SRGF_VERSION
            SRGFExportJsonData["info"]["region_time_zone"] = int(self.region_time_zone)
            SRGFExportJsonData['info']['uid'] = self.uid
            SRGFExportJsonData["list"] = gachaList
            open(f"{utils.working_dir}/data/{self.uid}/{self.uid}_export_data.json", "w", encoding="utf-8").write(
                json.dumps(SRGFExportJsonData, indent=2, sort_keys=True, ensure_ascii=False))
            with open(f"{utils.working_dir}/data/{self.uid}/{self.uid}_data.pickle", 'wb') as f:
                pickle.dump(SRGFExportJsonData, f)
            self.trigger.emit((1, "跃迁记录更新完毕", self.uid))
        else:
            dataPath = f"{utils.working_dir}/data/{self.isAdditional}/{self.isAdditional}_data.pickle"
            if not os.path.exists(dataPath):
                self.trigger.emit((-1, f"增量更新失败",
                                   "请检查是否对当前UID进行过全量更新"))
                return
            data = pickle.load(open(dataPath, 'rb'))
            gachaList = data["list"]
            for key in GACHATYPE.keys():
                latestId = [i["id"] for i in gachaList if i["gacha_type"] == GACHATYPE[key]]
                gachaTypeEnd = False
                if latestId:
                    latestId = latestId[0]
                end_id = "0"
                page = 0
                while True:
                    apiPerUnit = updateAPI(self.gachaUrl, GACHATYPE[key], 20, page, end_id)
                    responsePerUnit = json.loads(requests.get(apiPerUnit).content.decode("utf-8"))
                    if responsePerUnit["data"]:
                        gachaPerResponse = responsePerUnit["data"]["list"]
                        if not len(gachaPerResponse):
                            break
                        self.uid = responsePerUnit['data']["list"][0]['uid']
                        self.region_time_zone = str(responsePerUnit['data']["region_time_zone"])
                        self.trigger.emit((0, f"正在获取第{str(page + 1)}页 | {key}", self.uid))
                        for i in gachaPerResponse:
                            if i["id"] == latestId:
                                gachaTypeEnd = True
                                break
                            gachaList.append(originalToSRGFListUnit(i))
                        if gachaTypeEnd:
                            break
                        end_id = responsePerUnit["data"]["list"][-1]["id"]
                        page += 1
                        self.msleep(300)
                    else:
                        self.trigger.emit((-1, f"数据获取失败", "请检查:\n你输入URL是否可用\n距离上一次在游戏内打开跃迁记录的时间间隔在一天以内"))
                        return
            data["info"]["export_app"] = "asta"
            data["info"]["export_app_version"] = utils.app_version
            data["info"]["srgf_version"] = SRGF_VERSION
            data["info"]["region_time_zone"] = int(self.region_time_zone)
            data['info']['uid'] = self.uid
            data["list"] = gachaList
            open(f"{utils.working_dir}/data/{self.uid}/{self.uid}_export_data.json", "w", encoding="utf-8").write(
                json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))
            with open(f"{utils.working_dir}/data/{self.uid}/{self.uid}_data.pickle", 'wb') as f:
                pickle.dump(data, f)
            self.trigger.emit((1, "跃迁记录更新完毕", self.uid))