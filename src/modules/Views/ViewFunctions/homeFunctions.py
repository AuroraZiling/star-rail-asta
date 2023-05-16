import json
import os
import requests

from PySide6.QtCore import QThread, Signal

from ...Scripts.Utils.config_utils import ConfigUtils
from ...constant import SOFTWARE_ANNOUNCEMENT_URL

utils = ConfigUtils()


class HomeSoftwareAnnouncementThread(QThread):
    trigger = Signal(str)

    def __init__(self, parent=None):
        super(HomeSoftwareAnnouncementThread, self).__init__(parent)

    def run(self):
        self.trigger.emit("正在获取公告...")
        try:
            originalInfo = requests.get(SOFTWARE_ANNOUNCEMENT_URL).text
        except requests.exceptions.SSLError:
            self.trigger.emit("公告获取失败")
            return
        except requests.exceptions.ConnectionError:
            self.trigger.emit("无网络连接")
            return
        self.trigger.emit(originalInfo)