from PySide6.QtCore import QThread, Signal

from ...Scripts.Utils import metadata_utils
from ...Scripts.Utils.config_utils import ConfigUtils

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
