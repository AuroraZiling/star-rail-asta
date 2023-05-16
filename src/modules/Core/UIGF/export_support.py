import json
import pathlib
import pickle
import time

from ...Scripts.Utils.config_utils import ConfigUtils
from ...constant import UIGF_VERSION

utils = ConfigUtils()


class ExportSupport:
    def __init__(self, UID):
        self.uid = UID
        self.dataPath = f"{utils.workingDir}/data/{self.uid}/{self.uid}_data.pickle"

    def UIGFSave(self, dst):
        data = pickle.load(open(self.dataPath, 'rb'))
        data["info"]["export_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        data["info"]["export_timestamp"] = int(round(time.time() * 1000))
        data["info"]["export_app"] = "sangonomiya"
        data["info"]["export_app_version"] = utils.appVersion
        data["info"]["uigf_version"] = UIGF_VERSION
        data['info']['uid'] = self.uid
        open(dst, 'w', encoding="utf-8").write(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))