import logging

import requests
from PySide6 import QtGui
from PySide6.QtCharts import QChartView
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QColor, QPalette, QPainter
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QAbstractItemView, QHeaderView, \
    QTableWidgetItem, QStyleOptionViewItem

from qfluentwidgets import FluentIcon, RoundMenu, TableWidget, TextEdit, MessageBox, InfoBarPosition, ComboBox, \
    Action, InfoBar, StateToolTip, TableItemDelegate, isDarkTheme, PushButton, ToggleButton
from qfluentwidgets import DropDownPushButton
from qfluentwidgets.common.style_sheet import styleSheetManager

from ..Scripts.UI import style_sheet
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

        self.analyzer = None
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

        self.bottomRightBasicLevelHBox = QHBoxLayout(self)
        self.bottomRightBasicLevel5TotalBtn = PushButton()
        self.bottomRightBasicLevel4TotalBtn = PushButton()
        self.bottomRightBasicLevel3TotalBtn = PushButton()
        self.bottomRightBasicLevelHBox.addWidget(self.bottomRightBasicLevel5TotalBtn)
        self.bottomRightBasicLevelHBox.addWidget(self.bottomRightBasicLevel4TotalBtn)
        self.bottomRightBasicLevelHBox.addWidget(self.bottomRightBasicLevel3TotalBtn)

        self.bottomRightBasicAverageHBox = QHBoxLayout(self)
        self.bottomRightBasicAverage5TotalLabel = QLabel("5星平均出货")
        self.bottomRightBasicAverage4TotalLabel = QLabel("4星平均出货")
        self.bottomRightCompleteAnalysisBtn = PushButton()
        self.bottomRightBasicAverageHBox.addWidget(self.bottomRightBasicAverage5TotalLabel)
        self.bottomRightBasicAverageHBox.addWidget(self.bottomRightBasicAverage4TotalLabel)
        self.bottomRightBasicAverageHBox.addWidget(self.bottomRightCompleteAnalysisBtn)

        self.bottomRightBasicListTopHBox = QHBoxLayout(self)
        self.bottomRightBasicListLabel = QLabel("五星列表")
        self.bottomRightBasicToggleBtn = ToggleButton("显示耗费抽数", self, FluentIcon.SEND_FILL)
        self.bottomRightBasicListTopHBox.addWidget(self.bottomRightBasicListLabel)
        self.bottomRightBasicListTopHBox.addWidget(self.bottomRightBasicToggleBtn)
        self.bottomRightBasicListTextEdit = TextEdit(self)

        self.bottomRightAnalysisLabel = QLabel("保底情况")
        self.bottomRightAnalysisGuaranteeLabel = QLabel("未知")
        self.bottomRightGraphLabel = QLabel("图像", self)
        self.bottomRightGraphView = QChartView(self)
        self.bottomRightVBox.addWidget(self.bottomRightBasicLabel)
        self.bottomRightVBox.addWidget(self.bottomRightBasicTotalLabel)
        self.bottomRightVBox.addLayout(self.bottomRightBasicLevelHBox)
        self.bottomRightVBox.addLayout(self.bottomRightBasicAverageHBox)
        self.bottomRightVBox.addLayout(self.bottomRightBasicListTopHBox)
        self.bottomRightVBox.addWidget(self.bottomRightBasicListTextEdit)
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
        self.bottomRightGraphLabel.setEnabled(mode)
        self.bottomRightBasicToggleBtn.setEnabled(mode)

    def emptyAllStatistics(self):
        self.bottomLeftGachaTable.clearContents()
        self.bottomRightGraphView.setChart(analysis.empty_chart())

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        if not gacha_report_read.getUIDList():
            self.setInteractive(False)
            InfoBar.warning("警告", "找不到数据",
                            position=InfoBarPosition.BOTTOM_RIGHT, parent=self)
            self.initData()
            self.emptyAllStatistics()
        else:
            self.initData()
            self.setInteractive(True)
        self.bottomRightGraphView.setBackgroundBrush(QColor(37, 37, 37) if isDarkTheme() else QColor(255, 255, 255))

    def __bottomRightBasicToggleBtnClicked(self):
        if self.bottomRightBasicToggleBtn.isChecked():
            self.bottomRightBasicListTextEdit.setText(self.analyzer.get_star_5_cost_to_string())
        else:
            self.bottomRightBasicListTextEdit.setText(self.analyzer.get_star_5_to_string())

    def initFrame(self):
        self.headerLeftGachaReportTitleLabel.setFont(utils.get_font(18))
        self.headerRightGachaTypeCombobox.setFixedWidth(160)
        self.headerRightGachaTypeCombobox.addItems(["角色活动跃迁", "光锥活动跃迁", "群星跃迁", "始发跃迁"])
        self.headerRightGachaTypeCombobox.setEnabled(False)
        self.headerRightGachaTypeCombobox.currentIndexChanged.connect(self.__headerRightGachaTypeComboboxChanged)
        self.headerRightUIDSelectCombobox.setFixedWidth(160)
        self.headerRightUIDSelectCombobox.currentIndexChanged.connect(self.__headerRightUIDSelectComboboxChanged)
        self.headerRightFullUpdateDropBtn.setFixedWidth(160)
        self.headerRightFullUpdateDropBtn.setMenu(self.headerRightFullUpdateDropBtnMenu)

        self.bottomLeftGachaTable.setFixedWidth(600)
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

        self.bottomRightBasicLevel5TotalBtn.setText("5星数量")
        self.bottomRightBasicLevel4TotalBtn.setText("4星数量")
        self.bottomRightBasicLevel3TotalBtn.setText("3星数量")
        styleSheetManager.deregister(self.bottomRightBasicLevel5TotalBtn)
        styleSheetManager.deregister(self.bottomRightBasicLevel4TotalBtn)
        styleSheetManager.deregister(self.bottomRightBasicLevel3TotalBtn)
        self.bottomRightBasicLevel5TotalBtn.setObjectName("level_5")
        self.bottomRightBasicLevel4TotalBtn.setObjectName("level_4")
        self.bottomRightBasicLevel3TotalBtn.setObjectName("level_3")
        self.bottomRightBasicLevel5TotalBtn.setStyleSheet(style_sheet.component_style_sheet("gacha_report_push_button_5"))
        self.bottomRightBasicLevel4TotalBtn.setStyleSheet(style_sheet.component_style_sheet("gacha_report_push_button_4"))
        self.bottomRightBasicLevel3TotalBtn.setStyleSheet(style_sheet.component_style_sheet("gacha_report_push_button_3"))

        self.bottomRightBasicAverage5TotalLabel.setFont(utils.get_font(12))
        self.bottomRightBasicAverage4TotalLabel.setFont(utils.get_font(12))
        self.bottomRightBasicAverage5TotalLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bottomRightBasicAverage4TotalLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        styleSheetManager.deregister(self.bottomRightBasicAverage5TotalLabel)
        styleSheetManager.deregister(self.bottomRightBasicAverage4TotalLabel)
        self.bottomRightBasicAverage5TotalLabel.setObjectName("level_5_average")
        self.bottomRightBasicAverage4TotalLabel.setObjectName("level_4_average")
        self.bottomRightBasicAverage5TotalLabel.setStyleSheet(
            style_sheet.component_style_sheet("gacha_report_push_button_5"))
        self.bottomRightBasicAverage4TotalLabel.setStyleSheet(
            style_sheet.component_style_sheet("gacha_report_push_button_4"))

        self.bottomRightBasicListLabel.setFont(utils.get_font(12))
        self.bottomRightBasicListTextEdit.setFixedHeight(70)
        self.bottomRightBasicToggleBtn.setFixedWidth(160)
        self.bottomRightBasicToggleBtn.clicked.connect(self.__bottomRightBasicToggleBtnClicked)

        styleSheetManager.deregister(self.bottomRightCompleteAnalysisBtn)
        self.bottomRightCompleteAnalysisBtn.setObjectName("complete_analysis")
        self.bottomRightCompleteAnalysisBtn.setText("查看完整分析")
        self.bottomRightCompleteAnalysisBtn.setStyleSheet(style_sheet.component_style_sheet("gacha_report_complete_analysis_button"))

        self.bottomRightAnalysisLabel.setFont(utils.get_font(14))
        self.bottomRightAnalysisGuaranteeLabel.setFont(utils.get_font(10))
        self.bottomRightGraphLabel.setFont(utils.get_font(14))
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
        self.analyzer = analysis.Analysis(currentData)
        self.bottomRightBasicTotalLabel.setText(f"跃迁次数: {self.analyzer.get_total_amount_to_string()}")
        self.bottomRightBasicLevel5TotalBtn.setText(
            f"5星数量: {self.analyzer.get_star_5_amount_to_string()} ({self.analyzer.get_star_5_percent_to_string()})")
        self.bottomRightBasicLevel4TotalBtn.setText(
            f"4星数量: {self.analyzer.get_star_4_amount_to_string()} ({self.analyzer.get_star_4_percent_to_string()})")
        self.bottomRightBasicLevel3TotalBtn.setText(f"3星数量: {self.analyzer.get_star_3_amount_to_string()}")
        self.bottomRightBasicAverage5TotalLabel.setText(f"5星平均出货: {self.analyzer.get_star_5_average_to_string()}")
        self.bottomRightBasicAverage4TotalLabel.setText(f"4星平均出货: {self.analyzer.get_star_4_average_to_string()}")
        self.bottomRightBasicListTextEdit.setText(self.analyzer.get_star_5_to_string())
        self.bottomRightAnalysisGuaranteeLabel.setText(
            self.analyzer.get_guarantee(self.headerRightGachaTypeCombobox.currentText()))
        self.bottomRightGraphView.setChart(self.analyzer.get_pie_chart())

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
        self.__bottomRightBasicToggleBtnClicked()

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
