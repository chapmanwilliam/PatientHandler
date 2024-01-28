from PyQt6 import QtCore
from FormLayout.FormLayout_Base import FormLayoutBase
from SQL import getLastRowInsertID


class AddFormLayoutClone(FormLayoutBase):
    """Edit base QFormLayout."""
    itemAddedSignal = QtCore.pyqtSignal(int)

    def __init__(self, mainUI, table, ID):
        super().__init__(mainUI,table,ID)


    def getSaveSql(self):
        result = None
        d = self.getEntriesDic()
        if d:
            columns = ",\n".join([key for key in d])
            if self.table['patientID']: columns = columns + ",\n" + "PATIENT_ID"
            columns = "(" + columns + "\n,USE)"
            values = ",\n".join(["\"" + value + "\"" for key, value in d.items()])
            if self.table['patientID']: values = values + ",\n\"" + str(self.mainUI.patientID) + "\""
            values = "(" + values + "\n,1)"
            result = "INSERT INTO\n" + self.table['name'] + "\n" + columns + "\nVALUES\n" + values
        print(result)
        return result

    def loadWidgets(self):
        self.filled=False
        super().loadWidgets()

    def saveDataWidgets(self):
        result=super().saveDataWidgets()
        if result:
            self.ID=getLastRowInsertID(self.table['name'])
            self.itemAddedSignal.emit(self.ID)
        return result

