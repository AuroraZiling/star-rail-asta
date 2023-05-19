from PySide6.QtCore import QThread, Signal

from ...Scripts.Utils import tools
from ...Metadata.UIGF_API import updateUIGFItemIdList

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


class MetadataUIGFUpdateThread(QThread):
    trigger = Signal(bool)

    def __init__(self, parent=None):
        super(MetadataUIGFUpdateThread, self).__init__(parent)

    def run(self):
        result = updateUIGFItemIdList("chs", f"{utils.config_dir}/metadata/uigf_dict.json")
        self.trigger.emit(result)
