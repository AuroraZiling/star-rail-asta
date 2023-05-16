# coding:utf-8
import webbrowser

from PySide6 import QtGui
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QLabel, QFileDialog

from qfluentwidgets import (SettingCardGroup, PushSettingCard, ScrollArea, ExpandLayout, isDarkTheme, Dialog,
                            OptionsSettingCard,
                            SwitchSettingCard, setTheme, InfoBar, MessageBox)
from qfluentwidgets import FluentIcon, InfoBarPosition, qconfig

from .ViewConfigs.config import cfg
from ..Core.GachaReport import gacha_report_read
from ..Core.GachaReport.gacha_report_utils import getDefaultGameDataPath
from ..Scripts.UI import custom_icon, custom_dialog
from ..Scripts.UI.style_sheet import StyleSheet
from ..Scripts.Utils import config_utils, log_recorder as log

utils = config_utils.ConfigUtils()


class SettingWidget(ScrollArea):
    checkUpdateSig = Signal()

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.settingLabel = QLabel("设置", self)

        self.configPath = utils.configPath

        # Game

        self.gameGroup = SettingCardGroup("游戏", self.scrollWidget)
        self.gameDataCard = PushSettingCard(
            "浏览",
            FluentIcon.FOLDER,
            "游戏文件夹",
            cfg.get(cfg.gameDataFolder),
            self.gameGroup
        )
        self.gameDataResetCard = PushSettingCard(
            "重置",
            FluentIcon.CLOSE,
            "刷新游戏目录位置",
            "如果你错误地选择了游戏目录，此处可重置",
            self.gameGroup
        )

        # Storage
        self.storageGroup = SettingCardGroup("存储", self.scrollWidget)
        self.storageDataCard = PushSettingCard(
            "打开",
            FluentIcon.FOLDER,
            "数据文件夹",
            cfg.get(cfg.storageDataFolders),
            self.storageGroup
        )
        self.storageCacheCard = PushSettingCard(
            "打开",
            FluentIcon.FOLDER,
            "缓存文件夹",
            cfg.get(cfg.storageCacheFolders),
            self.storageGroup
        )
        self.storageLogCard = PushSettingCard(
            "打开",
            FluentIcon.FOLDER,
            "日志文件夹",
            cfg.get(cfg.storageLogFolders),
            self.storageGroup
        )
        self.storageConfigCard = PushSettingCard(
            "打开",
            FluentIcon.FOLDER,
            "配置文件",
            self.configPath,
            self.storageGroup
        )

        # Default

        self.defaultGroup = SettingCardGroup("操作", self.scrollWidget)

        self.defaultUIDDeleteCard = PushSettingCard(
            "删除",
            custom_icon.MyFluentIcon.DELETE,
            "删除UID档案",
            "选择需要删除的UID数据",
            self.defaultGroup
        )

        self.defaultLogDeleteCard = PushSettingCard(
            "删除",
            custom_icon.MyFluentIcon.DELETE,
            "清空日志文件",
            f"{utils.workingDir + '/logs'} 文件夹内的日志将被清空",
            self.defaultGroup
        )

        self.defaultCacheDeleteCard = PushSettingCard(
            "删除",
            custom_icon.MyFluentIcon.DELETE,
            f"清空缓存文件 (约 {utils.getDirSize(utils.workingDir + '/cache')} MB)",
            f"存放在 {utils.workingDir + '/cache'} 的缓存文件将被删除",
            self.defaultGroup
        )

        # Customize
        self.customizeGroup = SettingCardGroup("个性化", self.scrollWidget)

        self.customizeThemeSetting = OptionsSettingCard(
            qconfig.themeMode,
            FluentIcon.BRUSH,
            "主题色",
            "改变应用的明暗主题",
            texts=[
                "白昼", "黑夜",
                "采用系统设置"
            ],
            parent=self.customizeGroup
        )

        self.customizeAutoDeleteLogSetting = SwitchSettingCard(
            FluentIcon.DELETE,
            "自动删除旧日志",
            "程序启动后，若旧日志存在三个及以上，则全部删除",
            configItem=cfg.customizeAutoDeleteLog,
            parent=self.customizeGroup
        )

        # Update
        self.updateSoftwareGroup = SettingCardGroup("软件更新", self.scrollWidget)

        self.updateCheckCard = PushSettingCard(
            "检查",
            FluentIcon.UPDATE,
            "寻找可用的更新",
            "",
            self.updateSoftwareGroup
        )

        self.__initWidget()
        self.setObjectName("SettingFrame")
        log.infoWrite("[Settings] UI Initialized")

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss()

        # initialize layout
        self.initLayout()
        self.__connectSignalToSlot()

    def initLayout(self):
        self.settingLabel.move(60, 63)

        # Game

        self.gameGroup.addSettingCard(self.gameDataCard)
        self.gameGroup.addSettingCard(self.gameDataResetCard)

        # Storage

        self.storageGroup.addSettingCard(self.storageDataCard)
        self.storageGroup.addSettingCard(self.storageCacheCard)
        self.storageGroup.addSettingCard(self.storageLogCard)
        self.storageGroup.addSettingCard(self.storageConfigCard)

        # Default

        self.defaultGroup.addSettingCard(self.defaultUIDDeleteCard)
        self.defaultGroup.addSettingCard(self.defaultLogDeleteCard)
        self.defaultGroup.addSettingCard(self.defaultCacheDeleteCard)

        # Customize

        self.customizeGroup.addSettingCard(self.customizeThemeSetting)
        self.customizeGroup.addSettingCard(self.customizeAutoDeleteLogSetting)

        # Update

        self.updateSoftwareGroup.addSettingCard(self.updateCheckCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.gameGroup)
        self.expandLayout.addWidget(self.storageGroup)
        self.expandLayout.addWidget(self.defaultGroup)
        self.expandLayout.addWidget(self.customizeGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        StyleSheet.SETTING_FRAME.apply(self)

    def __showMessageBox(self, title, content):
        Dialog(title, content, self).exec()

    def __gameDataCardClicked(self):
        folder = QFileDialog.getExistingDirectory(
            self, "选择崩坏：星穹铁道游戏目录", "./")
        if not folder or cfg.get(cfg.gameDataFolder) == folder:
            return

        cfg.set(cfg.gameDataFolder, folder)
        self.gameDataCard.setContent(folder)
        log.infoWrite(f"[Settings] Game path changed: {folder}")

    def __gameDataResetCardClicked(self):
        cfg.set(cfg.gameDataFolder, getDefaultGameDataPath())
        self.gameDataCard.setContent(getDefaultGameDataPath())
        log.infoWrite(f"[Settings] Game path reset")

    @staticmethod
    def __defaultUIDDeleteCardReturnSignal(uid):
        utils.deleteDir(f"{utils.workingDir}/data/{uid}/", False)

    def __defaultUIDDeleteCardClicked(self):
        w = custom_dialog.ComboboxDialog("删除UID数据档案", "选择UID", gacha_report_read.getUIDList(), self)
        w.returnSignal.connect(self.__defaultUIDDeleteCardReturnSignal)
        w.exec()

    def __defaultLogDeleteCardClicked(self):
        utils.deleteAllLogFiles()
        InfoBar.success("成功", "旧日志文件已清空", InfoBarPosition.TOP_RIGHT, parent=self.window())

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        self.__defaultCacheSizeUpdate()

    def __defaultCacheDeleteCardClicked(self):
        utils.deleteAllCacheFiles()
        self.__defaultCacheSizeUpdate()
        InfoBar.success("成功", "缓存已清空", InfoBarPosition.TOP_RIGHT, parent=self.window())

    def __defaultCacheSizeUpdate(self):
        self.defaultCacheDeleteCard.titleLabel.setText(
            f"清空缓存文件 (约 {utils.getDirSize(utils.workingDir + '/cache')} MB)")


    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(lambda: InfoBar.warning("警告", self.tr(
            "更改将在应用重启后更新"), parent=self.window(), position=InfoBarPosition.TOP_RIGHT))
        cfg.themeChanged.connect(setTheme)

        # Game
        self.gameDataCard.clicked.connect(self.__gameDataCardClicked)
        self.gameDataResetCard.clicked.connect(self.__gameDataResetCardClicked)

        # Storage
        self.storageDataCard.clicked.connect(lambda: utils.openFolder(cfg.get(cfg.storageDataFolders)))
        self.storageCacheCard.clicked.connect(lambda: utils.openFolder(cfg.get(cfg.storageCacheFolders)))
        self.storageLogCard.clicked.connect(lambda: utils.openFolder(cfg.get(cfg.storageLogFolders)))
        self.storageConfigCard.clicked.connect(lambda: utils.openFolder(self.configPath))

        # Default
        self.defaultUIDDeleteCard.clicked.connect(self.__defaultUIDDeleteCardClicked)
        self.defaultLogDeleteCard.clicked.connect(self.__defaultLogDeleteCardClicked)
        self.defaultCacheDeleteCard.clicked.connect(self.__defaultCacheDeleteCardClicked)
