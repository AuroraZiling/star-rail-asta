import json
import os
import pathlib
import shutil

from PySide6.QtGui import QFont

from ..Utils import tools, log_recorder as log


class ConfigUtils(tools.Tools):
    def __init__(self):
        super().__init__()
        self.license = open(f"{self.workingDir}/assets/configs/license", 'r').read()
        self.openSourceLicense = open(f"{self.workingDir}/assets/configs/open_source", 'r').read()
        self.configPath = super().getConfigPath()
        self.themeColor = "#009faa"
        self.accountInfo = {}

        self.settings = {}
        self.appVersion = "Unknown"
        self.UIVersion = "Unknown"

        self.__fileCheck()
        self.__settings()

    def __fileCheck(self):
        pathlib.Path(self.configPath).mkdir(parents=True, exist_ok=True)
        if not os.path.exists(f"{self.configPath}/account.json"):
            shutil.copyfile(f"{self.workingDir}/assets/configs/modelFiles/account.json",
                            f"{self.configPath}/account.json")

    def __settings(self):
        if os.path.exists(f"{self.configPath}/settings.json"):
            self.settings = json.loads(open(f"{self.configPath}/settings.json", 'r').read())
        self.settingsLocal = json.loads(open(f"{self.workingDir}/assets/configs/application.json", 'r').read())
        self.accountInfo = json.loads(open(f"{self.configPath}/account.json", 'r', encoding="utf-8").read())
        self.appVersion = self.settingsLocal["application_version"]
        self.UIVersion = self.settingsLocal["ui_version"]

    def getFont(self, size):
        if self.OSName == "Windows":
            return QFont("Microsoft YaHei", size)
        elif self.OSName == "macOS":
            return QFont("Microsoft YaHei", size + 6)

    def getConfigAutoDeleteLog(self):
        try:
            with open(f"{self.configPath}/settings.json", 'r') as f:
                return json.loads(f.read())["Customize"]["autoDeleteLog"]
        except KeyError:
            return False
        except FileNotFoundError:
            return False

    def getAnnounceData(self):
        try:
            return json.loads(open(f"{self.workingDir}/cache/announce.json", 'r', encoding="utf-8").read())
        except json.decoder.JSONDecodeError:
            return None

    def getAnnounceIconData(self):
        try:
            return json.loads(open(f"{self.workingDir}/cache/announce_icons.json", 'r', encoding="utf-8").read())
        except json.decoder.JSONDecodeError:
            return None

    def deleteAllLogFiles(self):
        logDir = os.listdir(f"{self.workingDir}/logs")
        for eachLogFile in logDir:
            try:
                os.remove(f"{self.workingDir}/logs/{eachLogFile}")
            except PermissionError:
                continue
        log.infoWrite("[ConfigUtils] All old logs deleted")

    def deleteAllCacheFiles(self):
        logDir = os.listdir(f"{self.workingDir}/cache")
        for eachLogFile in logDir:
            try:
                os.remove(f"{self.workingDir}/cache/{eachLogFile}")
            except PermissionError:
                continue
        log.infoWrite("[ConfigUtils] All cache files deleted")

    def getAccountUid(self):
        self.accountInfo = json.loads(open(f"{self.configPath}/account.json", 'r', encoding="utf-8").read())
        log.infoWrite(f"[ConfigUtils] UID Get: {self.accountInfo['uid']}")
        return self.accountInfo["uid"]

    def getAccountName(self):
        self.accountInfo = json.loads(open(f"{self.configPath}/account.json", 'r', encoding="utf-8").read())
        log.infoWrite(f"[ConfigUtils] Name Get: {self.accountInfo['name']}")
        return self.accountInfo["name"]

    def getVersionType(self):
        return "dev" if "Dev" in self.appVersion else "release"
