import sys
from PySide2.QtWidgets import (QDialog, QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QFrame,
                               QHBoxLayout, QComboBox, QScrollArea, QDoubleSpinBox, QLabel, QLineEdit, QCompleter)
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
        # ---------------- headerLayout ---------------------
        myFont = QFont()
        myFont.setUnderline(True)

        paramNameLabel = QLabel("Parameter Name")
        paramNameLabel.setFont(myFont)

        reqValueLabel = QLabel("Required Value")
        reqValueLabel.setFont(myFont)
        reqValueLabel.setMaximumWidth(115)

        lowerRangeLabel = QLabel("Lower Range")
        lowerRangeLabel.setFont(myFont)
        lowerRangeLabel.setMaximumWidth(100)

        higherRangeLabel = QLabel("Upper Range")
        higherRangeLabel.setFont(myFont)
        higherRangeLabel.setMaximumWidth(100)

        headerLayout = QHBoxLayout()
        headerLayout.addSpacing(20)
        headerLayout.addWidget(paramNameLabel)
        headerLayout.addWidget(reqValueLabel)
        headerLayout.addWidget(lowerRangeLabel)
        headerLayout.addWidget(higherRangeLabel)
        headerLayout.addSpacing(75)

        # ---------------- paramComboLayout -----------------
        # TODO Add function that loads already specified parameters in the .h file
        loadedParams = [ParamWidget(), ParamWidget(), ParamWidget()]
        loadedParams[1].paramComboBox.setCurrentIndex(1)

        self.specifiedParamsList = []
        self.paramComboLayout = QVBoxLayout()  # TODO Update name
        for widget in loadedParams:
            self.add_entry()
            # add_entry() prepends a ParamWidget object to the list, hence [0] index
            self.specifiedParamsList[0].paramComboBox.setCurrentIndex(widget.paramComboBox.currentIndex())
            # set all other values using widget properties
        self.paramComboLayout.addStretch(1)

        # ---------------- scrollArea -----------------------
        innerScrollArea = QWidget()
        innerScrollArea.setLayout(self.paramComboLayout)

        mainScrollArea = QScrollArea()
        mainScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        mainScrollArea.setWidgetResizable(True)
        mainScrollArea.setWidget(innerScrollArea)

        # ---------------- entryBtnLayout -------------------
        addEntryBtn = QPushButton("Add Entry")
        addEntryBtn.setIcon(QIcon("plus_icon.png"))
        addEntryBtn.clicked.connect(self.add_entry)
        clearEntryBtn = QPushButton("Clear All")
        clearEntryBtn.setIcon(QIcon("minus_icon.png"))
        clearEntryBtn.clicked.connect(self.remove_all_entries)

        # TODO Add sort button
        entryBtnLayout = QHBoxLayout()
        entryBtnLayout.addWidget(addEntryBtn)
        entryBtnLayout.addWidget(clearEntryBtn)

        # ---------------- centreLayout ---------------------
        centreLayout = QVBoxLayout()
        centreLayout.addLayout(headerLayout)
        centreLayout.addWidget(mainScrollArea)
        centreLayout.addLayout(entryBtnLayout)
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

    def add_entry(self):
        self.specifiedParamsList.insert(0, ParamWidget())
        self.specifiedParamsList[0].removeBtn.clicked.connect(self.remove_entry)
        self.paramComboLayout.insertWidget(0, self.specifiedParamsList[0])

    def remove_entry(self):
        sender_object = self.sender().parentWidget()
        self.specifiedParamsList.remove(sender_object)

    def remove_all_entries(self):
        choice = QMessageBox.question(self, "Confirm Clear All",
                                      "\nClear all entries?",
                                      QMessageBox.Yes, QMessageBox.No)
        if choice == QMessageBox.Yes:
            # First entry of list progressively removed, keep referencing first element
            for i in range(len(self.specifiedParamsList)):
                self.specifiedParamsList[0].removeBtn.click()

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

        self.paramName = None
        self.requiredValue = None
        self.rangeLow = None
        self.rangeHigh = None

        # ===================================================
        # # TODO Disable scrolling? Actually somewhat complicated
        self.paramComboBox = QComboBox()
        self.paramComboBox.addItems(ParamWidget._paramList["Name"])

        paramNameList = QStringListModel()
        paramNameList.setStringList(ParamWidget._paramList["Name"])
        self.paramCompleter = QCompleter()
        self.paramCompleter.setModel(paramNameList)

        self.paramLineEdit = QLineEdit()
        self.paramLineEdit.setCompleter(self.paramCompleter)
        # ---------------------------------------------------
        # Probably go for QDoubleSpinBox
        self.reqValLineEdit = QDoubleSpinBox()
        self.reqValLineEdit.setMaximumWidth(115)
        self.reqValLineEdit.setMinimum(-1000)  # or setRange(min, max)
        self.reqValLineEdit.setSingleStep(0.01)

        # ---------------------------------------------------
        self.rangeLowLineEdit = QDoubleSpinBox()
        self.rangeLowLineEdit.setMaximumWidth(100)
        self.rangeHighLineEdit = QDoubleSpinBox()
        self.rangeHighLineEdit.setMaximumWidth(100)

        self.removeBtn = QPushButton()
        self.removeBtn.setIcon(QIcon("minus_icon.png"))
        self.removeBtn.setMaximumWidth(35)
        self.removeBtn.setFlat(True)
        self.removeBtn.clicked.connect(self.remove_self)

        # ===================================================
        layout = QHBoxLayout()
        layout.addWidget(self.paramComboBox)
        layout.addWidget(self.reqValLineEdit)
        layout.addWidget(self.rangeLowLineEdit)
        layout.addWidget(self.rangeHighLineEdit)
        layout.addWidget(self.removeBtn)
        self.setLayout(layout)

    def remove_self(self):
        self.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
