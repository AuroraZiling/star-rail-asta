# coding:utf-8
import logging
import os
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

from qfluentwidgets import FluentIcon, NavigationInterface, NavigationItemPosition, setTheme, Theme, isDarkTheme, \
    InfoBar, InfoBarPosition
from qframelesswindow import FramelessWindow

from modules.Scripts.Utils.file_verification import assetsCheck

from modules.Views import home_frame, gacha_report_frame, link_frame, \
    settings_frame, about_frame, metadata_frame, glyphs_frame
from modules.Scripts.UI import custom_icon
from modules.Scripts.UI.title_bar import CustomTitleBar
from modules.Scripts.UI.style_sheet import StyleSheet
from modules.Scripts.Utils import file_verification, metadata_utils, config_utils, downloader, log_recorder as log
from modules.Metadata import character_list, weapon_list

utils = config_utils.ConfigUtils()

if sys.platform.startswith("win32"):
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

log.infoWrite("-----===== Asta Log =====-----")
log.infoWrite(f"Time: {time.strftime('%Y.%m.%d %H:%M:%S', time.localtime())}")
log.infoWrite(f"OS Platform: {sys.platform}")
log.infoWrite(f"Version: {utils.appVersion}")
log.infoWrite(f"Python Version: {sys.version}")
log.infoWrite(f"Working Directory: {utils.workingDir}")
log.infoWrite("-----===== Start Tracking =====-----")


def startUp():
    log.infoWrite("[Main] Running Assets Check")
    assetsCheck()
    if utils.getConfigAutoDeleteLog() and utils.getLogAmount() > 3:
        utils.deleteDir(utils.logDir)


class GlobalExceptHookHandler(object):
    def __init__(self, logFile):
        self.__logFile = logFile

        self.__logger = self.__BuildLogger()
        sys.excepthook = self.__HandleException

    def __BuildLogger(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.FileHandler(self.__logFile))
        return logger

    def __HandleException(self, excType, excValue, tb):
        try:
            currentTime = datetime.datetime.now()
            self.__logger.info("\n\n---===Oops! Asta Crushed===---")
            self.__logger.info('Timestamp: %s' % (currentTime.strftime("%Y-%m-%d %H:%M:%S")))
            self.__logger.error("Uncaught exception：", exc_info=(excType, excValue, tb))
            self.__logger.info('\n\n')
        except:
            pass

        sys.__excepthook__(excType, excValue, tb)

        err_msg = ''.join(traceback.format_exception(excType, excValue, tb))
        err_msg += '\n Asta 发生了不可预料的崩溃，请查看 logs/error.log 内容并反馈'
        win32api.MessageBox(0, err_msg, "Error", win32con.MB_OK)


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()

        file_verification.create_directory(f"{utils.workingDir}/logs")

        self.setTitleBar(CustomTitleBar(self))
        self.setWindowFlags(Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint)

        self.mainHBoxLayout = QHBoxLayout(self)
        self.mainNavigationInterface = NavigationInterface(self, showMenuButton=True)
        self.mainStackWidget = QStackedWidget(self)

        self.mainHomeInterface = home_frame.HomeWidget(self)
        self.mainGachaReportInterface = gacha_report_frame.GachaReportWidget(self)
        self.mainLinkInterface = link_frame.LinkWidget(self)
        self.mainGlyphsInterface = glyphs_frame.GlyphsWidget(self)
        self.mainMetaDataInterface = metadata_frame.MetaDataWidget(self)
        self.mainSettingInterface = settings_frame.SettingWidget(self)
        self.mainAboutInterface = about_frame.AboutWidget(self)

        self.mainStackWidget.addWidget(self.mainHomeInterface)
        self.mainStackWidget.addWidget(self.mainGachaReportInterface)
        self.mainStackWidget.addWidget(self.mainLinkInterface)
        self.mainStackWidget.addWidget(self.mainGlyphsInterface)
        self.mainStackWidget.addWidget(self.mainMetaDataInterface)
        self.mainStackWidget.addWidget(self.mainSettingInterface)
        self.mainStackWidget.addWidget(self.mainAboutInterface)

        self.initMetaData()

        self.initLayout()
        self.initNavigation()
        self.initWindow()
        startUp()
        log.infoWrite("[Main] UI Initialized")

    def initMetaData(self):
        if not metadata_utils.readMetaData("character"):
            characterData = character_list.categoryCharacterInStar()
            metadata_utils.updateMetaData("character", characterData)
            log.infoWrite("[MetaData] 角色元数据列表已更新")
            InfoBar.success("成功", "角色元数据列表已更新", position=InfoBarPosition.BOTTOM_RIGHT, parent=self)

        if not metadata_utils.readMetaData("permanent"):
            characterData = character_list.getPermanentCharacter()
            metadata_utils.updateMetaData("permanent", characterData)
            log.infoWrite("[MetaData] 常驻角色元数据列表已更新")
            InfoBar.success("成功", "常驻角色元数据列表已更新", position=InfoBarPosition.BOTTOM_RIGHT, parent=self)

        if not metadata_utils.readMetaData("weapon"):
            weaponData = weapon_list.categoryWeaponInStar()
            metadata_utils.updateMetaData("weapon", weaponData)
            log.infoWrite("[MetaData] 光锥元数据列表已更新")
            InfoBar.success("成功", "光锥元数据列表已更新", position=InfoBarPosition.BOTTOM_RIGHT, parent=self)

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
            text="UIGF",
            onClick=lambda: self.switchTo(self.mainLinkInterface)
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
        self.setFixedSize(1200, 700)
        self.setWindowTitle('Asta')
        self.setWindowIcon(QIcon(f'{utils.workingDir}/assets/avatar.png'))
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
        log.infoWrite(f"[Main] Current frame changed: {widget.objectName()}")


if __name__ == '__main__':
    log.infoWrite("[Main] Asta is starting...")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(f"{utils.workingDir}/assets/avatar.png"))
    w = Window()
    w.show()
    GlobalExceptHookHandler(f"{utils.workingDir}/logs/error.log")
    app.exec()
    log.infoWrite("[Main] Asta has been shutdown")
    log.infoWrite("-----===== Stop Tracking =====-----")
