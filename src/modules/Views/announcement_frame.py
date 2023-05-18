import webbrowser

from PySide6 import QtGui
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy

from qfluentwidgets import PrimaryPushButton, FluentIcon, InfoBar, PushButton, InfoBarPosition, isDarkTheme, ListWidget

from ..Scripts.UI.style_sheet import StyleSheet
from ..Scripts.Utils import downloader, log_recorder as log
from ..Scripts.Utils.config_utils import ConfigUtils
from .ViewFunctions import announcementFunctions
from ..constant import ANNOUNCE_REQUEST_URL, ANNOUNCE_ICON_REQUEST_URL

utils = ConfigUtils()


class AnnouncementWidget(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        if not (utils.jsonValidator(f"{utils.workingDir}/cache/announce.json") or utils.jsonValidator(f"{utils.workingDir}/cache/announce_icons.json")):
            log.infoWrite("[Announcement] Get announce.json")
            downloader.downloadFromJson(ANNOUNCE_REQUEST_URL, utils.workingDir + "/cache/", "announce.json")
            log.infoWrite("[Announcement] Get announce_icon.json")
            downloader.downloadFromJson(ANNOUNCE_ICON_REQUEST_URL, utils.workingDir + "/cache/",
                                        "announce_icons.json")

        self.baseVBox = QVBoxLayout(self)

        self.announceData = utils.getAnnounceData()
        self.announceIconData = utils.getAnnounceIconData()
        self.currentAnnounceHTMLPath = ""

        self.headerHBox = QHBoxLayout(self)

        self.headerLeftVBox = QVBoxLayout(self)
        self.headerLeftAnnounceTitleLabel = QLabel(self)
        self.headerLeftContentTitleLabel = QLabel(self)
        self.headerLeftVBox.addWidget(self.headerLeftAnnounceTitleLabel)
        self.headerLeftVBox.addWidget(self.headerLeftContentTitleLabel)

        self.headerHBox.addLayout(self.headerLeftVBox)
        self.headerHBox.addStretch(1)

        self.headerRightVBox = QVBoxLayout(self)
        self.headerRightRefreshBtn = PrimaryPushButton("刷新", self, FluentIcon.SYNC)
        self.headerRightAnnounceDateLabel = QLabel(self)
        self.headerRightVBox.addSpacing(3)
        self.headerRightVBox.addWidget(self.headerRightRefreshBtn, 0, Qt.AlignmentFlag.AlignRight)
        self.headerRightVBox.addWidget(self.headerRightAnnounceDateLabel, 0, Qt.AlignmentFlag.AlignRight)

        self.headerHBox.addLayout(self.headerRightVBox)
        self.headerHBox.addSpacing(5)
        self.baseVBox.addLayout(self.headerHBox)

        self.announceHBox = QHBoxLayout(self)

        self.announceListBox = ListWidget(self)
        self.announceHBox.addWidget(self.announceListBox)

        self.contentVBox = QVBoxLayout(self)
        self.contentBanner = QLabel(self)
        self.contentNoBanner = QLabel("此公告没有封面", self)
        self.contentHTMLBtn = PushButton(self)
        self.contentVBox.addWidget(self.contentBanner)
        self.contentVBox.addStretch(1)
        self.contentVBox.addWidget(self.contentNoBanner)
        self.contentVBox.addStretch(1)
        self.contentVBox.addWidget(self.contentHTMLBtn)
        self.announceHBox.addLayout(self.contentVBox)

        self.baseVBox.addLayout(self.announceHBox)

        log.infoWrite(f"[Announcement] UI Initialized")

        self.announceFunc = announcementFunctions.AnnouncementFunctions(self.announceData, self.announceIconData)
        self.initAnnounce()

        self.setObjectName("AnnouncementFrame")
        StyleSheet.ANNOUNCEMENT_FRAME.apply(self)

        self.initFrame()

    def initFrame(self):
        # Top - Left
        self.headerLeftAnnounceTitleLabel.setText("公告")
        self.headerLeftAnnounceTitleLabel.setFont(utils.getFont(18))
        self.headerLeftContentTitleLabel.setText("尚未选择公告")
        self.headerLeftContentTitleLabel.setFont(utils.getFont(10))
        # Top - Right
        self.headerRightRefreshBtn.setFixedWidth(100)
        self.headerRightAnnounceDateLabel.setText("于" + utils.getFileDate(f"{utils.workingDir}/cache/announce.json") + "更新")
        self.headerRightAnnounceDateLabel.setFont(utils.getFont(10))
        # List
        self.announceListBox.resize(200, 200)
        self.announceListBox.setFrameShape(QFrame.Shape.NoFrame)
        self.announceListBox.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.announceListBox.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.announceListBox.currentItemChanged.connect(self.__announceListBoxItemChanged)
        self.announceListBox.setCurrentRow(0)
        # Content
        self.contentBanner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentBanner.setMaximumWidth(750)
        self.contentBanner.setScaledContents(True)
        self.contentNoBanner.setFont(utils.getFont(24))
        self.contentNoBanner.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.contentNoBanner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentHTMLBtn.setText("详情")
        self.contentHTMLBtn.setFixedSize(750, 30)
        self.contentHTMLBtn.clicked.connect(self.openAnnounce)
        # Refresh
        self.headerRightRefreshBtn.clicked.connect(self.refreshAnnounce)

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        if isDarkTheme():
            self.announceListBox.setStyleSheet("background-color: rgb(39, 39, 39); color: white;")

    def __announceListBoxItemChanged(self):
        currentAnnounceData = self.announceFunc.getCurrentAnnounce(self.announceListBox.currentIndex().row())
        log.infoWrite(f"[Announcement] Announcement changed: {currentAnnounceData['bigTitle']}")
        self.headerLeftContentTitleLabel.setText(currentAnnounceData["bigTitle"])
        self.contentBanner.hide()
        if currentAnnounceData["banner"]:
            self.contentBanner.show()
            self.contentNoBanner.hide()
            self.contentBanner.setPixmap(currentAnnounceData["banner"])
            self.contentBanner.setFixedHeight(currentAnnounceData["bannerHeight"])
        else:
            self.contentNoBanner.show()
        self.currentAnnounceHTMLPath = currentAnnounceData["contentHtml"]

    def initAnnounce(self):
        self.announceFunc.getIcons()
        self.headerRightAnnounceDateLabel.setText("于" + utils.getFileDate(f"{utils.workingDir}/cache/announce.json") + "更新")
        for index, item in enumerate(self.announceFunc.getItems()):
            self.announceListBox.addItem(item)
            self.announceListBox.item(index).setSizeHint(QSize(300, 30))
        log.infoWrite(f"[Announcement] Announcement initialized")
        self.__announceListBoxItemChanged()

    def refreshAnnounce(self):
        self.announceListBox.clear()
        downloader.downloadFromJson(ANNOUNCE_REQUEST_URL, utils.workingDir + "/cache/", "announce.json")
        downloader.downloadFromJson(ANNOUNCE_ICON_REQUEST_URL, utils.workingDir + "/cache/",
                                    "announce_icons.json")
        self.announceData = utils.getAnnounceData()
        self.announceIconData = utils.getAnnounceIconData()
        self.initAnnounce()
        log.infoWrite("[Announcement] Announcement updated")
        InfoBar.success("成功", "公告已更新", position=InfoBarPosition.TOP, parent=self)

    def openAnnounce(self):
        webbrowser.open(f"{utils.workingDir}/cache/{self.announceListBox.currentRow()}.html")
        log.infoWrite(f"[Announcement] Announcement opened at row:{self.announceListBox.currentRow()}")