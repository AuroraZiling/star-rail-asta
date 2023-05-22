import json
import pickle
import time

from ...Scripts.Utils.tools import Tools
from ...constant import SRGF_VERSION

utils = Tools()


class ExportSupport:
    def __init__(self, UID):
        self.uid = UID
        self.dataPath = f"{utils.working_dir}/data/{self.uid}/{self.uid}_data.pickle"

    def SRGFSave(self, dst):
        data = pickle.load(open(self.dataPath, 'rb'))
        data["info"]["export_timestamp"] = int(round(time.time() * 1000))
        data["info"]["export_app"] = "asta"
        data["info"]["export_app_version"] = utils.app_version
        data["info"]["srgf_version"] = SRGF_VERSION
        data['info']['uid'] = self.uid
        open(dst, 'w', encoding="utf-8").write(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))
