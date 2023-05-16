import json
import pathlib
import pickle
import time

from ...Scripts.Utils.config_utils import ConfigUtils
from ...constant import UIGF_DATA_MODEL, UIGF_VERSION

utils = ConfigUtils()


class ImportSupport:
    def __init__(self, UID, language, export_time):
        self.uid = UID
        self.language = language
        self.export_time = export_time
        self.export_app_version = utils.appVersion

        self.UIGFImportJsonData = UIGF_DATA_MODEL

    def UIGFSave(self, uigfDataList):
        self.UIGFImportJsonData["info"]["export_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.UIGFImportJsonData["info"]["export_timestamp"] = int(round(time.time() * 1000))
        self.UIGFImportJsonData["info"]["export_app"] = "sangonomiya"
        self.UIGFImportJsonData["info"]["export_app_version"] = utils.appVersion
        self.UIGFImportJsonData["info"]["uigf_version"] = UIGF_VERSION
        self.UIGFImportJsonData['info']['uid'] = self.uid
        self.UIGFImportJsonData["list"] = uigfDataList["list"]
        pathlib.Path(f"{utils.workingDir}/data/{self.uid}").mkdir(parents=True, exist_ok=True)
        open(f"{utils.workingDir}/data/{self.uid}/{self.uid}_export_data.json", "w", encoding="utf-8").write(
            json.dumps(self.UIGFImportJsonData, indent=2, sort_keys=True, ensure_ascii=False))
        with open(f"{utils.workingDir}/data/{self.uid}/{self.uid}_data.pickle", 'wb') as f:
            pickle.dump(self.UIGFImportJsonData, f)
