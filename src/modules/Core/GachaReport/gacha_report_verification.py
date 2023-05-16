import os
from ...Scripts.Utils.tools import Tools

utils = Tools()


def dataVerification(uid):
    if os.path.exists(f"{utils.workingDir}/data/{uid}/{uid}_data.pickle") and os.path.exists(
            f"{utils.workingDir}/data/{uid}/{uid}_export_data.json"):
        return True
    return False
