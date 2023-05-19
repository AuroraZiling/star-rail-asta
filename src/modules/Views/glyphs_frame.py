from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout

from qfluentwidgets import TextEdit, PushButton, FluentIcon, ComboBox
from ..Scripts.UI.style_sheet import StyleSheet
from ..Scripts.Utils import tools
from ..constant import FONT_MAPPING, FONT_NAME_MAPPING

utils = tools.Tools()


class GlyphsWidget(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        for eachFont in FONT_MAPPING:
            QFontDatabase.addApplicationFont(f"{utils.working_dir}/assets/Hoyo-Glyphs/{eachFont}")

        self.currentFont = FONT_MAPPING[0]

        self.glyphsVBox = QVBoxLayout(self)

        self.glyphsTitleHBox = QHBoxLayout(self)
        self.glyphsTitleLabel = QLabel("崩坏：星穹铁道 架空文字", self)
        self.glyphsTranslateTypeComboBox = ComboBox(self)
        self.glyphsTitleResetBtn = PushButton("清空", self, FluentIcon.DELETE)
        self.glyphsTitleHBox.addWidget(self.glyphsTitleLabel)
        self.glyphsTitleHBox.addWidget(self.glyphsTranslateTypeComboBox)
        self.glyphsTitleHBox.addWidget(self.glyphsTitleResetBtn)
        self.glyphsVBox.addLayout(self.glyphsTitleHBox)

        self.glyphsSubTitleLabel = QLabel("Powered by Hoyo-Glyphs", self)

        self.glyphsVBox.addWidget(self.glyphsSubTitleLabel)

        self.glyphsTextGridBox = QGridLayout(self)

        self.glyphsTextOriginalLabel = QLabel("源文本", self)
        self.glyphsTextOriginalTextEdit = TextEdit(self)
        self.glyphsTextTranslatedLabel = QLabel("转换后", self)
        self.glyphsTextTranslatedTextEdit = TextEdit(self)

        self.glyphsTextGridBox.addWidget(self.glyphsTextOriginalLabel, 0, 0)
        self.glyphsTextGridBox.addWidget(self.glyphsTextOriginalTextEdit, 1, 0)
        self.glyphsTextGridBox.addWidget(self.glyphsTextTranslatedLabel, 0, 1)
        self.glyphsTextGridBox.addWidget(self.glyphsTextTranslatedTextEdit, 1, 1)

        self.glyphsVBox.addLayout(self.glyphsTextGridBox)

        self.glyphsGithubLabel = QLabel("https://github.com/SpeedyOrc-C/Hoyo-Glyphs", self)
        self.glyphsVBox.addWidget(self.glyphsGithubLabel)

        self.setObjectName("GlyphsFrame")
        StyleSheet.GLYPHS_FRAME.apply(self)
        self.initFrame()

    def __glyphsTitleResetBtnClicked(self):
        self.glyphsTextOriginalTextEdit.setText("")
        self.glyphsTextTranslatedTextEdit.setText("")

    def __glyphsTranslateTypeComboBoxChanged(self):
        self.currentFont = FONT_MAPPING[self.glyphsTranslateTypeComboBox.currentIndex()]
        self.glyphsTextTranslatedTextEdit.setFontFamily(FONT_NAME_MAPPING[self.glyphsTranslateTypeComboBox.currentIndex()])
        self.__glyphsTextOriginalTextEditChanged()

    def __glyphsTextOriginalTextEditChanged(self):
        self.glyphsTextTranslatedTextEdit.setText(self.glyphsTextOriginalTextEdit.toPlainText())

    def initFrame(self):
        self.glyphsTitleLabel.setObjectName("glyphsTitleLabel")
        self.glyphsSubTitleLabel.setObjectName("glyphsSubTitleLabel")
        self.glyphsTextOriginalLabel.setObjectName("glyphsTextOriginalLabel")
        self.glyphsTextTranslatedLabel.setObjectName("glyphsTextTranslatedLabel")

        self.glyphsTranslateTypeComboBox.addItems(
            ["Sans-Regular", "Serif-Regular"])
        self.glyphsTranslateTypeComboBox.setCurrentIndex(0)
        self.glyphsTranslateTypeComboBox.setFixedWidth(300)
        self.glyphsTitleResetBtn.setFixedWidth(100)
        self.glyphsTranslateTypeComboBox.currentIndexChanged.connect(self.__glyphsTranslateTypeComboBoxChanged)
        self.glyphsTitleResetBtn.clicked.connect(self.__glyphsTitleResetBtnClicked)

        self.glyphsTextOriginalTextEdit.textChanged.connect(self.__glyphsTextOriginalTextEditChanged)
        self.glyphsTextTranslatedTextEdit.setReadOnly(True)
        self.glyphsTextTranslatedTextEdit.setFontFamily(FONT_NAME_MAPPING[0])
        self.glyphsTextTranslatedTextEdit.setFontPointSize(24)
