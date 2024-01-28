from ListBoxes.ListBoxSearchable_Clone import ListBoxSearchable_Clone
from ListBoxes.label_PhotoClone import label_PhotoClone

# This class loads results of SQL query into list box with id
class ListBoxSearchable_CloneWithPhoto(ListBoxSearchable_Clone):
    def __init__(self, mainUI, type):
        super().__init__(mainUI,type)
        self.mainUI = mainUI
        self.type = type  # the type of listbox: Addresses, Telephones, Emails, RefDoctors etc

        self.photo=label_PhotoClone(self.mainUI,self.type)
        self.hlayout2.addWidget(self.photo)

    def setID(self):
        super().setID()
        self.photo.ID=self.list.ID
        self.photo.fillPhoto()




