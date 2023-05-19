# coding:utf-8
from enum import Enum

from PySide6.QtCore import QLocale
from qfluentwidgets import qconfig, QConfig, ConfigItem, BoolValidator, FolderValidator, ConfigSerializer

from .Scripts.Utils.tools import Tools
from .Core.GachaReport.gacha_report_utils import getDefaultGameDataPath

utils = Tools()


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
    ConfigItem("Versions", "application", utils.app_version)
    ConfigItem("Versions", "ui", utils.app_version)

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
        "MetaData", "metaDataUpdateAtStartUp", False, BoolValidator()
    )


cfg = Config()
qconfig.load(f"{utils.config_dir}/settings.json", cfg)
