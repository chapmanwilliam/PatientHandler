from PyQt6.QtWidgets import QDialog, QLineEdit
from PyQt6.uic import loadUi
from SQL import executeScriptsFromFile as RunScript, getLastRowInsertID
from EditDialogBase import EditDialog

class EmailDialog(EditDialog):
    """Email dialog."""
    def __init__(self, parent, emailID, ui):
        super().__init__(parent,emailID,ui)
        self.loadText()


    def getdicData(self):
        d = {}
        for w in self.findChildren(QLineEdit):
            d.update({w.objectName(): w.text()})
        print(d)
        return d

    def add(self):
        #This adds a new doctor and makes that doctor one of this patients doctors
        result = RunScript("SQL/AddEmail.sql",(self.parent.patientID,)) #Add a blank address
        if not result: return
        self.pushButton_ADD.setEnabled(False)
        self.ID=getLastRowInsertID('EMAILS')
        self.loadText()
        self.parent.fillEmails()
    def delete(self):
        result = RunScript("SQL/DeleteEmail.sql",(self.ID,))
        if not result: return
        self.parent.fillEmails()
        self.close()
    def save(self):
        d=self.getdicData()
        result = RunScript("SQL/UpdateEmail.sql", (d['lineEditEmail'],
                                                     self.parent.patientID,
                                                     1,
                                                 self.ID))
        self.parent.fillEmails()

    def loadText(self):
        result = RunScript("SQL/GetEmail.sql", (self.ID,)).fetchone()
        self.lineEditEmail.setText(result['Email'])
