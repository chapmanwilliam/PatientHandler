from Dialogs.FormDialog_Base import FormDialogBase
from FormLayout.FormLayout_Base import AddDoctorFormLayoutClone

class AddDoctorFormDialog(FormDialogBase):

    def __init__(self, parent,table,ID):
        super(AddDoctorFormDialog, self).__init__(parent,table,ID)


    def createLayout(self):
        self.layout = AddDoctorFormLayoutClone(self.mainUI,self.table,self.ID)




