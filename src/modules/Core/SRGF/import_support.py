import datetime
import json
import pathlib
import pickle
import time

from ...Scripts.Utils import tools
from ...constant import SRGF_DATA_MODEL, SRGF_VERSION

utils = tools.Tools()


class ImportSupport:
    def __init__(self, UID, language):
        self.uid = UID
        self.language = language

        self.SRGFImportJsonData = SRGF_DATA_MODEL

    def SRGFSave(self, srgfDataList):
        self.SRGFImportJsonData["info"]["export_timestamp"] = int(time.mktime(datetime.datetime.now().timetuple()))
        self.SRGFImportJsonData["info"]["export_app"] = "asta"
        self.SRGFImportJsonData["info"]["region_time_zone"] = srgfDataList["info"]["region_time_zone"]
        self.SRGFImportJsonData["info"]["export_app_version"] = utils.app_version
        self.SRGFImportJsonData["info"]["srgf_version"] = SRGF_VERSION
        self.SRGFImportJsonData['info']['uid'] = self.uid
        self.SRGFImportJsonData["list"] = srgfDataList["list"]
        pathlib.Path(f"{utils.working_dir}/data/{self.uid}").mkdir(parents=True, exist_ok=True)
        open(f"{utils.working_dir}/data/{self.uid}/{self.uid}_export_data.json", "w", encoding="utf-8").write(
            json.dumps(self.SRGFImportJsonData, indent=2, sort_keys=True, ensure_ascii=False))
        with open(f"{utils.working_dir}/data/{self.uid}/{self.uid}_data.pickle", 'wb') as f:
            pickle.dump(self.SRGFImportJsonData, f)
