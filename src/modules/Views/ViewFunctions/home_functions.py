import json
import os
import requests

from PySide6.QtCore import QThread, Signal

from ...Scripts.Utils import downloader, tools
from ...constant import SOFTWARE_ANNOUNCEMENT_URL, ANNOUNCE_REQUEST_URL, ANNOUNCE_ICON_REQUEST_URL, \
    ANNOUNCE_CURRENT_UP_URL

utils = tools.Tools()


class HomeCurrentUPThread(QThread):
    trigger = Signal(int, int, str, str, str)

    def __init__(self, parent=None):
        super(HomeCurrentUPThread, self).__init__(parent)

    def run(self):
        character1ImagePath = f"{utils.working_dir}/assets/unknownAvatar.png"
        character1Pool = "信息获取失败"
        self.trigger.emit(0, 0, "正在获取信息...", "未知", character1ImagePath)
        self.trigger.emit(1, 0, "正在获取信息...", "未知", character1ImagePath)
        upWeaponList = []
        if not os.path.exists(f"{utils.working_dir}/cache/announce.json"):
            downloader.downloadFromJson(ANNOUNCE_REQUEST_URL, utils.working_dir + "/cache/", "announce.json")
            downloader.downloadFromJson(ANNOUNCE_ICON_REQUEST_URL, utils.working_dir + "/cache/",
                                        "announce_icons.json")
        downloader.downloadFromJson(ANNOUNCE_CURRENT_UP_URL, utils.working_dir + "/cache/", "current_up.json")
        if os.path.exists(f"{utils.working_dir}/cache/current_up.json") and os.path.exists(f"{utils.working_dir}/cache/announce.json"):
            originalCurrentUPInfo = json.loads(open(f"{utils.working_dir}/cache/current_up.json", 'r', encoding="utf-8").read())["data"]["list"]
            character1Time = f"{originalCurrentUPInfo[0]['start_time']} - {originalCurrentUPInfo[0]['end_time']}"
            downloader.downloadFromImage(originalCurrentUPInfo[0]['pool'][0]['icon'], utils.working_dir + "/cache/", "current_up_character_1.png")

            originalInfo = json.loads(open(f"{utils.working_dir}/cache/announce.json", encoding="utf-8").read())["data"]["list"]
            for announce in originalInfo:
                if "活动期间，限定5星角色「" in announce["content"]:
                    character1Pool = f"「{originalCurrentUPInfo[0]['title']}」跃迁 | {announce['content'].split('活动期间，限定5星角色')[1].split('跃迁成功概率限时提升')[0]}"
                if "活动期间，限定5星光锥「" in announce["content"]:
                    upWeaponList.append(announce["content"].split("活动期间，限定5星光锥「")[1].split("」")[0])
        else:
            self.trigger.emit(0, 0, "信息获取失败", "未知", character1ImagePath)
            self.trigger.emit(1, 0, "信息获取失败", "未知", character1ImagePath)
            return
        upWeaponList = ' '.join(upWeaponList)
        if os.path.exists(f"{utils.working_dir}/cache/current_up_character_1.png"):
            character1ImagePath = f"{utils.working_dir}/cache/current_up_character_1.png"
        self.trigger.emit(0, 0, character1Pool, character1Time, character1ImagePath)
        self.trigger.emit(1, 0, "武器: " + ' '.join(upWeaponList), "未知", character1ImagePath)


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
