import json
import pathlib
import pickle
import time
import requests

from PySide6.QtCore import QThread, Signal

from ...constant import SRGF_VERSION, SRGF_DATA_MODEL, GACHATYPE, SRGF_GACHATYPE
from ..SRGF.converter import originalToSRGFListUnit
from .gacha_report_utils import updateAPI
from ...Scripts.Utils.tools import Tools

utils = Tools()
gachaTarget = ""


class GachaReportThread(QThread):
    trigger = Signal(tuple)

    def __init__(self, gachaUrl, parent=None):
        super(GachaReportThread, self).__init__(parent)
        self.uid = ""
        self.region_time_zone = ""
        self.gachaUrl = gachaUrl

    def run(self):
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
        SRGFExportJsonData["info"]["export_timestamp"] = int(round(time.time() * 1000))
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
