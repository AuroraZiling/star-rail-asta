from PySide6.QtCore import QThread, Signal

from ...Scripts.Utils import tools
from ...Metadata.SRGF_API import updateSRGFItemIdList

utils = tools.Tools()


class MetadataUpdateThread(QThread):
    trigger = Signal(bool)

    def __init__(self, parent=None):
        super(MetadataUpdateThread, self).__init__(parent)

    def run(self):
        utils.update_metadata("character")
        utils.update_metadata("weapon")
        utils.update_metadata("permanent")
        self.trigger.emit(True)


class MetadataSRGFUpdateThread(QThread):
    trigger = Signal(bool)

    def __init__(self, parent=None):
        super(MetadataSRGFUpdateThread, self).__init__(parent)

    def run(self):
        result = updateSRGFItemIdList("chs", f"{utils.config_dir}/metadata/uigf_dict.json")
        self.trigger.emit(result)
