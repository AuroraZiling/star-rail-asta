import json
import pathlib
import pickle
import time
import requests

from PySide6.QtCore import QThread, Signal

from ...constant import UIGF_VERSION, UIGF_DATA_MODEL, GACHATYPE, UIGF_GACHATYPE
from ..UIGF.converter import originalToUIGFListUnit
from .gacha_report_utils import updateAPI
from ...Scripts.Utils.tools import Tools

utils = Tools()
gachaTarget = ""


class GachaReportThread(QThread):
    trigger = Signal(tuple)

    def __init__(self, gachaUrl, parent=None):
        super(GachaReportThread, self).__init__(parent)
        self.uid = ""
        self.gachaUrl = gachaUrl

    def run(self):
        UIGFExportJsonData = UIGF_DATA_MODEL
        gachaList = []
        for key in GACHATYPE.keys():
            end_id = "0"
            page = 0
            if key == "始发跃迁":
                continue
            while True:
                apiPerUnit = updateAPI(self.gachaUrl, GACHATYPE[key], 20, page, end_id)
                responsePerUnit = json.loads(requests.get(apiPerUnit).content.decode("utf-8"))
                if responsePerUnit["data"]:
                    gachaPerResponse = responsePerUnit["data"]["list"]
                    if not len(gachaPerResponse):
                        break
                    self.uid = responsePerUnit['data']["list"][0]['uid']
                    self.trigger.emit((0, f"正在获取第{str(page + 1)}页 | {key}", self.uid))
                    for i in gachaPerResponse:
                        gachaList.append(originalToUIGFListUnit(i, UIGF_GACHATYPE[GACHATYPE[key]]))
                    end_id = responsePerUnit["data"]["list"][-1]["id"]
                    page += 1
                    self.usleep(500)
                else:
                    self.trigger.emit((-1, f"数据获取失败", "请检查:\n你输入URL是否可用\n距离上一次在游戏内打开祈愿记录的时间间隔在一天以内"))
                    return
        pathlib.Path(f"{utils.working_dir}/data/{self.uid}").mkdir(parents=True, exist_ok=True)
        UIGFExportJsonData["info"]["export_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        UIGFExportJsonData["info"]["export_timestamp"] = int(round(time.time() * 1000))
        UIGFExportJsonData["info"]["export_app"] = "asta"
        UIGFExportJsonData["info"]["export_app_version"] = utils.app_version
        UIGFExportJsonData["info"]["uigf_version"] = UIGF_VERSION
        UIGFExportJsonData['info']['uid'] = self.uid
        UIGFExportJsonData["list"] = gachaList
        open(f"{utils.working_dir}/data/{self.uid}/{self.uid}_export_data.json", "w", encoding="utf-8").write(
            json.dumps(UIGFExportJsonData, indent=2, sort_keys=True, ensure_ascii=False))
        with open(f"{utils.working_dir}/data/{self.uid}/{self.uid}_data.pickle", 'wb') as f:
            pickle.dump(UIGFExportJsonData, f)
        self.trigger.emit((1, "跃迁记录更新完毕", self.uid))
