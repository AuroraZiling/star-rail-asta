import logging

import requests
from PySide6 import QtGui
from PySide6.QtCharts import QChartView
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QColor, QPalette, QPainter
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QAbstractItemView, QHeaderView, \
    QTableWidgetItem, QStyleOptionViewItem

from qfluentwidgets import FluentIcon, RoundMenu, TableWidget, TextEdit, MessageBox, InfoBarPosition, ComboBox, \
    Action, InfoBar, StateToolTip, TableItemDelegate, isDarkTheme
from qfluentwidgets import DropDownPushButton

from ..config import cfg
from ..Scripts.Utils import tools
from ..Core.GachaReport.gacha_report_thread import GachaReportThread
from ..Scripts.UI.style_sheet import StyleSheet
from ..Scripts.UI.custom_dialog import URLDialog
from ..Core.GachaReport.gacha_report_utils import convertAPI
from ..Core.GachaReport import gacha_report_read
from ..Core.GachaReport.Analysis import table_completion, analysis
from ..Core.GachaReport.MihoyoAPI import by_web_cache
from ..constant import GACHATYPE

utils = tools.Tools()

rowColorMapping = {}


class CustomTableItemDelegate(TableItemDelegate):

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(option, index)
        global rowColorMapping
        option.palette.setColor(QPalette.Text, rowColorMapping[index.row()])
        option.palette.setColor(QPalette.HighlightedText, rowColorMapping[index.row()])


