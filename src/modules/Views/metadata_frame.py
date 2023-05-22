import logging

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from qfluentwidgets import SwitchSettingCard, PushSettingCard, InfoBar, InfoBarPosition, IndeterminateProgressBar
from qfluentwidgets import FluentIcon

from ..config import cfg
from .ViewFunctions.metadata_functions import MetadataUpdateThread, MetadataSRGFUpdateThread
from ..Scripts.Utils import tools
from ..Scripts.UI.style_sheet import StyleSheet

utils = tools.Tools()


class MetaDataWidget(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.baseVBox = QVBoxLayout(self)

        self.metaDataTitleLabel = QLabel("元数据", self)
        self.metaDataSubTitleLabel = QLabel("建议在大版本更新后更新", self)

        self.metaDataAutoUpdateLabel = QLabel("自动更新", self)

        self.metaDataAutoUpdateCard = SwitchSettingCard(
            FluentIcon.UPDATE,
            "启动时自动更新元数据",
            "",
            configItem=cfg.metaDataUpdateAtStartUp,
            parent=self
        )

        self.metaDataCharacterWeaponUpdateLabel = QLabel("更新", self)

        self.metaDataUpdateCard = PushSettingCard(
            "更新",
            FluentIcon.UPDATE,
            "更新元数据",
            "",
            parent=self
        )

        self.metaDataUpdateProgressBar = IndeterminateProgressBar(self)

        self.metaDataSRGFUpdateCard = PushSettingCard(
            "更新",
            FluentIcon.UPDATE,
            "更新SRGF API数据",
            "",
            parent=self
        )

        self.metaDataSRGFUpdateProgressBar = IndeterminateProgressBar(self)

        self.baseVBox.addWidget(self.metaDataTitleLabel)
        self.baseVBox.addWidget(self.metaDataSubTitleLabel)
        self.baseVBox.addWidget(self.metaDataAutoUpdateLabel)
        self.baseVBox.addWidget(self.metaDataAutoUpdateCard)
        self.baseVBox.addWidget(self.metaDataCharacterWeaponUpdateLabel)
        self.baseVBox.addWidget(self.metaDataUpdateCard)
        self.baseVBox.addWidget(self.metaDataUpdateProgressBar)
        self.baseVBox.addWidget(self.metaDataSRGFUpdateCard)
        self.baseVBox.addWidget(self.metaDataSRGFUpdateProgressBar)
        self.baseVBox.addStretch(1)

        self.setObjectName("MetaDataWidget")
        self.initFrame()
        StyleSheet.METADATA_FRAME.apply(self)

        logging.info("[Settings] All cache files deleted")

    def closeEvent(self, event):
        self.metaDataUpdateThread.exit()
        self.metaDataSRGFUpdateThread.exit()
        event.accept()

    def __metaDataUpdateCardSignal(self, status):
        if status:
            self.metaDataUpdateCard.setEnabled(True)
            self.metaDataUpdateProgressBar.setVisible(False)
            InfoBar.success("成功", "元数据已更新", position=InfoBarPosition.TOP_RIGHT, parent=self)
            logging.info(f"[Metadata] Character and weapon metadata updated")

    def __metaDataUpdateCardClicked(self):
        self.metaDataUpdateCard.setEnabled(False)
        self.metaDataUpdateProgressBar.setVisible(True)
        self.metaDataUpdateThread = MetadataUpdateThread()
        self.metaDataUpdateThread.start()
        self.metaDataUpdateThread.trigger.connect(self.__metaDataUpdateCardSignal)

    def __metaDataSRGFUpdateCardSignal(self, status):
        message = "SRGF API 数据已更新" if status else "SRGF API 数据无需更新"
        self.metaDataSRGFUpdateCard.setEnabled(True)
        self.metaDataSRGFUpdateProgressBar.setVisible(False)
        InfoBar.success("成功", message, position=InfoBarPosition.TOP_RIGHT, parent=self)
        logging.info(f"[Metadata] SRGF metadata updated")

    def __metaDataSRGFUpdateCardClicked(self):
        self.metaDataSRGFUpdateCard.setEnabled(False)
        self.metaDataSRGFUpdateProgressBar.setVisible(True)
        self.metaDataSRGFUpdateThread = MetadataSRGFUpdateThread()
        self.metaDataSRGFUpdateThread.start()
        self.metaDataSRGFUpdateThread.trigger.connect(self.__metaDataSRGFUpdateCardSignal)

    def initFrame(self):
        self.metaDataTitleLabel.setObjectName("metaDataTitleLabel")
        self.metaDataSubTitleLabel.setObjectName("metaDataSubTitleLabel")
        self.metaDataAutoUpdateLabel.setFont(utils.get_font(18))
        self.metaDataCharacterWeaponUpdateLabel.setFont(utils.get_font(18))

        self.metaDataUpdateProgressBar.setVisible(False)
        self.metaDataSRGFUpdateProgressBar.setVisible(False)

        self.metaDataUpdateCard.clicked.connect(self.__metaDataUpdateCardClicked)

        self.metaDataSRGFUpdateCard.clicked.connect(self.__metaDataSRGFUpdateCardClicked)

        if cfg.metaDataUpdateAtStartUp.value:
            self.__metaDataUpdateCardClicked()
            self.__metaDataSRGFUpdateCardClicked()
