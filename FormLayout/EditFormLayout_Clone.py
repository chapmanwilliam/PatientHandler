from PyQt6 import QtCore
from FormLayout.FormLayout_Base import FormLayoutBase

class EditFormLayoutClone(FormLayoutBase):
    """Edit base QFormLayout."""
    itemDeletedSignal = QtCore.pyqtSignal(int)

    def __init__(self, mainUI, table, ID):
        super().__init__(mainUI,table,ID)


    def getSaveSql(self):
        result = None
        d=self.getEntriesDic()
        if d:
            d.update({'USE':1})
            result = ",\n".join([key + "=\"" + value + "\"" for key, value in d.items()])
            result = "UPDATE " + self.table['name'] + "\nSET\n" + result + '\nWHERE ROWID=' + str(self.ID)
        return result

    def deleteThisItem(self):
        print('delete')
        self.itemDeletedSignal.emit(self.ID)

    def saveDataWidgets(self):
        result=super().saveDataWidgets()
        if result:
            self.itemChangedSignal.emit(self.ID)
        return result


