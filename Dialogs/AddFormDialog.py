from Dialogs.FormDialog_Base import FormDialogBase
from FormLayout.AddFormLayout_Clone import AddFormLayoutClone

class AddFormDialog(FormDialogBase):

    def __init__(self, parent,table,ID):
        super(AddFormDialog, self).__init__(parent,table,ID)


    def createLayout(self):
        self.layout = AddFormLayoutClone(self.mainUI,self.table,self.ID)




