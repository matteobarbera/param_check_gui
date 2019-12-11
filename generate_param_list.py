import sys

from PySide2.QtCore import QStringListModel, Signal, Slot
from PySide2.QtGui import QIcon, Qt, QFont, QIntValidator, QDoubleValidator, QPixmap
from PySide2.QtWidgets import (QDialog, QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QFrame, QLabel,
                               QTextBrowser, QHBoxLayout, QLineEdit, QCompleter, QTableWidget, QSizePolicy,
                               QHeaderView, QTableWidgetItem, QAbstractItemView)
from numpy import isnan

from full_param_list_html_parser import load_param_df
from load_critical_parameters import read_critical_parameters, write_critical_parameters


# TODO Add shortcuts and tooltips
class App(QDialog):

    def __init__(self):
        super(App, self).__init__()
        self.title = "Critical Parameters"
        self.left = 200
        self.top = 200
        self.width = 750
        self.height = 700

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.hasChanged = False

        self.mainLayout = QVBoxLayout()

        self.createTopLayout()
        self.createCentreLayout()
        self.createBottomLayout()

        self.addEntryWidget.changedStatus.connect(self.changesMade)

        self.setLayout(self.mainLayout)
        self.show()

    def createTopLayout(self):
        explanationText = QLabel()
        explanationText.setIndent(20)
        explanationText.setText("<font size=4><b>Critical Parameter Generator</b></font>"
                                "<span style='margin-top: 0px; margin-bottom: 0px;'>"

                                "<p> This application lets you define the parameters and their corresponding values "
                                "that will be checked by <i>avy_param_check.cpp</i> in the "
                                "<span style='font-weight: 500;'> Commander</span> module.</p>"
                                
                                "<p>Specifying a required value will ensure that the user will be warned if the "
                                "parameter is not exactly that value. Any range requirement imposed will thus be "
                                "ignored.</p>"
                                
                                "<p>If one of the range entries is left blank it will default to the parameter's "
                                "minimum or maximum value.</p>"
                                "</span>")
        explanationText.setWordWrap(True)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)

        topLayout = QVBoxLayout()
        topLayout.addWidget(explanationText)
        topLayout.addWidget(divider)

        self.mainLayout.addLayout(topLayout)

    def createCentreLayout(self):
        # ---------------- paramEditLayout -----------------
        self.addEntryWidget = ParamWidget()

        paramEditLayout = QVBoxLayout()
        paramEditLayout.addWidget(self.addEntryWidget)

        # ---------------- centreLayout ---------------------
        centreLayout = QVBoxLayout()
        centreLayout.addLayout(paramEditLayout)
        self.mainLayout.addLayout(centreLayout)

    def createBottomLayout(self):
        # -------------- changesMadeFrame -------------------
        changesMadeImage = QPixmap("check_icon.png")

        self.changesMadeIcon = QLabel()
        self.changesMadeIcon.setPixmap(changesMadeImage.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.changesMadeIcon.setMaximumHeight(25)

        self.changesMadeLabel = QLabel("No unsaved changes")
        self.changesMadeLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        changesMadeLayout = QHBoxLayout()
        changesMadeLayout.addStretch(1)
        changesMadeLayout.addWidget(self.changesMadeIcon)
        changesMadeLayout.addWidget(self.changesMadeLabel)
        changesMadeLayout.addStretch(1)
        changesMadeLayout.setContentsMargins(0, 3, 0, 3)

        self.changesMadeFrame = QFrame()
        self.changesMadeFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.changesMadeFrame.setStyleSheet("QFrame { background-color: Palegreen; }")
        self.changesMadeFrame.setMinimumWidth(250)
        self.changesMadeFrame.setLayout(changesMadeLayout)

        # -------------- bottomBtnLayout --------------------
        self.okBtn = QPushButton("Ok")
        self.okBtn.clicked.connect(self.saveAndClose)
        self.okBtn.setEnabled(False)

        closeBtn = QPushButton("Close")
        closeBtn.clicked.connect(self.confirmClose)
        closeBtn.setShortcut("Ctrl+Q")

        self.applyBtn = QPushButton("Apply")
        self.applyBtn.clicked.connect(self.addEntryWidget.exportParameters)
        self.applyBtn.setEnabled(False)

        bottomBtnLayout = QHBoxLayout()
        bottomBtnLayout.addStretch(1)
        bottomBtnLayout.addWidget(self.changesMadeFrame)
        bottomBtnLayout.addWidget(self.okBtn)
        bottomBtnLayout.addWidget(closeBtn)
        bottomBtnLayout.addWidget(self.applyBtn)

        mainBottomLayout = QVBoxLayout()
        mainBottomLayout.addLayout(bottomBtnLayout)

        self.mainLayout.addLayout(mainBottomLayout)

    def confirmClose(self):
        if self.hasChanged:
            choice = QMessageBox.question(self, "Close Window", "Close application?\nThere are unsaved changes",
                                          QMessageBox.Yes, QMessageBox.No)
            if choice == QMessageBox.Yes:
                sys.exit()
            else:
                pass
        else:
            sys.exit()

    def saveAndClose(self):
        self.addEntryWidget.exportParameters()
        sys.exit()

    @Slot(bool)
    def changesMade(self, changes_made: bool):
        icon_size = 16
        if changes_made:
            self.hasChanged = True
            self.okBtn.setEnabled(True)
            self.applyBtn.setEnabled(True)
            icon = QPixmap("cross_icon.png")
            self.changesMadeIcon.setPixmap(
                icon.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.changesMadeLabel.setText("Unsaved changes")
            self.changesMadeFrame.setStyleSheet("QFrame { background-color: Salmon; }")
        else:
            self.hasChanged = False
            self.okBtn.setEnabled(False)
            self.applyBtn.setEnabled(False)
            icon = QPixmap("check_icon.png")
            self.changesMadeIcon.setPixmap(
                icon.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.changesMadeLabel.setText("No unsaved changes")
            self.changesMadeFrame.setStyleSheet("QFrame { background-color: Palegreen; }")


class MyQLineEdit(QLineEdit):

    validator_default_min = -1e9
    validator_default_max = 1e9
    validator_default_prec = 6

    def __init__(self):
        super(MyQLineEdit, self).__init__()
        self.defaultStyleSheet = self.styleSheet()
        self.isInputValid = True

    def setIntValidator(self, min_value=validator_default_min, max_value=validator_default_max):
        validator = QIntValidator(min_value, max_value, self)
        self.setValidator(validator)

    def setDoubleValidator(
            self, min_value=validator_default_min, max_value=validator_default_max, precision=validator_default_prec):
        validator = QDoubleValidator(min_value, max_value, precision, self)
        self.setValidator(validator)

    def inputIsValid(self):
        self.isInputValid = True
        self.setStyleSheet(self.defaultStyleSheet)

    def inputIsInvalid(self):
        self.isInputValid = False
        self.setStyleSheet("QLineEdit { background-color : Salmon; }")


# TODO Improve minimum widget height/width
class ParamWidget(QWidget):

    _paramList = load_param_df()
    changedStatus = Signal(bool)

    def __init__(self):
        super(ParamWidget, self).__init__()

        # ===================================================
        # ---------------- LineEdits ------------------------
        paramNameList = QStringListModel()
        paramNameList.setStringList(ParamWidget._paramList["Name"])
        paramCompleter = QCompleter()
        paramCompleter.setModel(paramNameList)
        paramCompleter.setCaseSensitivity(Qt.CaseInsensitive)

        self.paramLineEdit = QLineEdit()
        self.paramLineEdit.setCompleter(paramCompleter)
        self.paramLineEdit.setMinimumHeight(25)

        self.paramLineEdit.textChanged.connect(self.updateDescription)
        self.paramLineEdit.textChanged.connect(self.updateSpinboxes)

        self.reqValLineEdit = MyQLineEdit()
        self.reqValLineEdit.setMinimumHeight(25)
        self.reqValLineEdit.setMinimumWidth(110)
        self.reqValLineEdit.setDoubleValidator(MyQLineEdit.validator_default_min, MyQLineEdit.validator_default_max)
        self.reqValLineEdit.clear()
        self.reqValLineEdit.setReadOnly(True)
        self.reqValLineEdit.textChanged.connect(self.disableRangeBoxes)
        self.reqValLineEdit.textChanged.connect(self.checkValid)

        self.rangeLowLineEdit = MyQLineEdit()
        self.rangeLowLineEdit.setMinimumHeight(25)
        self.rangeLowLineEdit.setMinimumWidth(100)
        self.rangeLowLineEdit.clear()
        self.rangeLowLineEdit.setReadOnly(True)
        self.rangeLowLineEdit.textChanged.connect(self.checkValid)

        self.rangeHighLineEdit = MyQLineEdit()
        self.rangeHighLineEdit.setMinimumHeight(25)
        self.rangeHighLineEdit.setMinimumWidth(100)
        self.rangeHighLineEdit.clear()
        self.rangeHighLineEdit.setReadOnly(True)
        self.rangeHighLineEdit.textChanged.connect(self.checkValid)

        # ---------------- paramInputLayout -----------------
        myFont = QFont()
        myFont.setBold(True)

        spacerValue = 23

        paramNameLabel = QLabel("Parameter Name")
        paramNameLabel.setFont(myFont)
        paramNameLabel.setBuddy(self.paramLineEdit)
        paramNameLayout = QVBoxLayout()
        paramNameLayout.addWidget(paramNameLabel)
        paramNameLayout.addWidget(self.paramLineEdit)
        paramNameLayout.addSpacing(spacerValue)

        reqValueLabel = QLabel("Required Value")
        reqValueLabel.setBuddy(self.reqValLineEdit)
        reqValueLabel.setFont(myFont)
        self.incrLabel = QLabel("Incr:")
        reqValueLayout = QVBoxLayout()
        reqValueLayout.addWidget(reqValueLabel)
        reqValueLayout.addWidget(self.reqValLineEdit)
        reqValueLayout.addWidget(self.incrLabel)

        lowerRangeLabel = QLabel("Lower Range")
        lowerRangeLabel.setBuddy(self.rangeLowLineEdit)
        lowerRangeLabel.setFont(myFont)
        lowerRangeLayout = QVBoxLayout()
        lowerRangeLayout.addWidget(lowerRangeLabel)
        lowerRangeLayout.addWidget(self.rangeLowLineEdit)
        lowerRangeLayout.addSpacing(spacerValue)

        higherRangeLabel = QLabel("Upper Range")
        higherRangeLabel.setBuddy(self.rangeHighLineEdit)
        higherRangeLabel.setFont(myFont)
        higherRangeLayout = QVBoxLayout()
        higherRangeLayout.addWidget(higherRangeLabel)
        higherRangeLayout.addWidget(self.rangeHighLineEdit)
        higherRangeLayout.addSpacing(spacerValue)

        addBtnFont = QFont()
        addBtnFont.setPointSize(10)
        self.addBtn = QPushButton("Add Entry")
        self.addBtn.setFont(addBtnFont)
        self.addBtn.setMaximumHeight(23)
        self.addBtn.setIcon(QIcon("plus_icon.png"))
        self.addBtn.clicked.connect(self.addEntry)

        addBtnLayout = QVBoxLayout()
        addBtnLayout.addSpacing(spacerValue)
        addBtnLayout.addWidget(self.addBtn)
        addBtnLayout.addSpacing(spacerValue)

        paramInputLayout = QHBoxLayout()
        paramInputLayout.addLayout(paramNameLayout)
        paramInputLayout.addLayout(reqValueLayout)
        paramInputLayout.addLayout(lowerRangeLayout)
        paramInputLayout.addLayout(higherRangeLayout)
        paramInputLayout.addLayout(addBtnLayout)

        # ---------------- descriptionBox -------------------
        self.descriptionBox = QTextBrowser()
        self.descriptionBox.setMinimumHeight(50)
        self.descriptionBox.setMaximumHeight(130)
        self.descriptionBox.setAcceptRichText(True)
        self.descriptionBox.setStyleSheet("background-color: rgb(240,240,240)")

        # ------------------ tableLayout --------------------
        self.paramTable = QTableWidget(0, 4)
        self.paramTable.setHorizontalHeaderLabels(["Parameter Name", "Required", "Minimum", "Maximum"])
        self.paramTable.setSortingEnabled(True)
        self.paramTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.paramTable.setShowGrid(False)
        self.paramTable.setAlternatingRowColors(True)
        self.paramTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.paramTable.verticalHeader().setDefaultSectionSize(25)
        self.paramTable.setStyleSheet("alternate-background-color: LightSteelBlue")
        self.paramTable.itemPressed.connect(self.selectRow)
        self.loadParameters()

        self.paramTableHeader = self.paramTable.horizontalHeader()
        self.paramTableHeader.setSectionResizeMode(0, QHeaderView.Stretch)

        self.removeEntryBtn = QPushButton()
        self.removeEntryBtn.setIcon(QIcon("minus_icon.png"))
        self.removeEntryBtn.setFlat(True)
        self.removeEntryBtn.setMaximumSize(20, 20)
        self.removeEntryBtn.clicked.connect(self.removeEntry)

        self.editEntryBtn = QPushButton()
        self.editEntryBtn.setIcon(QIcon("edit_icon.png"))
        self.editEntryBtn.setFlat(True)
        self.editEntryBtn.setMaximumSize(20, 20)
        self.editEntryBtn.setEnabled(False)
        self.editEntryBtn.clicked.connect(self.editEntry)

        sideBtnLayout = QVBoxLayout()
        sideBtnLayout.addWidget(self.removeEntryBtn)
        sideBtnLayout.addWidget(self.editEntryBtn)
        sideBtnLayout.addStretch(1)
        sideBtnLayout.setContentsMargins(0, 0, 0, 0)

        btnFrame = QFrame()
        btnFrame.setFrameStyle(QFrame.Box | QFrame.Sunken)
        btnFrame.setLineWidth(1)
        btnFrame.setLayout(sideBtnLayout)

        tableLayout = QHBoxLayout()
        tableLayout.addWidget(self.paramTable)
        tableLayout.addWidget(btnFrame)

        # ---------------- clearEntryBtn --------------------
        clearEntryBtn = QPushButton("Clear All")
        clearEntryBtn.setIcon(QIcon("minus_icon.png"))
        clearEntryBtn.clicked.connect(self.removeAllEntries)

        # ===================================================
        layout = QVBoxLayout()
        layout.addLayout(paramInputLayout)
        layout.addWidget(self.descriptionBox)
        layout.addLayout(tableLayout)
        layout.addWidget(clearEntryBtn)
        self.setLayout(layout)

    def addEntry(self):
        if self.paramLineEdit.text() in ParamWidget._paramList["Name"]:
            self.addRow()
        elif len(self.paramLineEdit.text().strip()) != 0:
            choice = QMessageBox.question(self, "Unknown parameter",
                                          "The parameter is not in the Full Parameter List"
                                          "\nAre you sure you want to add it? PX4 might crash",
                                          QMessageBox.Yes, QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.addRow()

    def addRow(self):
        if not (self.reqValLineEdit.isInputValid and self.rangeLowLineEdit.isInputValid
                and self.rangeHighLineEdit.isInputValid):
            choice = QMessageBox.question(self, "Warning",
                                          "One of the specified values is outside the expected valid ranges."
                                          "\nAre you sure you want to add this parameter to the table?",
                                          QMessageBox.Yes, QMessageBox.No)
            if choice == QMessageBox.No:
                return
        for i in range(self.paramTable.rowCount()):
            if self.paramLineEdit.text() == self.paramTable.item(i, 0).text():
                choice = QMessageBox.question(self, "Warning",
                                              f"{self.paramLineEdit.text()} has already been specified."
                                              f"\nDo you want to overwrite it?",
                                              QMessageBox.Yes, QMessageBox.No)
                if choice == QMessageBox.Yes:
                    self.paramTable.removeRow(i)
                    break
                else:
                    return
        if len((self.reqValLineEdit.text().strip(" -") + self.rangeLowLineEdit.text().strip(" -")
                + self.rangeHighLineEdit.text()).strip(" -")) != 0:
            self.paramTable.setSortingEnabled(False)
            self.paramTable.insertRow(0)
            self.paramTable.setItem(0, 0, QTableWidgetItem(self.paramLineEdit.text()))
            self.paramTable.setItem(0, 1, QTableWidgetItem(self.reqValLineEdit.text()))
            if self.rangeLowLineEdit.isEnabled() and self.rangeHighLineEdit.isEnabled():
                self.paramTable.setItem(0, 2, QTableWidgetItem(self.rangeLowLineEdit.text()))
                self.paramTable.setItem(0, 3, QTableWidgetItem(self.rangeHighLineEdit.text()))
            self.paramTable.setSortingEnabled(True)
            self.paramLineEdit.clear()
        self.changedStatus.emit(True)

    def editEntry(self):
        row_index = self.paramTable.currentRow()
        self.paramLineEdit.setText(self.paramTable.item(row_index, 0).text())

    def removeEntry(self):
        selection = self.paramTable.selectionModel().selectedRows()
        indices = sorted([index.row() for index in selection], reverse=True)
        for index in indices:
            self.paramTable.removeRow(index)
        self.changedStatus.emit(True)

    def removeAllEntries(self):
        choice = QMessageBox.question(self, "Confirm Clear All", "\nClear all entries?",
                                      QMessageBox.Yes, QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.paramTable.selectAll()
            self.removeEntry()

    def selectRow(self):
        selection = self.paramTable.selectionModel().selectedRows()
        # Only one parameter at a time can be edited
        if len(selection) == 0 or len(selection) > 1:
            self.editEntryBtn.setEnabled(False)
        else:
            self.editEntryBtn.setEnabled(True)

    def updateDescription(self):
        if self.paramLineEdit.text() in ParamWidget._paramList["Name"]:
            parameter_name = self.paramLineEdit.text()
            self.descriptionBox.setText(ParamWidget._paramList.loc[parameter_name, "Description"])
        elif len(self.paramLineEdit.text().strip()) != 0:
            warning_text = "<b>Warning</b>: Parameter not in Full Parameter List"
            self.descriptionBox.setText(warning_text)
        else:
            self.descriptionBox.setText("")

    @staticmethod
    def setSpinboxDetails(lineEdit_: MyQLineEdit, parameterName: str, labelArgument: str):
        min_value = MyQLineEdit.validator_default_min
        max_value = MyQLineEdit.validator_default_max
        precision = MyQLineEdit.validator_default_prec
        if not isnan(ParamWidget._paramList.loc[parameterName, "Min"]):
            min_value = ParamWidget._paramList.loc[parameterName, "Min"]
        if not isnan(ParamWidget._paramList.loc[parameterName, "Max"]):
            max_value = ParamWidget._paramList.loc[parameterName, "Max"]
        if not isnan(ParamWidget._paramList.loc[parameterName, "Incr"]):
            try:
                _, decimals = str(ParamWidget._paramList.loc[parameterName, "Incr"]).split(".")
                precision = len(decimals)
            except ValueError:
                precision = 0
        if ParamWidget._paramList.loc[parameterName, "Type"] == "INT32":
            lineEdit_.setIntValidator(min_value, max_value)
            if not isnan(ParamWidget._paramList.loc[parameterName, labelArgument]):
                lineEdit_.setPlaceholderText(
                    f"{labelArgument}: {round(float(ParamWidget._paramList.loc[parameterName, labelArgument]))}")
            else:
                lineEdit_.setPlaceholderText(
                    f"{labelArgument}: {ParamWidget._paramList.loc[parameterName, labelArgument]}")
        else:
            lineEdit_.setDoubleValidator(min_value, max_value, precision)
            lineEdit_.setPlaceholderText(
                f"{labelArgument}: {ParamWidget._paramList.loc[parameterName, labelArgument]}")
        lineEdit_.clear()
        lineEdit_.setReadOnly(False)

    @staticmethod
    def clearSpinboxDetails(lineEdit_: MyQLineEdit):
        lineEdit_.setPlaceholderText("")
        lineEdit_.clear()
        lineEdit_.setReadOnly(True)

    @staticmethod
    def setUnknownSpinboxDetails(lineEdit_: MyQLineEdit):
        lineEdit_.clear()
        lineEdit_.setDoubleValidator()
        lineEdit_.setPlaceholderText("Unknown")
        lineEdit_.clear()
        lineEdit_.setReadOnly(False)

    def updateSpinboxes(self):
        if self.paramLineEdit.text() in ParamWidget._paramList["Name"]:
            parameter_name = self.paramLineEdit.text()
            self.setSpinboxDetails(self.reqValLineEdit, parameter_name, "Default")
            self.setSpinboxDetails(self.rangeLowLineEdit, parameter_name, "Min")
            self.setSpinboxDetails(self.rangeHighLineEdit, parameter_name, "Max")
            self.incrLabel.setText(f"Incr: {ParamWidget._paramList.loc[parameter_name, 'Incr']}")
        elif len(self.paramLineEdit.text().strip()) != 0:
            self.setUnknownSpinboxDetails(self.reqValLineEdit)
            self.setUnknownSpinboxDetails(self.rangeLowLineEdit)
            self.setUnknownSpinboxDetails(self.rangeHighLineEdit)
            self.incrLabel.setText("Incr:")
        else:
            self.clearSpinboxDetails(self.reqValLineEdit)
            self.clearSpinboxDetails(self.rangeLowLineEdit)
            self.clearSpinboxDetails(self.rangeHighLineEdit)
            self.incrLabel.setText("Incr:")
        for i in range(self.paramTable.rowCount()):
            if self.paramLineEdit.text() == self.paramTable.item(i, 0).text():
                if self.paramTable.item(i, 1) is not None:
                    self.reqValLineEdit.setText(self.paramTable.item(i, 1).text())
                if self.paramTable.item(i, 2) is not None:
                    self.rangeLowLineEdit.setText(self.paramTable.item(i, 2).text())
                if self.paramTable.item(i, 3) is not None:
                    self.rangeHighLineEdit.setText(self.paramTable.item(i, 3).text())
                return

    def disableRangeBoxes(self):
        if self.reqValLineEdit.text() != "":
            self.rangeLowLineEdit.setDisabled(True)
            self.rangeHighLineEdit.setDisabled(True)
        else:
            self.rangeLowLineEdit.setDisabled(False)
            self.rangeHighLineEdit.setDisabled(False)

    def checkValid(self):
        minVal = MyQLineEdit.validator_default_min
        maxVal = MyQLineEdit.validator_default_max
        if self.paramLineEdit.text() in ParamWidget._paramList["Name"]:
            parameterName = self.paramLineEdit.text()
            if not isnan(ParamWidget._paramList.loc[parameterName, "Min"]):
                minVal = ParamWidget._paramList.loc[parameterName, "Min"]
            if not isnan(ParamWidget._paramList.loc[parameterName, "Max"]):
                maxVal = ParamWidget._paramList.loc[parameterName, "Max"]

        if len(self.reqValLineEdit.text().strip("- ")) != 0:
            reqVal = self._toNumeric(self.reqValLineEdit.text())
            if reqVal < minVal or reqVal > maxVal:
                self.reqValLineEdit.inputIsInvalid()
            else:
                self.reqValLineEdit.inputIsValid()
        else:
            self.reqValLineEdit.inputIsValid()

        lowVal = minVal
        uppVal = maxVal
        if len(self.rangeLowLineEdit.text().strip(" -")) != 0:
            lowVal = self._toNumeric(self.rangeLowLineEdit.text())
        if len(self.rangeHighLineEdit.text().strip(" -")) != 0:
            uppVal = self._toNumeric(self.rangeHighLineEdit.text())

        if lowVal < minVal or lowVal > maxVal or lowVal > uppVal:
            self.rangeLowLineEdit.inputIsInvalid()
        else:
            self.rangeLowLineEdit.inputIsValid()
        if uppVal < minVal or uppVal > maxVal or uppVal < lowVal:
            self.rangeHighLineEdit.inputIsInvalid()
        else:
            self.rangeHighLineEdit.inputIsValid()

    def loadParameters(self):
        hFileParameters = read_critical_parameters()
        self.paramTable.setSortingEnabled(False)
        for paramName, specifiedValues in hFileParameters.items():
            self.paramTable.insertRow(0)
            self.paramTable.setItem(0, 0, QTableWidgetItem(paramName))
            if len(specifiedValues) == 1:
                self.paramTable.setItem(0, 1, QTableWidgetItem(specifiedValues[0]))
            else:
                self.paramTable.setItem(0, 1, QTableWidgetItem(""))
                if "-INFINITY" not in specifiedValues[0]:
                    self.paramTable.setItem(0, 2, QTableWidgetItem(specifiedValues[0]))
                else:
                    self.paramTable.setItem(0, 2, QTableWidgetItem(""))
                if "INFINITY" not in specifiedValues[1]:
                    self.paramTable.setItem(0, 3, QTableWidgetItem(specifiedValues[1]))
                else:
                    self.paramTable.setItem(0, 3, QTableWidgetItem(""))
        self.paramTable.setSortingEnabled(True)

    def exportParameters(self):
        critParams = dict()
        for i in range(self.paramTable.rowCount()):
            values = []
            if len(self.paramTable.item(i, 1).text().strip()) != 0:
                values.append(self._toNumeric(self.paramTable.item(i, 1).text()))
                critParams[self.paramTable.item(i, 0).text()] = values
                continue
            if len(self.paramTable.item(i, 2).text().strip()) == 0:
                values.append("-INFINITY")
            else:
                values.append(self._toNumeric(self.paramTable.item(i, 2).text()))
            if len(self.paramTable.item(i, 3).text().strip()) == 0:
                values.append("INFINITY")
            else:
                values.append(self._toNumeric(self.paramTable.item(i, 3).text()))
            critParams[self.paramTable.item(i, 0).text()] = values

        write_critical_parameters(critParams)
        self.changedStatus.emit(False)

    @staticmethod
    def _toNumeric(s: str) -> int or float:
        try:
            num = int(s)
        except ValueError:
            num = float(s)
        return num


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
