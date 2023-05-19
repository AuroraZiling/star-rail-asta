import logging

from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout

from qfluentwidgets import HyperlinkCard, isDarkTheme, TextEdit

from ..Scripts.UI import custom_icon
from ..Scripts.UI.style_sheet import StyleSheet
from ..Scripts.Utils import tools

utils = tools.Tools()


class AboutWidget(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.aboutVBox = QVBoxLayout(self)

        self.aboutTopHBox = QHBoxLayout(self)

        self.aboutTopProjImage = QLabel("", self)
        self.aboutTopHBox.addWidget(self.aboutTopProjImage)

        self.aboutTopProjDesVBox = QVBoxLayout(self)
        self.aboutTopProjDesLabel = QLabel("Asta", self)
        self.aboutTopProjDesVersion = QLabel(f"{utils.app_version} for {utils.OS_name}", self)
        self.aboutTopProjDesLicense = QLabel("GPL v3.0", self)
        self.aboutTopProjDesGithub = QLabel("https://github.com/AuroraZiling/asta", self)
        self.aboutTopProjDesVBox.addWidget(self.aboutTopProjDesLabel)
        self.aboutTopProjDesVBox.addWidget(self.aboutTopProjDesVersion)
        self.aboutTopProjDesVBox.addWidget(self.aboutTopProjDesLicense)
        self.aboutTopProjDesVBox.addWidget(self.aboutTopProjDesGithub)
        self.aboutTopProjDesVBox.addStretch(1)
        self.aboutTopHBox.addLayout(self.aboutTopProjDesVBox)

        self.aboutTopUIImage = QLabel("", self)
        self.aboutTopHBox.addWidget(self.aboutTopUIImage)

        self.aboutTopUIDesVBox = QVBoxLayout(self)
        self.aboutTopUIDesDesignLabel = QLabel("UI Design", self)
        self.aboutTopUIDesLabel = QLabel("PyQt-Fluent-Widgets", self)
        self.aboutTopUIDesVersion = QLabel(f"{utils.ui_version} for PySide6", self)
        self.aboutTopUIDesGithub = QLabel("https://github.com/zhiyiYo/PyQt-Fluent-Widgets", self)
        self.aboutTopUIDesVBox.addWidget(self.aboutTopUIDesDesignLabel)
        self.aboutTopUIDesVBox.addWidget(self.aboutTopUIDesLabel)
        self.aboutTopUIDesVBox.addWidget(self.aboutTopUIDesVersion)
        self.aboutTopUIDesVBox.addWidget(self.aboutTopUIDesGithub)
        self.aboutTopUIDesVBox.addStretch(1)

        self.aboutTopHBox.addLayout(self.aboutTopUIDesVBox)
        self.aboutVBox.addLayout(self.aboutTopHBox)

        self.aboutOpenSourceVBox = QVBoxLayout(self)
        self.aboutOpenSourceLabel = QLabel("开放源代码许可", self)
        self.aboutOpenSourceTextEdit = TextEdit(self)
        self.aboutOpenSourceVBox.addWidget(self.aboutOpenSourceLabel)
        self.aboutOpenSourceVBox.addWidget(self.aboutOpenSourceTextEdit)
        self.aboutVBox.addLayout(self.aboutOpenSourceVBox)

        self.aboutFeedbackVBox = QVBoxLayout(self)
        self.aboutFeedbackLabel = QLabel("反馈", self)
        self.aboutFeedbackGithubIssueHyperlink = HyperlinkCard(
            url='https://github.com/AuroraZiling/asta/issues',
            text="提交",
            parent=self,
            icon=custom_icon.MyFluentIcon.GITHUB,
            title="Github Issue"
        )
        self.aboutFeedbackGithubPullRequestHyperlink = HyperlinkCard(
            url='https://github.com/AuroraZiling/asta/pulls',
            text="提交",
            parent=self,
            icon=custom_icon.MyFluentIcon.GITHUB,
            title="Github Pull Request"
        )
        self.aboutFeedbackVBox.addWidget(self.aboutFeedbackLabel)
        self.aboutFeedbackVBox.addWidget(self.aboutFeedbackGithubIssueHyperlink)
        self.aboutFeedbackVBox.addWidget(self.aboutFeedbackGithubPullRequestHyperlink)
        self.aboutVBox.addLayout(self.aboutFeedbackVBox)

        self.aboutVBox.addStretch(1)

        self.setObjectName("AboutFrame")
        self.initGrid()
        self.initFrame()
        StyleSheet.ABOUT_FRAME.apply(self)
        logging.info("[About] UI initialized")

    def initGrid(self):
        # Top
        self.aboutTopHBox.insertSpacing(0, 15)
        self.aboutTopHBox.insertSpacing(2, 10)
        self.aboutVBox.insertSpacing(0, 10)

    def initFrame(self):
        # Top
        # Top - Project Description
        self.aboutTopProjImage.move(60, 50)
        self.aboutTopProjImage.setFixedSize(128, 128)
        self.aboutTopProjImage.setPixmap(QtGui.QPixmap(f"{utils.working_dir}/assets/avatar_rounded.png"))
        self.aboutTopProjImage.setScaledContents(True)
        self.aboutTopProjDesLabel.setFont(utils.get_font(30))
        self.aboutTopProjDesVersion.setFont(utils.get_font(12))
        self.aboutTopProjDesLicense.setFont(utils.get_font(12))
        self.aboutTopProjDesGithub.setStyleSheet("color: grey;")
        self.aboutTopProjDesGithub.setFont(utils.get_font(8))
        # Top - UI Design
        self.aboutTopUIImage.setFixedSize(85, 85)
        self.aboutTopUIImage.setPixmap(QtGui.QPixmap(f"{utils.working_dir}/assets/pyqt-fluent-widgets-logo.png"))
        self.aboutTopUIImage.setScaledContents(True)
        self.aboutTopUIDesDesignLabel.setStyleSheet("margin-bottom: 0px;")
        self.aboutTopUIDesDesignLabel.setFont(utils.get_font(8))
        self.aboutTopUIDesLabel.setStyleSheet("margin-top: 0px;")
        self.aboutTopUIDesLabel.setFont(utils.get_font(20))
        self.aboutTopUIDesVersion.setFont(utils.get_font(10))
        self.aboutTopUIDesGithub.setStyleSheet("color: grey;")
        self.aboutTopUIDesGithub.setFont(utils.get_font(7))
        # Open Source
        self.aboutOpenSourceLabel.setFont(utils.get_font(16))
        self.aboutOpenSourceTextEdit.setMinimumHeight(240)
        if isDarkTheme():
            self.aboutOpenSourceTextEdit.setStyleSheet("background-color: #323232; color: white;")
        self.aboutOpenSourceTextEdit.setFont(utils.get_font(10))
        self.aboutOpenSourceTextEdit.setReadOnly(True)
        self.aboutOpenSourceTextEdit.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.aboutOpenSourceTextEdit.setPlainText(utils.open_source_license)
        # Feedback
        self.aboutFeedbackLabel.setFont(utils.get_font(16))
        self.aboutFeedbackGithubIssueHyperlink.setFont(utils.get_font(12))
        self.aboutFeedbackGithubPullRequestHyperlink.setFont(utils.get_font(12))
