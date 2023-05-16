# coding:utf-8
import json
from enum import Enum

from PySide6.QtCore import QLocale
from qfluentwidgets import qconfig, QConfig, ConfigItem, BoolValidator, FolderValidator, ConfigSerializer

from ...Scripts.Utils.config_utils import ConfigUtils
from ...Core.GachaReport.gacha_report_utils import getDefaultGameDataPath

utils = ConfigUtils()

workingDir = utils.workingDir
configPath = utils.configPath
settingsLocal = json.loads(open(f"{workingDir}/assets/configs/application.json", 'r').read())
appVersion, UIVersion = settingsLocal["application_version"], settingsLocal["ui_version"]


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = "zh_CN"
    ENGLISH = "en_US"
    AUTO = "Auto"


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):

    """ Config of application """

    # General
    ConfigItem("Versions", "application", appVersion)
    ConfigItem("Versions", "ui", UIVersion)

    # Game
    gameDataFolder = ConfigItem(
        "Folders", "GameData", getDefaultGameDataPath(), FolderValidator())

    # Storage
    storageDataFolders = ConfigItem(
        "Folders", "Data", "data", FolderValidator())
    storageCacheFolders = ConfigItem(
        "Folders", "Cache", "cache", FolderValidator())
    storageLogFolders = ConfigItem(
        "Folders", "Log", "logs", FolderValidator())

    # Customize
    customizeAutoDeleteLog = ConfigItem("Customize", "autoDeleteLog", False, BoolValidator(), restart=True)

    # Gacha Report
    gachaReportLastUID = ConfigItem(
        "GachaReport", "lastUID", "")

    # MetaData
    metaDataUpdateAtStartUp = ConfigItem(
        "MetaData", "metaDataUpdateAtStartUp", True, BoolValidator()
    )


cfg = Config()
qconfig.load(f"{configPath}/settings.json", cfg)