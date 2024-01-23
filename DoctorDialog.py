from PyQt6.QtWidgets import QDialog, QLineEdit
from PyQt6.uic import loadUi
from SQL import executeScriptsFromFile as RunScript, getLastRowInsertID
from EditDialogBase import EditDialog

class DoctorDialog(EditDialog):
    """Doctor dialog."""
    def __init__(self, parent, doctorID, ui):
        super().__init__(parent,doctorID,ui)
        self.loadText()

    def getdicData(self):
        d = {}
        for w in self.findChildren(QLineEdit):
            d.update({w.objectName(): w.text()})
        print(d)
        return d

    def add(self):
        #This adds a new doctor and makes that doctor one of this patients doctors
        result = RunScript("SQL/AddDoctor.sql") #Add a blank doctor
        if not result: return
        self.pushButton_ADD.setEnabled(False)
        self.ID=getLastRowInsertID('DOCTORS')
        result = RunScript("SQL/AddReferringDoctor.sql",(self.parent.patientID,self.ID))  # Add a referring doctor
        if not result: return
        self.loadText()
        self.parent.fillDoctors()
    def delete(self):
        result = RunScript("SQL/DeleteReferringDoctor.sql",(self.parent.patientID, self.ID,))
        if not result: return
        self.parent.fillDoctors()
        self.close()
    def save(self):
        d=self.getdicData()
        result = RunScript("SQL/UpdateDoctor.sql", (d['lineEditTitle'],
                                                 d['lineEditFirstName'],
                                                 d['lineEditSecondName'],
                                                 d['lineEditAddress'],
                                                 d['lineEditPostCode'],
                                                 d['lineEditCountry'],
                                                 d['lineEditTelephone'],
                                                 d['lineEditJobTitle'],
                                                    d['lineEditEmail'],
                                                 self.ID))
        self.parent.fillDoctors()

    def loadText(self):
        result = RunScript("SQL/GetDoctor.sql", (self.ID,)).fetchone()
        self.lineEditTitle.setText(result['Title'])
        self.lineEditFirstName.setText(result['FirstName'])
        self.lineEditSecondName.setText(result['SecondName'])
        self.lineEditAddress.setText(result['Address'])
        self.lineEditPostCode.setText(result['PostCode'])
        self.lineEditCountry.setText(result['Country'])
        self.lineEditTelephone.setText(result['TelNo'])
        self.lineEditJobTitle.setText(result['Job_Title'])
        self.lineEditEmail.setText(result['Email'])
