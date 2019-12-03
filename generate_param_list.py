import sys
from PySide2.QtWidgets import (QDialog, QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QFrame, QLabel,
                               QTextBrowser, QHBoxLayout, QDoubleSpinBox, QLineEdit, QCompleter, QTableWidget,
                               QHeaderView, QTableWidgetItem, QAbstractItemView)
from PySide2.QtGui import QIcon, Qt, QFont
from PySide2.QtCore import QStringListModel
from numpy import inf
from full_param_list_html_parser import load_param_df


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

        self.mainLayout = QVBoxLayout()

        self.create_top_layout()
        self.create_centre_layout()
        self.create_bottom_layout()

        self.setLayout(self.mainLayout)
        self.show()

    def create_top_layout(self):
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

    def create_centre_layout(self):
        # ==================================================

        # ---------------- paramEditLayout -----------------
        # TODO Add function that loads already specified parameters in the .h file
        self.addEntryWidget = ParamWidget()

        paramEditLayout = QVBoxLayout()
        paramEditLayout.addWidget(self.addEntryWidget)

        # ---------------- centreLayout ---------------------
        centreLayout = QVBoxLayout()
        centreLayout.addLayout(paramEditLayout)
        self.mainLayout.addLayout(centreLayout)

    def create_bottom_layout(self):
        okBtn = QPushButton("Ok")

        closeBtn = QPushButton("Close")
        closeBtn.clicked.connect(self.confirm_close)
        closeBtn.setShortcut("Ctrl+Q")

        applyBtn = QPushButton("Apply")

        bottomLayout = QHBoxLayout()
        bottomLayout.addStretch(1)
        bottomLayout.addWidget(okBtn)
        bottomLayout.addWidget(closeBtn)
        bottomLayout.addWidget(applyBtn)

        self.mainLayout.addLayout(bottomLayout)

    def confirm_close(self):
        # TODO CHANGE THIS
        sys.exit()

        choice = QMessageBox.question(self, "Close Window", "Close?",
                                      QMessageBox.Yes, QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass


class MyDoubleSpinBox(QDoubleSpinBox):

    def __init__(self):
        super(MyDoubleSpinBox, self).__init__()
        self.labelValue = ""

    def valueFromText(self, text: str):
        self.setValue(float(text))


class ParamWidget(QWidget):

    _paramList = load_param_df()

    def __init__(self):
        super(ParamWidget, self).__init__()

        # ===================================================
        paramNameList = QStringListModel()
        paramNameList.setStringList(ParamWidget._paramList["Name"])
        self.paramCompleter = QCompleter()
        self.paramCompleter.setModel(paramNameList)
        self.paramCompleter.setCaseSensitivity(Qt.CaseInsensitive)

        self.paramLineEdit = QLineEdit()
        self.paramLineEdit.setCompleter(self.paramCompleter)
        self.paramLineEdit.setMinimumHeight(25)

        self.paramLineEdit.textChanged.connect(self.update_description)
        self.paramLineEdit.textChanged.connect(self.update_spinboxes)
        # ---------------- SpinBoxes ------------------------
        self.reqValLineEdit = MyDoubleSpinBox()
        self.reqValLineEdit.setMinimumHeight(25)
        self.reqValLineEdit.setMinimumWidth(110)
        self.reqValLineEdit.clear()
        self.reqValLineEdit.setReadOnly(True)

        self.rangeLowLineEdit = MyDoubleSpinBox()
        self.rangeLowLineEdit.setMinimumHeight(25)
        self.rangeLowLineEdit.setMinimumWidth(100)
        self.rangeLowLineEdit.clear()
        self.rangeLowLineEdit.setReadOnly(True)

        self.rangeHighLineEdit = MyDoubleSpinBox()
        self.rangeHighLineEdit.setMinimumHeight(25)
        self.rangeHighLineEdit.setMinimumWidth(100)
        self.rangeHighLineEdit.clear()
        self.rangeHighLineEdit.setReadOnly(True)

        # ---------------- headerLayout ---------------------
        myFont = QFont()
        myFont.setUnderline(True)

        paramNameLabel = QLabel("Parameter Name")
        paramNameLabel.setFont(myFont)
        paramNameLabel.setBuddy(self.paramLineEdit)
        paramNameLayout = QVBoxLayout()
        paramNameLayout.addWidget(paramNameLabel)
        paramNameLayout.addWidget(self.paramLineEdit)
        paramNameLayout.addSpacing(23)

        reqValueLabel = QLabel("Required Value")
        reqValueLabel.setBuddy(self.reqValLineEdit)
        reqValueLabel.setFont(myFont)
        self.defaultLabel = QLabel(f"Def: {self.reqValLineEdit.labelValue}")
        # reqValueLabel.setMaximumWidth(115)
        reqValueLayout = QVBoxLayout()
        reqValueLayout.addWidget(reqValueLabel)
        reqValueLayout.addWidget(self.reqValLineEdit)
        reqValueLayout.addWidget(self.defaultLabel)

        lowerRangeLabel = QLabel("Lower Range")
        lowerRangeLabel.setBuddy(self.rangeLowLineEdit)
        lowerRangeLabel.setFont(myFont)
        self.minValueLabel = QLabel(f"Min: {self.rangeLowLineEdit.labelValue}")
        # lowerRangeLabel.setMaximumWidth(100)
        lowerRangeLayout = QVBoxLayout()
        lowerRangeLayout.addWidget(lowerRangeLabel)
        lowerRangeLayout.addWidget(self.rangeLowLineEdit)
        lowerRangeLayout.addWidget(self.minValueLabel)

        higherRangeLabel = QLabel("Upper Range")
        higherRangeLabel.setBuddy(self.rangeHighLineEdit)
        higherRangeLabel.setFont(myFont)
        self.maxValueLabel = QLabel(f"Max: {self.rangeHighLineEdit.labelValue}")
        # higherRangeLabel.setMaximumWidth(100)
        higherRangeLayout = QVBoxLayout()
        higherRangeLayout.addWidget(higherRangeLabel)
        higherRangeLayout.addWidget(self.rangeHighLineEdit)
        higherRangeLayout.addWidget(self.maxValueLabel)

        addBtnFont = QFont()
        addBtnFont.setPointSize(10)
        self.addBtn = QPushButton("Add Entry")
        self.addBtn.setFont(addBtnFont)
        self.addBtn.setMaximumHeight(23)
        self.addBtn.setIcon(QIcon("plus_icon.png"))
        self.addBtn.clicked.connect(self.add_entry)

        addBtnLayout = QVBoxLayout()
        addBtnLayout.addSpacing(23)
        addBtnLayout.addWidget(self.addBtn)
        addBtnLayout.addSpacing(23)

        headerLayout = QHBoxLayout()
        # headerLayout.addSpacing(20)
        headerLayout.addLayout(paramNameLayout)
        headerLayout.addLayout(reqValueLayout)
        headerLayout.addLayout(lowerRangeLayout)
        headerLayout.addLayout(higherRangeLayout)
        headerLayout.addLayout(addBtnLayout)

        # ---------------- descriptionBox -------------------
        self.descriptionBox = QTextBrowser()
        self.descriptionBox.setMinimumHeight(50)
        self.descriptionBox.setMaximumHeight(130)
        self.descriptionBox.setStyleSheet("background-color: rgb(240,240,240)")

        # ---------------- paramTableView --------------------
        self.paramTableView = QTableWidget(0, 4)
        self.paramTableView.setHorizontalHeaderLabels(["Parameter Name", "Required", "Minimum", "Maximum"])
        self.paramTableView.setSortingEnabled(True)
        self.paramTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.paramTableView.setShowGrid(False)
        self.paramTableView.setAlternatingRowColors(True)
        self.paramTableView.setSelectionBehavior(QTableWidget.SelectRows)
        self.paramTableView.itemPressed.connect(self.select_row)

        self.paramTableHeader = self.paramTableView.horizontalHeader()
        self.paramTableHeader.setSectionResizeMode(0, QHeaderView.Stretch)

        self.removeEntryBtn = QPushButton()
        self.removeEntryBtn.setIcon(QIcon("minus_icon.png"))
        self.removeEntryBtn.setFlat(True)
        self.removeEntryBtn.setMaximumSize(20, 20)
        self.removeEntryBtn.clicked.connect(self.remove_entry)

        self.editEntryBtn = QPushButton()
        self.editEntryBtn.setIcon(QIcon("edit_icon.png"))
        self.editEntryBtn.setFlat(True)
        self.editEntryBtn.setMaximumSize(20, 20)
        self.editEntryBtn.setEnabled(False)
        self.editEntryBtn.clicked.connect(self.edit_entry)

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
        tableLayout.addWidget(self.paramTableView)
        tableLayout.addWidget(btnFrame)

        # ---------------- clearEntryBtn --------------------
        clearEntryBtn = QPushButton("Clear All")
        clearEntryBtn.setIcon(QIcon("minus_icon.png"))
        clearEntryBtn.clicked.connect(self.remove_all_entries)
        # ===================================================
        layout = QVBoxLayout()
        layout.addLayout(headerLayout)
        layout.addWidget(self.descriptionBox)
        layout.addLayout(tableLayout)
        layout.addWidget(clearEntryBtn)
        self.setLayout(layout)

    def add_entry(self):
        if self.paramLineEdit.text() in ParamWidget._paramList["Name"]:
            self.add_row()
            self.paramLineEdit.clear()
        elif len(self.paramLineEdit.text().strip()) != 0:
            choice = QMessageBox.question(self, "Unknown parameter",
                                          "The parameter is not in the Full Parameter List"
                                          "\nAre you sure you want to add it? PX4 might crash",
                                          QMessageBox.Yes, QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.add_row()
                self.paramLineEdit.clear()

    def add_row(self):
        # TODO Allow overwriting parameter
        for i in range(self.paramTableView.rowCount()):
            if self.paramLineEdit.text() == self.paramTableView.item(i, 0).text():
                QMessageBox.critical(self, "Error", f"The {self.paramLineEdit.text()} has already been specified")
                return
        # TODO Add logic to prevent wrong values being filled
        # TODO Fill in empty value
        self.paramTableView.setSortingEnabled(False)
        self.paramTableView.insertRow(0)
        self.paramTableView.setItem(0, 0, QTableWidgetItem(self.paramLineEdit.text()))
        self.paramTableView.setItem(0, 1, QTableWidgetItem(str(self.reqValLineEdit.value())))
        self.paramTableView.setItem(0, 2, QTableWidgetItem(str(self.rangeLowLineEdit.value())))
        self.paramTableView.setItem(0, 3, QTableWidgetItem(str(self.rangeHighLineEdit.value())))
        self.paramTableView.setSortingEnabled(True)

    def edit_entry(self):
        row_index = self.paramTableView.currentRow()
        self.paramLineEdit.setText(self.paramTableView.item(row_index, 0).text())

    def remove_entry(self):
        selection = self.paramTableView.selectionModel().selectedRows()
        indices = sorted([index.row() for index in selection], reverse=True)
        for index in indices:
            self.paramTableView.removeRow(index)

    def remove_all_entries(self):
        choice = QMessageBox.question(self, "Confirm Clear All",
                                      "\nClear all entries?",
                                      QMessageBox.Yes, QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.paramTableView.clearContents()
            for row in range(self.paramTableView.rowCount()):
                self.paramTableView.removeRow(row)

    def update_description(self):
        if self.paramLineEdit.text() in ParamWidget._paramList["Name"]:
            parameter_name = self.paramLineEdit.text()
            self.descriptionBox.setText(ParamWidget._paramList.loc[parameter_name, "Description"])
        elif len(self.paramLineEdit.text().strip()) != 0:
            warning_text = "<b>Warning</b>: Parameter not in Full Parameter List "
            self.descriptionBox.setText(warning_text)
        else:
            self.descriptionBox.setText("")

    @staticmethod
    def set_spinbox_details(spinbox: MyDoubleSpinBox, parameter_name: str, label_type: str):
        spinbox.setRange(ParamWidget._paramList.loc[parameter_name, "Min"],
                         ParamWidget._paramList.loc[parameter_name, "Max"])
        spinbox.setSingleStep(ParamWidget._paramList.loc[parameter_name, "Incr"])
        spinbox.labelValue = ParamWidget._paramList.loc[parameter_name, label_type]
        spinbox.clear()
        spinbox.setReadOnly(False)

    @staticmethod
    def clear_spinbox_details(spinbox: MyDoubleSpinBox):
        spinbox.labelValue = ""
        spinbox.clear()
        spinbox.setReadOnly(True)

    @staticmethod
    def unknown_spinbox_details(spinbox: MyDoubleSpinBox):
        spinbox.clear()
        spinbox.setRange(-inf, inf)
        spinbox.setSingleStep(1e-5)
        spinbox.labelValue = ""
        spinbox.clear()
        spinbox.setReadOnly(False)

    def update_spinboxes(self):
        if self.paramLineEdit.text() in ParamWidget._paramList["Name"]:
            parameter_name = self.paramLineEdit.text()
            self.set_spinbox_details(self.reqValLineEdit, parameter_name, "Default")
            self.defaultLabel.setText(f"Def: {self.reqValLineEdit.labelValue}")
            self.set_spinbox_details(self.rangeLowLineEdit, parameter_name, "Min")
            self.minValueLabel.setText(f"Min: {self.rangeLowLineEdit.labelValue}")
            self.set_spinbox_details(self.rangeHighLineEdit, parameter_name, "Max")
            self.maxValueLabel.setText(f"Max: {self.rangeHighLineEdit.labelValue}")
        elif len(self.paramLineEdit.text().strip()) != 0:
            self.unknown_spinbox_details(self.reqValLineEdit)
            self.defaultLabel.setText(f"Def: {self.reqValLineEdit.labelValue}")
            self.unknown_spinbox_details(self.rangeLowLineEdit)
            self.minValueLabel.setText(f"Min: {self.rangeLowLineEdit.labelValue}")
            self.unknown_spinbox_details(self.rangeHighLineEdit)
            self.maxValueLabel.setText(f"Max: {self.rangeHighLineEdit.labelValue}")
        else:
            self.clear_spinbox_details(self.reqValLineEdit)
            self.clear_spinbox_details(self.rangeLowLineEdit)
            self.clear_spinbox_details(self.rangeHighLineEdit)
        for i in range(self.paramTableView.rowCount()):
            if self.paramLineEdit.text() == self.paramTableView.item(i, 0).text():
                self.reqValLineEdit.valueFromText(self.paramTableView.item(i, 1).text())
                self.rangeLowLineEdit.valueFromText(self.paramTableView.item(i, 2).text())
                self.rangeHighLineEdit.valueFromText(self.paramTableView.item(i, 3).text())
                return

    def select_row(self):
        selection = self.paramTableView.selectionModel().selectedRows()
        if len(selection) == 0 or len(selection) > 1:
            self.editEntryBtn.setEnabled(False)
        else:
            self.editEntryBtn.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
