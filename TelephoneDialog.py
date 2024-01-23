from PyQt6.QtWidgets import QDialog, QLineEdit
from PyQt6.uic import loadUi
from SQL import executeScriptsFromFile as RunScript, getLastRowInsertID
from EditDialogBase import EditDialog

class TelephoneDialog(EditDialog):
    """Telephone dialog."""
    def __init__(self, parent, telID, ui):
        super().__init__(parent,telID,ui)
        self.loadText()


    def getdicData(self):
        d = {}
        for w in self.findChildren(QLineEdit):
            d.update({w.objectName(): w.text()})
        print(d)
        return d

    def add(self):
        #This adds a new doctor and makes that doctor one of this patients doctors
        result = RunScript("SQL/AddTelephone.sql",(self.parent.patientID,)) #Add a blank address
        if not result: return
        self.pushButton_ADD.setEnabled(False)
        self.ID=getLastRowInsertID('TEL_NOS')
        self.loadText()
        self.parent.fillTel()
    def delete(self):
        result = RunScript("SQL/DeleteTelephone.sql",(self.ID,))
        if not result: return
        self.parent.fillTel()
        self.close()
    def save(self):
        d=self.getdicData()
        result = RunScript("SQL/UpdateTelephone.sql", (
                                                     self.parent.patientID,
                                                     d['lineEditTelephone'],
                                                     1,
                                                 self.ID))
        self.parent.fillTel()

    def loadText(self):
        result = RunScript("SQL/GetTelephone.sql", (self.ID,)).fetchone()
        if result == None: return
        self.lineEditTelephone.setText(result['TEL_NO'])
