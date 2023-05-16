from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout

from qfluentwidgets import PrimaryPushButton, FluentIcon, TextEdit

from .ViewFunctions.homeFunctions import HomeSoftwareAnnouncementThread
from ..Scripts.UI.style_sheet import StyleSheet
from ..Scripts.Utils import config_utils, log_recorder as log

utils = config_utils.ConfigUtils()


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

        self.announceTitleLabel = QLabel("公告", self)
        self.announceTextBox = TextEdit(self)

        self.baseVBox.addWidget(self.announceTitleLabel)
        self.baseVBox.addWidget(self.announceTextBox)

        self.setObjectName("HomeFrame")
        StyleSheet.HOME_FRAME.apply(self)

        self.initFrame()
        self.getAnnouncementFromMetaData()

        log.infoWrite("[Home] UI Initialized")

    def closeEvent(self, event):
        self.homeCurrentUPThread.exit()
        self.homeSoftwareAnnouncementThread.exit()
        event.accept()

    def __topRefreshBtnClicked(self):
        if self.homeSoftwareAnnouncementThread.isRunning():
            return
        self.getAnnouncementFromMetaData()

    def initFrame(self):
        self.topTitleLabel.setObjectName("homeFrameTitle")
        self.topRefreshBtn.setFixedWidth(100)
        self.topRefreshBtn.clicked.connect(self.__topRefreshBtnClicked)

        self.announceTitleLabel.setObjectName("homeFrameAnnounceTitle")
        self.announceTextBox.setObjectName("homeFrameAnnounce")
        self.announceTextBox.setReadOnly(True)
        self.announceTextBox.setFrameShape(QFrame.Shape.NoFrame)
        self.announceTextBox.setContentsMargins(5, 5, 5, 5)

    def __getAnnouncementFromMetaDataSignal(self, info):
        self.announceTextBox.setText(info)

    def getAnnouncementFromMetaData(self):
        self.homeSoftwareAnnouncementThread = HomeSoftwareAnnouncementThread()
        self.homeSoftwareAnnouncementThread.start()
        self.homeSoftwareAnnouncementThread.trigger.connect(self.__getAnnouncementFromMetaDataSignal)
        log.infoWrite("[Home] Announcement Get")
