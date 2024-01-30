from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QPushButton
from PyQt6 import QtCore
from PyQt6.uic import loadUi
from SQL import executeScriptsFromFile as RunScript, executeScript


from ListBoxes.ListBoxes import ListBoxSearchableWithPhoto
from FormLayout.EditFormLayout_Clone import EditFormLayoutClone

class DoctorsDialog(QDialog):
    def __init__(self,mainUI):
        super(DoctorsDialog, self).__init__(mainUI)
        loadUi('Dialogs/DoctorsDialog.ui', self)
        self.mainUI=mainUI

        self.table = {'name': 'DOCTORS',
                 'columns': ['Title', 'First_Name', 'Second_Name', 'Job_Title', 'Address', 'Post_Code', 'Country', 'Telephone',
                             'Email'],
                 'patientID': False}

        #seachable list with photo (it's a layout)
        self.searchableList=ListBoxSearchableWithPhoto(self.mainUI, 'DOCTORS')
        #edit form (it's a layout)
        self.editForm=EditFormLayoutClone(self.mainUI,self.table,self.searchableList.list.ID)

        #delete button
        delete_button=QPushButton();delete_button.setText('DELETE')
        delete_button.clicked.connect(self.deleteClicked)
        self.buttonBox.addButton(delete_button,QDialogButtonBox.ButtonRole.DestructiveRole)

        #connections
        self.buttonBox.accepted.connect(self.OKclicked)
        self.searchableList.list.itemChangedSignal.connect(self.doctorChanged)
        self.editForm.focusLossedSignal.connect(self.saveThis)

        #add the two layouts to the vertical layout
        self.verticalLayout.addLayout(self.searchableList)
        self.verticalLayout.addLayout(self.editForm)

    def saveThis(self):
        self.editForm.saveDataWidgets()
        self.editForm.itemChangedSignal.connect(self.searchableList.list.RowEditedSignalled)
        self.mainUI.updateDoctorItem(self.editForm.ID) #update the main GUI

    def addDoctorToPatient(self):
        # Button clicked to add this doctor to this patient's referring doctor
        result = None
        print(self.editForm.ID)
        if self.mainUI.patientID == -1 or self.editForm.ID == -1: return result
        # check not already there
        sql = 'SELECT DOCTOR_ID, PATIENT_ID FROM REFERRING_DOCTORS WHERE PATIENT_ID={} AND DOCTOR_ID={}'.format(
            self.mainUI.patientID, self.editForm.ID
        )
        result = executeScript(sql)
        length = len(result.fetchall())
        if result:
            if length == 0:
                result = RunScript('SQL/Add to Patient Doctor.sql', (self.mainUI.patientID, self.editForm.ID))
                if result: self.mainUI.deleteDoctorItem(self.editForm.ID)
        return result

    def OKclicked(self):
        print('ok')
        self.addDoctorToPatient()
        self.close()

    def deleteClicked(self):
        self.searchableList.list.deleteListItem()
        self.mainUI.deleteDoctorItem(self.editForm.ID)
    @QtCore.pyqtSlot(int)
    def doctorChanged(self,ID):
        #then move onto the next
        print('doctor changed: ', ID)
        self.editForm.ID=ID
        self.editForm.fillForm()
