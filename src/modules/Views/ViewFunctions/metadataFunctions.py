from PySide6.QtCore import QThread, Signal

from ...Scripts.Utils import metadata_utils
from ...Scripts.Utils.config_utils import ConfigUtils
from ...Metadata.UIGF_API import updateUIGFItemIdList

utils = ConfigUtils()


class MetadataUpdateThread(QThread):
    trigger = Signal(bool)

    def __init__(self, parent=None):
        super(MetadataUpdateThread, self).__init__(parent)

    def run(self):
        metadata_utils.updateMetaData("character")
        metadata_utils.updateMetaData("weapon")
        metadata_utils.updateMetaData("permanent")
        self.trigger.emit(True)

class MetadataUIGFUpdateThread(QThread):
    trigger = Signal(bool)

    def __init__(self, parent=None):
        super(MetadataUIGFUpdateThread, self).__init__(parent)

    def run(self):
        result = updateUIGFItemIdList("chs", f"{utils.configPath}/metadata/uigf_dict.json")
        self.trigger.emit(result)