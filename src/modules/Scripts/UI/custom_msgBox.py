from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QColor

from qfluentwidgets import TextEdit
from qfluentwidgets.components.dialog_box.dialog import Ui_MessageBox
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase


class TextEditMsgBox(MaskDialogBase, Ui_MessageBox):
    """ Message box """

    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, title: str, content: str, text: str, parent=None, isReadOnly=True):
        super().__init__(parent=parent)
        self._setUpUi(title, content, self.widget)

        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 50))
        self.setMaskColor(QColor(0, 0, 0, 76))
        self._hBoxLayout.removeWidget(self.widget)
        self._hBoxLayout.addWidget(self.widget, 1, Qt.AlignmentFlag.AlignCenter)

        self.textEditWidget = TextEdit(self)
        self.textEditWidget.setText(text)
        self.textEditWidget.setReadOnly(isReadOnly)
        self.textEditWidget.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.textEditWidget.setFixedWidth(500)
        self.vBoxLayout.insertWidget(1, self.textEditWidget)

        self.buttonGroup.setMinimumWidth(280)
        self.widget.setFixedSize(500, 350)

    def eventFilter(self, obj, e: QEvent):
        if obj is self.window():
            if e.type() == QEvent.Type.Resize:
                self._adjustText()

        return super().eventFilter(obj, e)