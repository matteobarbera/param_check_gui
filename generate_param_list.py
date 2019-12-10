import sys

from PySide2.QtCore import QStringListModel
from PySide2.QtGui import QIcon, Qt, QFont, QIntValidator, QDoubleValidator
from PySide2.QtWidgets import (QDialog, QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QFrame, QLabel,
                               QTextBrowser, QHBoxLayout, QLineEdit, QCompleter, QTableWidget,
                               QHeaderView, QTableWidgetItem, QAbstractItemView)
from numpy import isnan

from full_param_list_html_parser import load_param_df
from load_critical_parameters import read_critical_parameters, write_critical_parameters


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
        applyBtn.clicked.connect(self.addEntryWidget.export_parameters)

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


class MyQLineEdit(QLineEdit):

    def __init__(self):
        super(MyQLineEdit, self).__init__()

    def set_int_validator(self, min_value=-1e9, max_value=1e9):
        validator = QIntValidator(min_value, max_value, self)
        self.setValidator(validator)

    def set_double_validator(self, min_value=-1e9, max_value=1e9, precision=6):
        validator = QDoubleValidator(min_value, max_value, precision, self)
        self.setValidator(validator)


# TODO Improve code layout
# TODO Refactor variables where appropriate
# TODO Improve minimum widget height/width
class ParamWidget(QWidget):

    _paramList = load_param_df()

    def __init__(self):
        super(ParamWidget, self).__init__()

        # ===================================================
        paramNameList = QStringListModel()
        paramNameList.setStringList(ParamWidget._paramList["Name"])
        paramCompleter = QCompleter()
        paramCompleter.setModel(paramNameList)
        paramCompleter.setCaseSensitivity(Qt.CaseInsensitive)

        self.paramLineEdit = QLineEdit()
        self.paramLineEdit.setCompleter(paramCompleter)
        self.paramLineEdit.setMinimumHeight(25)

        self.paramLineEdit.textChanged.connect(self.update_description)
        self.paramLineEdit.textChanged.connect(self.update_spinboxes)

        # ---------------- LineEdits ------------------------
        self.reqValLineEdit = MyQLineEdit()
        self.reqValLineEdit.setMinimumHeight(25)
        self.reqValLineEdit.setMinimumWidth(110)
        self.reqValLineEdit.set_double_validator(min_value=-1e9, max_value=1e9)
        self.reqValLineEdit.clear()
        self.reqValLineEdit.setReadOnly(True)
        self.reqValLineEdit.textChanged.connect(self.disable_range_boxes)

        self.rangeLowLineEdit = MyQLineEdit()
        self.rangeLowLineEdit.setMinimumHeight(25)
        self.rangeLowLineEdit.setMinimumWidth(100)
        self.rangeLowLineEdit.clear()
        self.rangeLowLineEdit.setReadOnly(True)

        self.rangeHighLineEdit = MyQLineEdit()
        self.rangeHighLineEdit.setMinimumHeight(25)
        self.rangeHighLineEdit.setMinimumWidth(100)
        self.rangeHighLineEdit.clear()
        self.rangeHighLineEdit.setReadOnly(True)

        # ---------------- headerLayout ---------------------
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
        self.addBtn.clicked.connect(self.add_entry)

        addBtnLayout = QVBoxLayout()
        addBtnLayout.addSpacing(spacerValue)
        addBtnLayout.addWidget(self.addBtn)
        addBtnLayout.addSpacing(spacerValue)

        headerLayout = QHBoxLayout()
        headerLayout.addLayout(paramNameLayout)
        headerLayout.addLayout(reqValueLayout)
        headerLayout.addLayout(lowerRangeLayout)
        headerLayout.addLayout(higherRangeLayout)
        headerLayout.addLayout(addBtnLayout)

        # ---------------- descriptionBox -------------------
        self.descriptionBox = QTextBrowser()
        self.descriptionBox.setMinimumHeight(50)
        self.descriptionBox.setMaximumHeight(130)
        self.descriptionBox.setAcceptRichText(True)
        self.descriptionBox.setStyleSheet("background-color: rgb(240,240,240)")

        # ---------------- paramTableView --------------------
        self.paramTableView = QTableWidget(0, 4)
        self.paramTableView.setHorizontalHeaderLabels(["Parameter Name", "Required", "Minimum", "Maximum"])
        self.paramTableView.setSortingEnabled(True)
        self.paramTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.paramTableView.setShowGrid(False)
        self.paramTableView.setAlternatingRowColors(True)
        self.paramTableView.setSelectionBehavior(QTableWidget.SelectRows)
        self.paramTableView.verticalHeader().setDefaultSectionSize(25)
        self.paramTableView.setStyleSheet("alternate-background-color: LightSteelBlue")
        self.paramTableView.itemPressed.connect(self.select_row)
        self.load_parameters()

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
        elif len(self.paramLineEdit.text().strip()) != 0:
            choice = QMessageBox.question(self, "Unknown parameter",
                                          "The parameter is not in the Full Parameter List"
                                          "\nAre you sure you want to add it? PX4 might crash",
                                          QMessageBox.Yes, QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.add_row()

    def add_row(self):
        for i in range(self.paramTableView.rowCount()):
            if self.paramLineEdit.text() == self.paramTableView.item(i, 0).text():
                choice = QMessageBox.question(self, "Warning",
                                              f"{self.paramLineEdit.text()} has already been specified."
                                              f"\nDo you want to overwrite it?",
                                              QMessageBox.Yes, QMessageBox.No)
                if choice == QMessageBox.Yes:
                    self.paramTableView.removeRow(i)
                    break
                else:
                    return
        # TODO Add logic to prevent wrong values being filled (outside of range, lower greater than upper, etc.)
        if len((self.reqValLineEdit.text() + self.rangeLowLineEdit.text() + self.rangeHighLineEdit.text()).strip()) != 0:
            self.paramTableView.setSortingEnabled(False)
            self.paramTableView.insertRow(0)
            self.paramTableView.setItem(0, 0, QTableWidgetItem(self.paramLineEdit.text()))
            self.paramTableView.setItem(0, 1, QTableWidgetItem(self.reqValLineEdit.text()))
            if self.rangeLowLineEdit.isEnabled() and self.rangeHighLineEdit.isEnabled():
                self.paramTableView.setItem(0, 2, QTableWidgetItem(self.rangeLowLineEdit.text()))
                self.paramTableView.setItem(0, 3, QTableWidgetItem(self.rangeHighLineEdit.text()))
            self.paramTableView.setSortingEnabled(True)
            self.paramLineEdit.clear()

    def edit_entry(self):
        row_index = self.paramTableView.currentRow()
        self.paramLineEdit.setText(self.paramTableView.item(row_index, 0).text())

    def remove_entry(self):
        selection = self.paramTableView.selectionModel().selectedRows()
        indices = sorted([index.row() for index in selection], reverse=True)
        for index in indices:
            self.paramTableView.removeRow(index)

    def remove_all_entries(self):
        choice = QMessageBox.question(self, "Confirm Clear All", "\nClear all entries?",
                                      QMessageBox.Yes, QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.paramTableView.selectAll()
            self.remove_entry()

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
    def set_spinbox_details(spinbox: MyQLineEdit, parameter_name: str, label_argument: str):
        min_value = -1e9
        max_value = 1e9
        precision = 6
        if not isnan(ParamWidget._paramList.loc[parameter_name, "Min"]):
            min_value = ParamWidget._paramList.loc[parameter_name, "Min"]
        if not isnan(ParamWidget._paramList.loc[parameter_name, "Max"]):
            max_value = ParamWidget._paramList.loc[parameter_name, "Max"]
        if not isnan(ParamWidget._paramList.loc[parameter_name, "Incr"]):
            try:
                _, decimals = str(ParamWidget._paramList.loc[parameter_name, "Incr"]).split('.')
                precision = len(decimals)
            except ValueError:
                precision = 0
        if ParamWidget._paramList.loc[parameter_name, "Type"] == "INT32":
            spinbox.set_int_validator(min_value, max_value)
            if not isnan(ParamWidget._paramList.loc[parameter_name, label_argument]):
                spinbox.setPlaceholderText(
                    f"{label_argument}: {round(float(ParamWidget._paramList.loc[parameter_name, label_argument]))}")
            else:
                spinbox.setPlaceholderText(
                    f"{label_argument}: {ParamWidget._paramList.loc[parameter_name, label_argument]}")
        else:
            spinbox.set_double_validator(min_value, max_value, precision)
            spinbox.setPlaceholderText(
                f"{label_argument}: {ParamWidget._paramList.loc[parameter_name, label_argument]}")
        spinbox.clear()
        spinbox.setReadOnly(False)

    @staticmethod
    def clear_spinbox_details(spinbox: MyQLineEdit):
        spinbox.setPlaceholderText("")
        spinbox.clear()
        spinbox.setReadOnly(True)

    @staticmethod
    def unknown_spinbox_details(spinbox: MyQLineEdit):
        spinbox.clear()
        spinbox.set_double_validator()
        spinbox.setPlaceholderText("Unknown")
        spinbox.clear()
        spinbox.setReadOnly(False)

    def update_spinboxes(self):
        if self.paramLineEdit.text() in ParamWidget._paramList["Name"]:
            parameter_name = self.paramLineEdit.text()
            self.set_spinbox_details(self.reqValLineEdit, parameter_name, "Default")
            self.set_spinbox_details(self.rangeLowLineEdit, parameter_name, "Min")
            self.set_spinbox_details(self.rangeHighLineEdit, parameter_name, "Max")
            self.incrLabel.setText(f"Incr: {ParamWidget._paramList.loc[parameter_name, 'Incr']}")
        elif len(self.paramLineEdit.text().strip()) != 0:
            self.unknown_spinbox_details(self.reqValLineEdit)
            self.unknown_spinbox_details(self.rangeLowLineEdit)
            self.unknown_spinbox_details(self.rangeHighLineEdit)
            self.incrLabel.setText("Incr:")
        else:
            self.clear_spinbox_details(self.reqValLineEdit)
            self.clear_spinbox_details(self.rangeLowLineEdit)
            self.clear_spinbox_details(self.rangeHighLineEdit)
            self.incrLabel.setText("Incr:")
        for i in range(self.paramTableView.rowCount()):
            if self.paramLineEdit.text() == self.paramTableView.item(i, 0).text():
                if self.paramTableView.item(i, 1) is not None:
                    self.reqValLineEdit.setText(self.paramTableView.item(i, 1).text())
                if self.paramTableView.item(i, 2) is not None:
                    self.rangeLowLineEdit.setText(self.paramTableView.item(i, 2).text())
                if self.paramTableView.item(i, 3) is not None:
                    self.rangeHighLineEdit.setText(self.paramTableView.item(i, 3).text())
                return

    def disable_range_boxes(self):
        if self.reqValLineEdit.text() != "":
            self.rangeLowLineEdit.setDisabled(True)
            self.rangeHighLineEdit.setDisabled(True)
        else:
            self.rangeLowLineEdit.setDisabled(False)
            self.rangeHighLineEdit.setDisabled(False)

    def select_row(self):
        selection = self.paramTableView.selectionModel().selectedRows()
        # Only one parameter at a time can be edited
        if len(selection) == 0 or len(selection) > 1:
            self.editEntryBtn.setEnabled(False)
        else:
            self.editEntryBtn.setEnabled(True)

    def load_parameters(self):
        h_file_parameters = read_critical_parameters()
        self.paramTableView.setSortingEnabled(False)
        for param_name, specified_values in h_file_parameters.items():
            self.paramTableView.insertRow(0)
            self.paramTableView.setItem(0, 0, QTableWidgetItem(param_name))
            if len(specified_values) == 1:
                self.paramTableView.setItem(0, 1, QTableWidgetItem(specified_values[0]))
            else:
                self.paramTableView.setItem(0, 1, QTableWidgetItem(''))
                if "-INFINITY" not in specified_values[0]:
                    self.paramTableView.setItem(0, 2, QTableWidgetItem(specified_values[0]))
                else:
                    self.paramTableView.setItem(0, 2, QTableWidgetItem(''))
                if "INFINITY" not in specified_values[1]:
                    self.paramTableView.setItem(0, 3, QTableWidgetItem(specified_values[1]))
                else:
                    self.paramTableView.setItem(0, 3, QTableWidgetItem(''))
        self.paramTableView.setSortingEnabled(True)

    def export_parameters(self):
        crit_params = dict()
        for i in range(self.paramTableView.rowCount()):
            values = []
            if len(self.paramTableView.item(i, 1).text().strip()) != 0:
                values.append(self.to_numeric(self.paramTableView.item(i, 1).text()))
                crit_params[self.paramTableView.item(i, 0).text()] = values
                continue
            if len(self.paramTableView.item(i, 2).text().strip()) == 0:
                values.append("-INFINITY")
            else:
                values.append(self.to_numeric(self.paramTableView.item(i, 2).text()))
            if len(self.paramTableView.item(i, 3).text().strip()) == 0:
                values.append("INFINITY")
            else:
                values.append(self.to_numeric(self.paramTableView.item(i, 3).text()))
            crit_params[self.paramTableView.item(i, 0).text()] = values

        write_critical_parameters(crit_params)

    @staticmethod
    def to_numeric(s: str):
        try:
            num = int(s)
        except ValueError:
            num = float(s)
        return num


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
