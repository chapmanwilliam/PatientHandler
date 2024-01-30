from PyQt6.QtWidgets import QDialog, QDialogButtonBox
from PyQt6 import QtCore

from FormLayout.EditFormLayout_Clone import EditFormLayoutClone

class FormDialogBase(QDialog):

    def __init__(self, mainUI,table,ID):
        super(FormDialogBase, self).__init__()
        self.mainUI=mainUI
        self.table=table
        self.ID=ID

        self.setWindowTitle("My Form")
        self.resize(400,300)


        #Button box
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        # Create layout and add widgets
        self.createLayout()
        self.layout.addWidget(self.buttonBox)
        # Set dialog layout
        self.setLayout(self.layout)
        # Add button signal
        self.buttonBox.accepted.connect(self.OKclicked)
        self.buttonBox.rejected.connect(self.CancelClicked)

    def createLayout(self):
        self.layout = EditFormLayoutClone(self.mainUI,self.table,self.ID)

    def OKclicked(self):
        self.layout.saveDataWidgets()
        self.close()

    def CancelClicked(self):
        self.close()

    def DeleteClicked(self):
        self.layout.deleteThisItem()
        self.close()

class EditFormDialog(FormDialogBase):

    def __init__(self, parent,table,ID):
        super(EditFormDialog, self).__init__(parent,table,ID)


    def createLayout(self):
        self.layout = EditFormLayoutClone(self.mainUI,self.table,self.ID)