class GachaReportWidget(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.frameMessageBox = None
        self.isInteractive = False

        self.completedOriginalTableData = {}
        self.currentUID = ""

        # Gacha Report Thread
        self.gachaReportThreadStateTooltip = None
        self.gachaReportThread = None

        self.baseVBox = QVBoxLayout(self)

        self.headerHBox = QHBoxLayout()
        self.headerLeftVBox = QVBoxLayout()
        self.headerLeftGachaReportTitleLabel = QLabel("跃迁记录")
        self.headerLeftVBox.addWidget(self.headerLeftGachaReportTitleLabel)

        self.headerRightHBox = QHBoxLayout()
        self.headerRightGachaTypeCombobox = ComboBox(self)
        self.headerRightUIDSelectCombobox = ComboBox(self)
        self.headerRightFullUpdateDropBtn = DropDownPushButton("全量更新", self, FluentIcon.UPDATE)
        self.headerRightFullUpdateDropBtnWebCacheAction = Action(FluentIcon.DOCUMENT.icon(), "网页缓存获取")
        self.headerRightFullUpdateDropBtnURLAction = Action(FluentIcon.ALIGNMENT.icon(), "手动URL获取")
        self.headerRightHBox.addWidget(self.headerRightGachaTypeCombobox)
        self.headerRightHBox.addWidget(self.headerRightUIDSelectCombobox)
        self.headerRightHBox.addWidget(self.headerRightFullUpdateDropBtn)
        self.headerRightFullUpdateDropBtnMenu = RoundMenu(parent=self)
        self.headerHBox.addLayout(self.headerLeftVBox)
        self.headerHBox.addLayout(self.headerRightHBox)

        self.bottomHBox = QHBoxLayout()
        self.bottomLeftVBox = QVBoxLayout()
        self.bottomLeftGachaTable = TableWidget()
        self.bottomLeftVBox.addWidget(self.bottomLeftGachaTable)

        self.bottomRightVBox = QVBoxLayout()
        self.bottomRightBasicLabel = QLabel("基本数据")
        self.bottomRightBasicTotalLabel = QLabel("未知抽数")
        self.bottomRightBasicLevel5TotalLabel = QLabel("未知5星数量")
        self.bottomRightBasicLevel5TotalTextEdit = TextEdit()
        self.bottomRightBasicLevel4TotalLabel = QLabel("未知4星数量")
        self.bottomRightBasicLevel3TotalLabel = QLabel("未知3星数量")
        self.bottomRightAnalysisLabel = QLabel("保底情况")
        self.bottomRightAnalysisGuaranteeLabel = QLabel("未知")
        self.bottomRightGraphLabel = QLabel("图像", self)
        self.bottomRightGraphView = QChartView(self)
        self.bottomRightVBox.addWidget(self.bottomRightBasicLabel)
        self.bottomRightVBox.addWidget(self.bottomRightBasicTotalLabel)
        self.bottomRightVBox.addWidget(self.bottomRightBasicLevel5TotalLabel)
        self.bottomRightVBox.addWidget(self.bottomRightBasicLevel5TotalTextEdit)
        self.bottomRightVBox.addWidget(self.bottomRightBasicLevel4TotalLabel)
        self.bottomRightVBox.addWidget(self.bottomRightBasicLevel3TotalLabel)
        self.bottomRightVBox.addWidget(self.bottomRightAnalysisLabel)
        self.bottomRightVBox.addWidget(self.bottomRightAnalysisGuaranteeLabel)
        self.bottomRightVBox.addWidget(self.bottomRightGraphLabel)
        self.bottomRightVBox.addWidget(self.bottomRightGraphView)

        self.bottomHBox.addLayout(self.bottomLeftVBox)
        self.bottomHBox.addLayout(self.bottomRightVBox)

        self.baseVBox.addLayout(self.headerHBox)
        self.baseVBox.addLayout(self.bottomHBox)

        logging.info("[GachaReport] UI Initialized")

        self.setObjectName("GachaReportFrame")
        StyleSheet.GACHA_REPORT_FRAME.apply(self)
        self.initHeaderRightFullUpdateDropBtnActions()
        self.initFrame()

        self.initData()

    def closeEvent(self, event):
        self.gachaReportThread.exit()
        event.accept()

    def __gachaReportThreadStateTooltipClosed(self):
        self.gachaReportThread.exit(0)
        self.gachaReportStatusChanged((1, "Operation cancelled", "Operation cancelled"))
        InfoBar.warning("操作终止", "数据读取已停止",
                        position=InfoBarPosition.BOTTOM, parent=self)

    def gachaReportStatusChanged(self, msg: tuple):
        if msg and self.gachaReportThreadStateTooltip:
            self.setInteractive(False)
            self.headerRightGachaTypeCombobox.setEnabled(False)
            self.gachaReportThreadStateTooltip.setContent(msg[1])
            if len(msg) == 3 and not msg[0] == -1:
                self.gachaReportThreadStateTooltip.setTitle(f"更新数据中 | {msg[2]}")
            if msg[0] == 1:
                self.setInteractive(True)
                self.gachaReportThreadStateTooltip.setState(True)
                self.gachaReportThreadStateTooltip = None
                self.headerRightFullUpdateDropBtn.setEnabled(True)
                self.headerRightGachaTypeCombobox.setEnabled(True)
                self.initData()
                self.headerRightUIDSelectCombobox.setCurrentText(msg[2])
                self.__headerRightUIDSelectComboboxChanged()
            elif msg[0] == -1:
                self.setInteractive(True)
                self.gachaReportThreadStateTooltip.setState(True)
                self.gachaReportThreadStateTooltip = None
                self.headerRightFullUpdateDropBtn.setEnabled(True)
                self.headerRightGachaTypeCombobox.setEnabled(True)
                MessageBox("错误", msg[2], self).exec()
        else:
            self.headerRightFullUpdateDropBtn.setEnabled(True)

    def __headerRightFullUpdateDropBtnWebCache(self):
        gachaURL = convertAPI(by_web_cache.getURL(cfg.gameDataFolder.value))
        if gachaURL:
            resp = MessageBox("成功", "请求已被获取，是否更新数据?", self)
            if resp.exec():
                self.headerRightFullUpdateDropBtn.setEnabled(False)
                self.gachaReportThread = GachaReportThread(gachaURL)
                self.gachaReportThreadStateTooltip = StateToolTip("更新数据中", "数据更新开始",
                                                                  self)
                self.gachaReportThreadStateTooltip.closedSignal.connect(self.__gachaReportThreadStateTooltipClosed)
                self.gachaReportThreadStateTooltip.move(5, 5)
                self.gachaReportThreadStateTooltip.show()
                self.gachaReportThread.start()
                self.gachaReportThread.trigger.connect(self.gachaReportStatusChanged)
        else:
            InfoBar.error("失败", "无法从游戏缓存中获取请求", InfoBarPosition.TOP_RIGHT, parent=self)

    def __headerRightFullUpdateDropBtnURL(self):
        w = URLDialog("输入URL", "请在下方输入 MiHoYo API 的URL", self)
        w.exec()
        gachaURL = w.textEditWidget.toPlainText()
        try:
            requests.get(gachaURL)
        except requests.exceptions.MissingSchema:
            InfoBar.error("错误", "URL格式错误", InfoBarPosition.TOP_RIGHT, parent=self)
            return
        if gachaURL:
            gachaURL = gachaURL.split("game_biz=hk4e_cn")[0] + "game_biz=hk4e_cn"
            self.headerRightFullUpdateDropBtn.setEnabled(False)
            self.gachaReportThread = GachaReportThread(gachaURL)
            self.gachaReportThreadStateTooltip = StateToolTip("更新数据中", "数据更新开始", self)
            self.gachaReportThreadStateTooltip.closedSignal.connect(self.__gachaReportThreadStateTooltipClosed)
            self.gachaReportThreadStateTooltip.move(5, 5)
            self.gachaReportThreadStateTooltip.show()
            self.gachaReportThread.start()
            self.gachaReportThread.trigger.connect(self.gachaReportStatusChanged)


    def initHeaderRightFullUpdateDropBtnActions(self):
        self.headerRightFullUpdateDropBtnWebCacheAction.triggered.connect(self.__headerRightFullUpdateDropBtnWebCache)
        self.headerRightFullUpdateDropBtnURLAction.triggered.connect(self.__headerRightFullUpdateDropBtnURL)
        self.headerRightFullUpdateDropBtnMenu.addAction(self.headerRightFullUpdateDropBtnWebCacheAction)
        self.headerRightFullUpdateDropBtnMenu.addAction(self.headerRightFullUpdateDropBtnURLAction)

    def setInteractive(self, mode):
        self.bottomLeftGachaTable.setEnabled(mode)
        self.headerRightGachaTypeCombobox.setEnabled(mode)
        self.headerRightUIDSelectCombobox.setEnabled(mode)
        self.bottomRightBasicLevel5TotalTextEdit.setEnabled(mode)
        self.bottomRightGraphLabel.setEnabled(mode)

    def emptyAllStatistics(self):
        self.bottomLeftGachaTable.clearContents()
        self.bottomRightBasicLevel5TotalTextEdit.clear()

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        if not gacha_report_read.getUIDList():
            self.setInteractive(False)
            InfoBar.warning("警告", "找不到UID",
                            position=InfoBarPosition.BOTTOM_RIGHT, parent=self)
            self.initData()
            self.emptyAllStatistics()
        else:
            self.initData()
            self.setInteractive(True)
        self.bottomRightGraphView.setBackgroundBrush(QColor(37, 37, 37) if isDarkTheme() else QColor(255, 255, 255))

    def initFrame(self):
        self.headerLeftGachaReportTitleLabel.setFont(utils.get_font(18))
        self.headerRightGachaTypeCombobox.setFixedWidth(160)
        self.headerRightGachaTypeCombobox.addItems(["角色活动跃迁", "光锥活动跃迁", "群星跃迁"])
        self.headerRightGachaTypeCombobox.setEnabled(False)
        self.headerRightGachaTypeCombobox.currentIndexChanged.connect(self.__headerRightGachaTypeComboboxChanged)
        self.headerRightUIDSelectCombobox.setFixedWidth(160)
        self.headerRightUIDSelectCombobox.currentIndexChanged.connect(self.__headerRightUIDSelectComboboxChanged)
        self.headerRightFullUpdateDropBtn.setFixedWidth(160)
        self.headerRightFullUpdateDropBtn.setMenu(self.headerRightFullUpdateDropBtnMenu)

        self.bottomLeftGachaTable.setFixedWidth(620)
        self.bottomLeftGachaTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.bottomLeftGachaTable.setColumnCount(6)
        self.bottomLeftGachaTable.verticalHeader().setHidden(True)
        self.bottomLeftGachaTable.setColumnWidth(0, 60)
        self.bottomLeftGachaTable.setColumnWidth(1, 75)
        self.bottomLeftGachaTable.setColumnWidth(2, 140)
        self.bottomLeftGachaTable.setColumnWidth(3, 160)
        self.bottomLeftGachaTable.setColumnWidth(4, 85)
        self.bottomLeftGachaTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.bottomLeftGachaTable.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bottomLeftGachaTable.setHorizontalHeaderLabels(
            ["序号", "类型", "名称", "获取时间", "十连/单抽", "保底内"])

        self.bottomRightBasicLabel.setFont(utils.get_font(14))
        self.bottomRightBasicTotalLabel.setFont(utils.get_font(12))
        self.bottomRightBasicLevel5TotalLabel.setFont(utils.get_font(10))
        self.bottomRightBasicLevel4TotalLabel.setFont(utils.get_font(10))
        self.bottomRightBasicLevel3TotalLabel.setFont(utils.get_font(10))
        self.bottomRightBasicLevel5TotalTextEdit.setReadOnly(True)

        self.bottomRightAnalysisLabel.setFont(utils.get_font(14))
        self.bottomRightAnalysisGuaranteeLabel.setFont(utils.get_font(10))
        self.bottomRightGraphLabel.setFont(utils.get_font(14))
        self.bottomRightGraphView.setFixedHeight(150)
        self.bottomRightGraphView.setRenderHint(QPainter.Antialiasing)

    def tableUpdateData(self, currentData):
        global rowColorMapping
        rowColorMapping = {}
        for index, each in enumerate(currentData):
            for eachColumn in range(0, 6):
                columnModel = [each["order"], each["item_type"], each["name"], each["time"], each["gacha_mode"],
                               each["guarantee"], each["color"]]
                self.bottomLeftGachaTable.setItem(index, eachColumn, QTableWidgetItem())
                self.bottomLeftGachaTable.setRowHeight(index, 40)
                self.bottomLeftGachaTable.item(index, eachColumn).setText(columnModel[eachColumn])
                rowColorMapping.update({index: QColor(columnModel[6])})
        self.bottomLeftGachaTable.setItemDelegate(CustomTableItemDelegate(self.bottomLeftGachaTable))
        logging.info(f"[GachaReport] Gacha table updated")

    def analysisUpdateData(self, currentData):
        analyzer = analysis.Analysis(currentData)
        self.bottomRightBasicTotalLabel.setText(f"跃迁次数: {analyzer.get_total_amount_to_string()}")
        self.bottomRightBasicLevel5TotalLabel.setText(
            f"5星数量: {analyzer.get_star_5_amount_to_string()} ({analyzer.get_star_5_percent_to_string()})")
        self.bottomRightBasicLevel5TotalTextEdit.setText(analyzer.get_star_5_to_string())
        self.bottomRightBasicLevel4TotalLabel.setText(
            f"4星数量: {analyzer.get_star_4_amount_to_string()} ({analyzer.get_star_4_percent_to_string()})")
        self.bottomRightBasicLevel3TotalLabel.setText(f"3星数量: {analyzer.get_star_3_amount_to_string()}")
        self.bottomRightAnalysisGuaranteeLabel.setText(
            analyzer.get_guarantee(self.headerRightGachaTypeCombobox.currentText()))
        self.bottomRightGraphView.setChart(analyzer.get_pie_chart())

    def __headerRightGachaTypeComboboxChanged(self):
        logging.info(f"[GachaReport] Gacha type selection changed")
        if not self.completedOriginalTableData:
            self.currentUID = self.headerRightUIDSelectCombobox.currentText()
            tableOriginalData = gacha_report_read.convertDataToTable(gacha_report_read.getDataFromUID(self.currentUID))
            self.completedOriginalTableData = table_completion.originalTableDataToComplete(tableOriginalData)
        currentTableData = self.completedOriginalTableData[
            GACHATYPE[self.headerRightGachaTypeCombobox.currentText()]]
        self.bottomLeftGachaTable.setRowCount(len(currentTableData))
        self.tableUpdateData(currentTableData)
        self.analysisUpdateData(currentTableData)

    def __headerRightUIDSelectComboboxChanged(self):
        currentUID = self.headerRightUIDSelectCombobox.currentText()
        UIDList = gacha_report_read.getUIDList()
        if currentUID and currentUID in UIDList:
            logging.info(f"[GachaReport] UID Selected: {currentUID}")
            self.headerRightGachaTypeCombobox.setEnabled(True)
            tableOriginalData = gacha_report_read.convertDataToTable(gacha_report_read.getDataFromUID(currentUID))
            self.completedOriginalTableData = table_completion.originalTableDataToComplete(tableOriginalData)

            if not self.headerRightGachaTypeCombobox.currentText():
                self.headerRightGachaTypeCombobox.setCurrentIndex(0)
            self.__headerRightGachaTypeComboboxChanged()

            cfg.set(cfg.gachaReportLastUID, currentUID)
        else:
            self.currentUID = ""
            cfg.set(cfg.gachaReportLastUID, "")

    def initData(self):
        self.headerRightUIDSelectCombobox.clear()
        self.headerRightUIDSelectCombobox.addItems(gacha_report_read.getUIDList())
        self.currentUID = cfg.gachaReportLastUID.value
        if self.currentUID:
            self.headerRightUIDSelectCombobox.setCurrentText(self.currentUID)
            self.__headerRightUIDSelectComboboxChanged()
        logging.info("[GachaReport] Data initialized")
