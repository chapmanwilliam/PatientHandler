from PyQt6.QtWidgets import QDialog, QLineEdit
from PyQt6.uic import loadUi
from SQL import executeScriptsFromFile as RunScript, getLastRowInsertID
from EditDialogBase import EditDialog

class AddressDialog(EditDialog):
    """Address dialog."""
    def __init__(self, parent, addressID, ui):
        super().__init__(parent,addressID,ui)
        self.loadText()


    def getdicData(self):
        d = {}
        for w in self.findChildren(QLineEdit):
            d.update({w.objectName(): w.text()})
        print(d)
        return d

    def add(self):
        #This adds a new doctor and makes that doctor one of this patients doctors
        result = RunScript("SQL/AddAddress.sql",(self.parent.patientID,)) #Add a blank address
        if not result: return
        self.pushButton_ADD.setEnabled(False)
        self.ID=getLastRowInsertID('ADDRESSES')
        self.loadText()
        self.parent.fillAddresses()
    def delete(self):
        result = RunScript("SQL/DeleteAddress.sql",(self.ID,))
        if not result: return
        self.parent.fillAddresses()
        self.close()
    def save(self):
        d=self.getdicData()
        result = RunScript("SQL/UpdateAddress.sql", (d['lineEditAddress'],
                                                 d['lineEditPostCode'],
                                                 d['lineEditCountry'],
                                                     self.parent.patientID,
                                                     1,
                                                 self.ID))
        self.parent.fillAddresses()

    def loadText(self):
        result = RunScript("SQL/GetAddress.sql", (self.ID,)).fetchone()
        self.lineEditAddress.setText(result['Address'])
        self.lineEditPostCode.setText(result['POST_CODE'])
        self.lineEditCountry.setText(result['COUNTRY'])
