from PyQt6.QtWidgets import QDialog, QLineEdit
from PyQt6.uic import loadUi
from SQL import executeScriptsFromFile as RunScript, getLastRowInsertID

class EditDialog(QDialog):
    """Edit base dialog."""
    def __init__(self, parent, ID, ui):
        super().__init__(parent)
        self.ui=ui
        self.ID=ID
        self.parent=parent
        # Load the dialog's GUI
        loadUi(self.ui, self)
        self.loadText()

        self.pushButton_SAVE.clicked.connect(self.save)
        self.pushButton_OK.clicked.connect(self.OK)
        self.pushButton_DELETE.clicked.connect(self.delete)
        self.pushButton_ADD.clicked.connect(self.add)

        if ID==-1: self.add()

    def getdicData(self):
        d = {}
        for w in self.findChildren(QLineEdit):
            d.update({w.objectName(): w.text()})
        print(d)
        return d

    def add(self):
        pass


    def delete(self):
        pass

    def OK(self):
        self.save()
        self.close()
    def save(self):
        pass

    def loadText(self):
        pass
