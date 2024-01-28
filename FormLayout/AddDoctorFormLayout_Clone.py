from PyQt6 import QtCore
from FormLayout.AddFormLayout_Clone import AddFormLayoutClone
from SQL import executeScript, getLastRowInsertID



class AddDoctorFormLayoutClone(AddFormLayoutClone):
    """Edit base QFormLayout."""
    itemAddedSignal = QtCore.pyqtSignal(int)

    def __init__(self, mainUI, table, ID):
        super().__init__(mainUI,table,ID)


    def getSaveSql(self):
        sql1 = None
        d = self.getEntriesDic()
        if d:
            #the main query adding the doctor
            columns = ",\n".join([key for key in d])
            if self.table['patientID']: columns = columns + ",\n" + "PATIENT_ID"
            columns = "(" + columns + ")"
            values = ",\n".join(["\"" + value + "\"" for key, value in d.items()])
            if self.table['patientID']: values = values + ",\n\"" + str(self.mainUI.patientID) + "\""
            values = "(" + values + ")"
            sql1 = "INSERT INTO\n" + self.table['name'] + "\n" + columns + "\nVALUES\n" + values
            sql1+=";\n" #end of first query

        return sql1

    def getSaveSql2(self):
        # the second query adding it to referring doctors
        sql2 = 'INSERT INTO REFERRING_DOCTORS (PATIENT_ID, DOCTOR_ID, USE) VALUES ({},{},1)'.format(
            self.mainUI.patientID, self.ID
        )
        return sql2

    def saveDataWidgets(self):
        # Save it to SQL
        result1 = executeScript(self.getSaveSql())
        if result1:
            self.ID=getLastRowInsertID('DOCTORS')
            result2=executeScript(self.getSaveSql2())
            if result2:
                self.itemAddedSignal.emit(self.ID)
                return result2
        return None

