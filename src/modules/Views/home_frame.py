import logging

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout

from qfluentwidgets import PrimaryPushButton, FluentIcon, TextEdit

from .ViewFunctions.home_functions import HomeSoftwareAnnouncementThread, HomeCurrentUPThread
from ..Scripts.UI.style_sheet import StyleSheet
from ..Scripts.Utils import tools

utils = tools.Tools()


class HomeWidget(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.homeCurrentUPThread = None
        self.homeSoftwareAnnouncementThread = None

        self.baseVBox = QVBoxLayout(self)

        self.topHBox = QHBoxLayout(self)

        self.topTitleLabel = QLabel("Asta", self)
        self.topRefreshBtn = PrimaryPushButton("刷新", self, FluentIcon.SYNC)

        self.topHBox.addWidget(self.topTitleLabel)
        self.topHBox.addWidget(self.topRefreshBtn)
        self.baseVBox.addLayout(self.topHBox)

        self.currentUPTitleLabel = QLabel("当期UP信息", self)

        self.currentUP1Box = QHBoxLayout(self)
        self.currentUP1RightBox = QVBoxLayout(self)
        self.currentUP1IconLabel = QLabel(self)
        self.currentUP1Box.addWidget(self.currentUP1IconLabel)
        self.currentUP1CharacterLabel = QLabel("暂无", self)
        self.currentUP1TimeLabel = QLabel("未知", self)
        self.currentUP1RightBox.addWidget(self.currentUP1CharacterLabel)
        self.currentUP1RightBox.addWidget(self.currentUP1TimeLabel)
        self.currentUP1Box.addLayout(self.currentUP1RightBox)

        self.currentUPWeaponLabel = QLabel("暂无", self)

        self.announceTitleLabel = QLabel("公告", self)
        self.announceTextBox = TextEdit(self)

        self.baseVBox.addWidget(self.currentUPTitleLabel)
        self.baseVBox.addLayout(self.currentUP1Box)
        self.baseVBox.addWidget(self.currentUPWeaponLabel)
        self.baseVBox.addWidget(self.announceTitleLabel)
        self.baseVBox.addWidget(self.announceTextBox)

        self.setObjectName("HomeFrame")
        StyleSheet.HOME_FRAME.apply(self)

        self.initFrame()
        self.getCurrentUPFromMetaData()
        self.getAnnouncementFromMetaData()

        logging.info("[Home] UI Initialized")

    def closeEvent(self, event):
        self.homeCurrentUPThread.exit()
        self.homeSoftwareAnnouncementThread.exit()
        event.accept()

    def __topRefreshBtnClicked(self):
        if self.homeCurrentUPThread.isRunning() or self.homeSoftwareAnnouncementThread.isRunning():
            return
        self.getAnnouncementFromMetaData()
        self.getCurrentUPFromMetaData()

    def initFrame(self):
        self.topTitleLabel.setObjectName("homeFrameTitle")
        self.topRefreshBtn.setFixedWidth(100)
        self.topRefreshBtn.clicked.connect(self.__topRefreshBtnClicked)

        self.currentUPTitleLabel.setObjectName("currentUPTitleLabel")
        self.currentUP1IconLabel.setObjectName("currentUP1IconLabel")
        self.currentUP1IconLabel.setFixedSize(79, 64)
        self.currentUP1IconLabel.setScaledContents(True)
        self.currentUP1CharacterLabel.setObjectName("currentUP1CharacterLabel")
        self.currentUP1TimeLabel.setObjectName("currentUP1TimeLabel")

        self.currentUPWeaponLabel.setObjectName("currentUPWeaponLabel")

        self.announceTitleLabel.setObjectName("homeFrameAnnounceTitle")
        self.announceTextBox.setObjectName("homeFrameAnnounce")
        self.announceTextBox.setReadOnly(True)
        self.announceTextBox.setFrameShape(QFrame.Shape.NoFrame)
        self.announceTextBox.setContentsMargins(5, 5, 5, 5)

    def __getCurrentUPFromMetaDataSignal(self, upType, upPool, info, timePeriod, iconPath):
        if upType == 0 and upPool == 0:
            self.currentUP1CharacterLabel.setText(info)
            self.currentUP1TimeLabel.setText(timePeriod)
            self.currentUP1IconLabel.setPixmap(QPixmap(iconPath))
        elif upType == 1:
            self.currentUPWeaponLabel.setText(info)

    def getCurrentUPFromMetaData(self):
        self.homeCurrentUPThread = HomeCurrentUPThread()
        self.homeCurrentUPThread.start()
        self.homeCurrentUPThread.trigger.connect(self.__getCurrentUPFromMetaDataSignal)
        logging.info("[Home] Current UP Get")

    def __getAnnouncementFromMetaDataSignal(self, info):
        self.announceTextBox.setText(info)

    def getAnnouncementFromMetaData(self):
        self.homeSoftwareAnnouncementThread = HomeSoftwareAnnouncementThread()
        self.homeSoftwareAnnouncementThread.start()
        self.homeSoftwareAnnouncementThread.trigger.connect(self.__getAnnouncementFromMetaDataSignal)
        logging.info("[Home] Announcement Get")
