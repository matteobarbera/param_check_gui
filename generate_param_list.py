import sys
from PySide2.QtWidgets import (QDialog, QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QFrame, QLabel,
                               QTextBrowser, QHBoxLayout, QDoubleSpinBox, QLineEdit, QCompleter, QTableWidget,
                               QHeaderView)
from PySide2.QtGui import QIcon, Qt, QFont
from PySide2.QtCore import QStringListModel
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

        # ---------------------------------------------------
        # Probably go for QDoubleSpinBox
        self.reqValLineEdit = QDoubleSpinBox()
        self.reqValLineEdit.setMinimumHeight(25)
        self.reqValLineEdit.setMinimumWidth(110)
        self.reqValLineEdit.setMinimum(-1000)  # or setRange(min, max)
        self.reqValLineEdit.setSingleStep(0.01)

        # ---------------------------------------------------
        self.rangeLowLineEdit = QDoubleSpinBox()
        self.rangeLowLineEdit.setMinimumHeight(25)
        self.rangeLowLineEdit.setMinimumWidth(100)
        self.rangeHighLineEdit = QDoubleSpinBox()
        self.rangeHighLineEdit.setMinimumHeight(25)
        self.rangeHighLineEdit.setMinimumWidth(100)

        # ---------------- headerLayout ---------------------
        myFont = QFont()
        myFont.setUnderline(True)

        paramNameLabel = QLabel("Parameter Name")
        paramNameLabel.setFont(myFont)
        paramNameLabel.setBuddy(self.paramLineEdit)
        paramNameLayout = QVBoxLayout()
        paramNameLayout.addWidget(paramNameLabel)
        paramNameLayout.addWidget(self.paramLineEdit)

        reqValueLabel = QLabel("Required Value")
        reqValueLabel.setBuddy(self.reqValLineEdit)
        reqValueLabel.setFont(myFont)
        # reqValueLabel.setMaximumWidth(115)
        reqValueLayout = QVBoxLayout()
        reqValueLayout.addWidget(reqValueLabel)
        reqValueLayout.addWidget(self.reqValLineEdit)

        lowerRangeLabel = QLabel("Lower Range")
        lowerRangeLabel.setBuddy(self.rangeLowLineEdit)
        lowerRangeLabel.setFont(myFont)
        # lowerRangeLabel.setMaximumWidth(100)
        lowerRangeLayout = QVBoxLayout()
        lowerRangeLayout.addWidget(lowerRangeLabel)
        lowerRangeLayout.addWidget(self.rangeLowLineEdit)

        higherRangeLabel = QLabel("Upper Range")
        higherRangeLabel.setBuddy(self.rangeHighLineEdit)
        higherRangeLabel.setFont(myFont)
        # higherRangeLabel.setMaximumWidth(100)
        higherRangeLayout = QVBoxLayout()
        higherRangeLayout.addWidget(higherRangeLabel)
        higherRangeLayout.addWidget(self.rangeHighLineEdit)

        addBtnFont = QFont()
        addBtnFont.setPointSize(10)
        self.addBtn = QPushButton("Add Entry")
        self.addBtn.setFont(addBtnFont)
        self.addBtn.setMaximumHeight(23)
        self.addBtn.setIcon(QIcon("plus_icon.png"))

        addBtnLayout = QVBoxLayout()
        addBtnLayout.addSpacing(23)
        addBtnLayout.addWidget(self.addBtn)

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
        self.paramTableView.setSortingEnabled(True)
        self.paramTableView.setHorizontalHeaderLabels(["Parameter Name", "Required", "Minimum", "Maximum"])

        self.paramTableHeader = self.paramTableView.horizontalHeader()
        self.paramTableHeader.setSectionResizeMode(0, QHeaderView.Stretch)

        # ---------------- clearEntryBtn --------------------
        clearEntryBtn = QPushButton("Clear All")
        clearEntryBtn.setIcon(QIcon("minus_icon.png"))
        clearEntryBtn.clicked.connect(self.remove_all_entries)
        # ===================================================
        layout = QVBoxLayout()
        layout.addLayout(headerLayout)
        layout.addWidget(self.descriptionBox)
        layout.addWidget(self.paramTableView)
        layout.addWidget(clearEntryBtn)
        self.setLayout(layout)

    def remove_all_entries(self):
        choice = QMessageBox.question(self, "Confirm Clear All",
                                      "\nClear all entries?",
                                      QMessageBox.Yes, QMessageBox.No)
        if choice == QMessageBox.Yes:
            pass

    def update_description(self):
        if self.paramLineEdit.text() in ParamWidget._paramList["Name"]:
            parameter_name = self.paramLineEdit.text()
            self.descriptionBox.setText(ParamWidget._paramList.loc[parameter_name, "Description"])
        elif len(self.paramLineEdit.text().strip()) != 0:
            warning_text = "<b>Warning</b>: Parameter not in Full Parameter List "
            self.descriptionBox.setText(warning_text)
        else:
            self.descriptionBox.setText("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
