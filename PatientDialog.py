from PyQt6.QtWidgets import QDialog, QLineEdit
from PyQt6 import QtCore
from PyQt6.uic import loadUi
from SQL import executeScriptsFromFile as RunScript, getLastRowInsertID
from EditDialogBase import EditDialog
from datetime import datetime

class PatientDialog(EditDialog):
    """Patient dialog."""
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
        #This adds a new Patient and makes that Patient one of this patients doctors
        result = RunScript("SQL/AddPatient.sql") #Add a blank Patient
        if not result: return
        self.pushButton_ADD.setEnabled(False)
        self.ID=getLastRowInsertID('Patients')
        self.parent.patientID=self.ID
        self.loadText()
        self.parent.fillPatients()
    def delete(self):
        result = RunScript("SQL/DeletePatient.sql",(self.parent.patientID,))
        if not result: return
        self.parent.refresh()
        self.close()
    def save(self):
        d=self.getdicData()
        result = RunScript("SQL/UpdatePatient.sql", (d['lineEditFirstName'],
                                                 d['lineEditSecondName'],
                                                 d['lineEditTitle'],
                                                 self.dateEditDOB.date().toString("yyyy-MM-dd"),
                                                 d['lineEditNHSNO'],
                                                 d['lineEditOccupation'],
                                                 self.ID))
        self.parent.fillPatients()

    def loadText(self):
        result = RunScript("SQL/GetPatient.sql", (self.ID,)).fetchone()
        qD = QtCore.QDate.fromString(result['DOB'], "yyyy-MM-dd")
        self.lineEditTitle.setText(result['Title'])
        self.lineEditFirstName.setText(result['FirstName'])
        self.lineEditSecondName.setText(result['SecondName'])
        self.dateEditDOB.setDate(qD)
        self.lineEditOccupation.setText(result['Occupation'])
        self.lineEditNHSNO.setText(result['NHS_NO'])
