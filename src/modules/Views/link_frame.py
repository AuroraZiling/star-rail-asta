# coding:utf-8
import json
import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QLabel, QFileDialog

from qfluentwidgets import SettingCardGroup, PushSettingCard, ScrollArea, ExpandLayout, MessageBox, HyperlinkCard
from qfluentwidgets import FluentIcon

from ..Core.GachaReport import gacha_report_read
from ..Scripts.UI import custom_msgBox, custom_dialog
from ..Scripts.UI.style_sheet import StyleSheet
from ..Scripts.Utils import tools
from ..Core.SRGF.import_support import ImportSupport
from ..Core.SRGF.export_support import ExportSupport

utils = tools.Tools()


class LinkWidget(ScrollArea):
    checkUpdateSig = Signal()

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.linkLabel = QLabel("SRGF 导入和导出", self)

        # Import
        self.importGroup = SettingCardGroup("导入", self.scrollWidget)
        self.importCard = PushSettingCard(
            "浏览",
            FluentIcon.EMBED,
            "导入 SRGF(Json) 文件",
            "目前支持的标准: Star Rail GachaLog Format standard (SRGF) v1.0",
            self.importGroup
        )

        # Export
        self.exportGroup = SettingCardGroup("导出", self.scrollWidget)
        self.exportCard = PushSettingCard(
            "浏览",
            FluentIcon.SHARE,
            "导出 SRGF(Json) 文件",
            "目前支持的标准: Star Rail GachaLog Format standard (SRGF) v1.0",
            self.exportGroup
        )

        # AboutSRGF
        self.srgfGroup = SettingCardGroup("关于 SRGF", self.scrollWidget)
        self.srgfCard = HyperlinkCard(
            f"https://srgf.org/zh/",
            "打开 SRGF 官网",
            FluentIcon.HELP,
            "什么是SRGF?",
            "Unified Standardized GenshinData Format",
            self.srgfGroup
        )

        self.setObjectName("LinkFrame")
        self.__initWidget()

        logging.info(f"[Link] UI Initialized")

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
        self.linkLabel.move(60, 63)

        # Import
        self.importGroup.addSettingCard(self.importCard)

        # Export
        self.exportGroup.addSettingCard(self.exportCard)

        # About SRGF
        self.srgfGroup.addSettingCard(self.srgfCard)

        # Add Cards
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.importGroup)
        self.expandLayout.addWidget(self.exportGroup)
        self.expandLayout.addWidget(self.srgfGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.linkLabel.setObjectName('linkLabel')

        StyleSheet.LINK_FRAME.apply(self)

    def __showMessageBox(self, title, content):
        MessageBox(title, content, self).exec()

    def __showTextEditMessageBox(self, title, content, text):
        custom_msgBox.TextEditMsgBox(title, content, text, self).exec()

    def __importCardClicked(self):
        filePath = QFileDialog.getOpenFileName(self, "打开 SRGF(Json) 文件", "./", "SRGF(json) File (*.json)")[0]
        logging.info(f"[Link][Import] Get SRGF File: {filePath}")
        if utils.json_validator(filePath, "srgf"):
            logging.info(f"[Sangonomiya][Link] SRGF Import File Path: {filePath}")
            importFile = json.loads(open(filePath, 'r', encoding="utf-8").read())
            tmp_uid = importFile["info"]["uid"]
            tmp_language = importFile["info"]["lang"]
            tmp_export_time = importFile["info"].get("export_time", "Unknown")
            tmp_export_application = importFile["info"]["export_app"]
            tmp_application_version = importFile["info"]["export_app_version"]
            tmp_time_region_zome = importFile["info"]["region_time_zone"]
            alertMessage = f'''UID: {tmp_uid}
语言: {tmp_language}
导出时间: {tmp_export_time}  
导出应用: {tmp_export_application}
导出应用版本: {tmp_application_version}
时区: {tmp_time_region_zome}'''
            self.__showTextEditMessageBox("验证", "请验证如下信息:", alertMessage)
            importSupport = ImportSupport(tmp_uid, tmp_language, tmp_export_time)
            importSupport.SRGFSave(importFile)
            logging.info(f"[Link][Import] Imported ({tmp_uid} from {tmp_export_application})")

    def __exportCardReturnSignal(self, uid):
        filePath = QFileDialog.getSaveFileName(self, "保存 SRGF(Json) 文件", f"./{uid}_export_data.json",
                                               "SRGF(json) File (*.json)")[0]
        exportSupport = ExportSupport(uid)
        exportSupport.SRGFSave(filePath)
        logging.info(f"[Link][Export] Exported ({uid} to {filePath})")

    def __exportCardClicked(self):
        w = custom_dialog.ComboboxDialog("导出", "选择需要导出的UID", gacha_report_read.getUIDList(), self)
        w.returnSignal.connect(self.__exportCardReturnSignal)
        w.exec()

    def __connectSignalToSlot(self):
        self.importCard.clicked.connect(self.__importCardClicked)
        self.exportCard.clicked.connect(self.__exportCardClicked)
