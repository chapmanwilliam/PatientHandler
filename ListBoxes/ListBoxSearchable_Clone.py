from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLineEdit, QLabel
from ListBoxes.ListBox_Clone import ListBox_Clone
from PyQt6 import QtCore


# This class loads results of SQL query into list box with id
class ListBoxSearchable_Clone(QVBoxLayout):
    def __init__(self, mainUI, type):
        super().__init__()
        self.mainUI = mainUI
        self.type = type  # the type of listbox: Addresses, Telephones, Emails, RefDoctors etc

        #LineEditor
        self.lnEdit=QLineEdit(self.mainUI)
        f = self.lnEdit.font()
        f.setPointSize(27)  # sets the size to 27
        self.lnEdit.setFont(f)
        self.lnEdit.setPlaceholderText("Search")

        #ID label
        self.labelID=QLabel(self.mainUI)
        f = self.labelID.font()
        f.setPointSize(27)  # sets the size to 27
        self.labelID.setFont(f)
        self.labelID.setText('ID: ')

        #ID lineedit
        self.lnEditID=QLineEdit(self.mainUI)
        f = self.lnEditID.font()
        f.setPointSize(27)  # sets the size to 27
        self.lnEditID.setFont(f)
        self.lnEditID.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.lnEditID.setPlaceholderText("ID")

        #the list box
        self.list=ListBox_Clone(self.mainUI,type)
        self.list.setMaximumHeight(100)
        self.list.setMinimumHeight(100)


        hlayout1=QHBoxLayout()
        hlayout1.addWidget(self.lnEdit)
        hlayout1.addWidget(self.labelID)
        hlayout1.addWidget(self.lnEditID)

        self.hlayout2=QHBoxLayout()
        self.hlayout2.addWidget(self.list)

        #add the widgets
        self.addLayout(hlayout1)
        self.addLayout(self.hlayout2)

        #connections
        self.lnEdit.textChanged.connect(self.lnEditChanged)
        self.lnEditID.textChanged.connect(self.lnEditIDChanged)

        self.list.itemClicked.connect(self.setID)
        self.list.itemDoubleClicked.connect(self.setID)
        self.list.currentRowChanged.connect(self.setID)
        self.list.itemChangedSignal.connect(self.setID)

    def setID(self):
        print('setting ID')
        if self.list.ID==-1:
            self.lnEditID.setText('')
        else:
            self.lnEditID.setText(str(self.list.ID).zfill(6))

    def lnEditChanged(self):
        self.list.searchTerm=self.lnEdit.text()
        self.list.fillBox()

    def lnEditIDChanged(self):
        pass



