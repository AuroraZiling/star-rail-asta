# coding:utf-8
import logging
import sys
import ctypes
import time
import traceback
import datetime

import win32api
import win32con
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QStackedWidget, QHBoxLayout

from qfluentwidgets import FluentIcon, NavigationInterface, NavigationItemPosition, \
    InfoBar, InfoBarPosition
from qframelesswindow import FramelessWindow

from modules.Scripts.Utils.file_verification import assetsCheck
from modules.Views import home_frame, gacha_report_frame, link_frame, \
    settings_frame, about_frame, metadata_frame, glyphs_frame, announcement_frame
from modules.Scripts.UI import custom_icon
from modules.Scripts.UI.title_bar import CustomTitleBar
from modules.Scripts.UI.style_sheet import StyleSheet
from modules.Scripts.Utils import tools
from modules.Metadata import character_list
from modules.config import cfg

utils = tools.Tools()

if sys.platform.startswith("win32"):
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

logging.info("-----===== Asta Log =====-----")
logging.info(f"Time: {time.strftime('%Y.%m.%d %H:%M:%S', time.localtime())}")
logging.info(f"OS Platform: {sys.platform}")
logging.info(f"Version: {utils.app_version}")
logging.info(f"Python Version: {sys.version}")
logging.info(f"Working Directory: {utils.working_dir}")
logging.info("-----===== Start Tracking =====-----")


def startUp():
    assetsCheck()
    if cfg.customizeAutoDeleteLog and utils.get_log_file_amount() > 3:
        utils.delete_directory(utils.log_dir)


class GlobalExceptHookHandler(object):
    def __init__(self, logFile):
        self.__logFile = logFile
        sys.excepthook = self.__HandleException

    @staticmethod
    def __HandleException(excType, excValue, tb):
        try:
            currentTime = datetime.datetime.now()
            logging.info("\n\n---===Oops! Asta Crushed===---")
            logging.info('Timestamp: %s' % (currentTime.strftime("%Y-%m-%d %H:%M:%S")))
            logging.error("Uncaught exception：", exc_info=(excType, excValue, tb))
            logging.info('\n\n')
        except:
            pass

        sys.__excepthook__(excType, excValue, tb)

        err_msg = ''.join(traceback.format_exception(excType, excValue, tb))
        err_msg += '\n Asta 发生了不可预料的崩溃，请查看日志内容并反馈'
        win32api.MessageBox(0, err_msg, "Error", win32con.MB_OK)


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()

        self.initMetaData()

        self.setTitleBar(CustomTitleBar(self))
        self.setWindowFlags(Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint)

        self.mainHBoxLayout = QHBoxLayout(self)
        self.mainNavigationInterface = NavigationInterface(self, showMenuButton=True)
        self.mainStackWidget = QStackedWidget(self)

        self.mainHomeInterface = home_frame.HomeWidget(self)
        self.mainGachaReportInterface = gacha_report_frame.GachaReportWidget(self)
        self.mainLinkInterface = link_frame.LinkWidget(self)
        self.mainAnnouncementInterface = announcement_frame.AnnouncementWidget(self)
        self.mainGlyphsInterface = glyphs_frame.GlyphsWidget(self)
        self.mainMetaDataInterface = metadata_frame.MetaDataWidget(self)
        self.mainSettingInterface = settings_frame.SettingWidget(self)
        self.mainAboutInterface = about_frame.AboutWidget(self)

        self.mainStackWidget.addWidget(self.mainHomeInterface)
        self.mainStackWidget.addWidget(self.mainGachaReportInterface)
        self.mainStackWidget.addWidget(self.mainLinkInterface)
        self.mainStackWidget.addWidget(self.mainAnnouncementInterface)
        self.mainStackWidget.addWidget(self.mainGlyphsInterface)
        self.mainStackWidget.addWidget(self.mainMetaDataInterface)
        self.mainStackWidget.addWidget(self.mainSettingInterface)
        self.mainStackWidget.addWidget(self.mainAboutInterface)

        self.initLayout()
        self.initNavigation()
        self.initWindow()
        startUp()
        logging.info("[Main] UI Initialized")

    def initMetaData(self):
        if not utils.read_metadata("permanent"):
            characterData = character_list.getPermanentCharacter()
            utils.update_metadata("permanent", characterData)
            logging.info("[MetaData] 常驻角色元数据列表已更新")
            InfoBar.success("成功", "常驻角色元数据列表已更新", position=InfoBarPosition.BOTTOM_RIGHT, parent=self)

    def initLayout(self):
        self.mainHBoxLayout.setSpacing(0)
        self.mainHBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.mainHBoxLayout.addWidget(self.mainNavigationInterface)
        self.mainHBoxLayout.addWidget(self.mainStackWidget)
        self.mainHBoxLayout.setStretchFactor(self.mainStackWidget, 1)

    def initNavigation(self):
        self.mainNavigationInterface.addItem(
            routeKey=self.mainHomeInterface.objectName(),
            icon=FluentIcon.HOME,
            text="主页",
            onClick=lambda: self.switchTo(self.mainHomeInterface)
        )

        self.mainNavigationInterface.addItem(
            routeKey=self.mainGachaReportInterface.objectName(),
            icon=custom_icon.MyFluentIcon.GACHA_REPORT,
            text="跃迁记录",
            onClick=lambda: self.switchTo(self.mainGachaReportInterface)
        )
        self.mainNavigationInterface.addItem(
            routeKey=self.mainLinkInterface.objectName(),
            icon=custom_icon.MyFluentIcon.DATA,
            text="SRGF",
            onClick=lambda: self.switchTo(self.mainLinkInterface)
        )

        self.mainNavigationInterface.addItem(
            routeKey=self.mainAnnouncementInterface.objectName(),
            icon=custom_icon.MyFluentIcon.ANNOUNCEMENT,
            text="公告",
            onClick=lambda: self.switchTo(self.mainAnnouncementInterface)
        )

        self.mainNavigationInterface.addSeparator()

        self.mainNavigationInterface.addItem(
            routeKey=self.mainGlyphsInterface.objectName(),
            icon=FluentIcon.FONT,
            text="架空文字 / Hoyo-Glyphs",
            onClick=lambda: self.switchTo(self.mainGlyphsInterface)
        )

        self.mainNavigationInterface.addSeparator()

        self.mainNavigationInterface.addItem(
            routeKey=self.mainMetaDataInterface.objectName(),
            icon=FluentIcon.CODE,
            text="元数据",
            onClick=lambda: self.switchTo(self.mainMetaDataInterface),
            position=NavigationItemPosition.BOTTOM
        )

        self.mainNavigationInterface.addItem(
            routeKey=self.mainSettingInterface.objectName(),
            icon=FluentIcon.SETTING,
            text="设置",
            onClick=lambda: self.switchTo(self.mainSettingInterface),
            position=NavigationItemPosition.BOTTOM
        )

        self.mainNavigationInterface.addItem(
            routeKey=self.mainAboutInterface.objectName(),
            icon=custom_icon.MyFluentIcon.ABOUT,
            text="关于",
            onClick=lambda: self.switchTo(self.mainAboutInterface),
            position=NavigationItemPosition.BOTTOM
        )
        self.mainNavigationInterface.setExpandWidth(220)
        self.mainStackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.onCurrentInterfaceChanged(0)

    def initWindow(self):
        self.setFixedSize(1300, 700)
        self.setWindowTitle('Asta')
        self.setWindowIcon(QIcon(f'{utils.working_dir}/assets/avatar.png'))
        self.titleBar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        StyleSheet.MAIN_WINDOW.apply(self)

    def switchTo(self, widget):
        self.mainStackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.mainStackWidget.widget(index)
        self.mainNavigationInterface.setCurrentItem(widget.objectName())
        logging.info(f"[Main] Current frame changed: {widget.objectName()}")


if __name__ == '__main__':
    logging.info("[Main] Asta is starting...")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(f"{utils.working_dir}/assets/avatar.png"))
    w = Window()
    w.show()
    GlobalExceptHookHandler(f"{utils.working_dir}/logs/error.log")
    app.exec()
    logging.info("[Main] Asta has been shutdown")
    logging.info("-----===== Stop Tracking =====-----")
