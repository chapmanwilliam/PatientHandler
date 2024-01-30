from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout
from PyQt6 import QtCore
from PyQt6.QtGui import *
from SQL import executeScriptsFromFile as RunScript

from Dialogs.FormDialog_Base import EditFormDialog
from Dialogs.AddFormDialog import AddFormDialog
from Dialogs.AddDoctorFormDialog import AddDoctorFormDialog
from ListBoxes.label_PhotoClone import label_PhotoClone


# This class loads results of SQL query into list box with id
class ListBox(QListWidget):
    itemChangedSignal = QtCore.pyqtSignal(int)

    def __init__(self, mainUI, type):
        super().__init__(mainUI)
        self.mainUI = mainUI
        self.type = type  # the type of listbox: Addresses, Telephones, Emails, RefDoctors etc

        self.ID = -1
        self.searchTerm = ""
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)

        self.itemClicked.connect(self.thisItemClicked)
        self.itemDoubleClicked.connect(self.listDblClicked)
        self.currentRowChanged.connect(self.listItemChanged)
        self.itemChanged.connect(self.listItemChanged)

        self.fillBox()
        self.actionList()

    def actionList(self):
        # Add
        self.actionAdd = QAction("Add...", self)
        self.actionAdd.triggered.connect(self.addListItem)
        self.addAction(self.actionAdd)
        # Add existing - for DOCTORS
        if self.type == "REFERRING_DOCTORS":
            self.actionAddExisting = QAction("Add existing...", self)
            self.actionAddExisting.triggered.connect(self.addExistingDoctor)
            self.addAction(self.actionAddExisting)
        # Edit
        self.actionEdit = QAction("Edit...", self)
        self.actionEdit.triggered.connect(self.editListItem)
        self.addAction(self.actionEdit)
        # Delete
        self.actionDelete = QAction("Delete...", self)
        self.actionDelete.triggered.connect(self.deleteListItem)
        self.addAction(self.actionDelete)

    def getTable(self):
        match self.type:
            case 'PATIENTS':
                table = {'name': 'PATIENTS',
                         'columns': ['First_Name', 'Second_Name', 'Title', 'Date_of_birth', 'NHS_no', 'Occupation'],
                         'patientID': False}
            case 'ADDRESSES':
                table = {'name': 'ADDRESSES',
                         'columns': ['Address', 'Post_Code', 'Country'],
                         'patientID': True}
            case 'EMAILS':
                table = {'name': 'EMAILS',
                         'columns': ['Email'],
                         'patientID': True}
            case 'TELEPHONES':
                table = {'name': 'TELEPHONES',
                         'columns': ['Telephone'],
                         'patientID': True}
            case 'REFERRING_DOCTORS':
                table = {'name': 'DOCTORS',
                         'columns': ['Title', 'First_Name', 'Second_Name', 'Job_Title',
                                     'Address', 'Post_Code', 'Country', 'Telephone', 'Email'],
                         'patientID': False}
            case 'DOCTORS':
                table = {'name': 'DOCTORS',
                         'columns': ['Title', 'First_Name', 'Second_Name', 'Job_Title',
                                     'Address', 'Post_Code', 'Country', 'Telephone', 'Email'],
                         'patientID': False}

            case other:
                print("No matching type found getting table: ", self.type)
                return None
        return table

    def addExistingDoctor(self):
        print('got here')
        self.mainUI.showDoctors()

    def addListItem(self):
        if self.mainUI.patientID == -1: return
        table = self.getTable()
        if not table: return
        if self.type == 'REFERRING_DOCTORS':
            addDialog = AddDoctorFormDialog(self.mainUI, table, self.ID)
        else:
            addDialog = AddFormDialog(self.mainUI, table, self.ID)
        addDialog.setWindowTitle("Add " + str.capitalize(self.type.replace('_', ' ')))
        addDialog.layout.itemAddedSignal.connect(self.RowAddedSignalled)
        addDialog.exec()

    def editListItem(self):
        if self.ID == -1: return
        table = self.getTable()
        if not table: return
        editDialog = EditFormDialog(self.mainUI, table, self.ID)
        editDialog.setWindowTitle("Edit " + str.capitalize(self.type.replace('_', ' ')))
        editDialog.layout.itemChangedSignal.connect(self.RowEditedSignalled)
        editDialog.layout.itemDeletedSignal.connect(self.deleteListItemSignalled)
        editDialog.exec()

    @QtCore.pyqtSlot(int)
    def RowAddedSignalled(self, ID):
        # This adds the row to the latest info from database
        self.ID = ID
        if ID == -1: return
        result = self.getSQLresult()
        if not result: return
        txt = ''
        for i in result:
            if i['ID'] == ID:
                txt = i['TXT']
                item = QListWidgetItem(txt)
                item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.CheckState.Checked)
                item.value = self.ID
                self.addItem(item)
                self.setCurrentItem(item)

    @QtCore.pyqtSlot(int)
    def RowEditedSignalled(self, ID):
        # This updates the row to the latest info from database
        print('Row Edited Signalled, ', ID)
        if ID == -1: return
        result = self.getSQLresult()
        if not result: return
        txt = ''
        for i in result:
            if i['ID'] == ID:
                txt = i['TXT']
                self.item(self.currentRow()).setText(txt)

    @QtCore.pyqtSlot(int)
    def deleteListItemSignalled(self, ID):
        print('deleteListitem signaled', ID)
        self.deleteListItem()

    def deleteListItem(self):
        result = None
        sql = None
        params = None
        if self.ID == -1: return result
        match self.type:
            case 'PATIENTS':
                sql = "SQL/Deletes/DeletePatient.sql"
                params = (self.ID,)
            case 'ADDRESSES':
                sql = "SQL/Deletes/DeleteAddress.sql"
                params = (self.ID,)
            case 'EMAILS':
                sql = "SQL/Deletes/DeleteEmail.sql"
                params = (self.ID,)
            case 'TELEPHONES':
                sql = "SQL/Deletes/DeleteTelephone.sql"
                params = (self.ID,)
            case 'REFERRING_DOCTORS':
                sql = "SQL/Deletes/DeleteReferringDoctor.sql"
                params = (self.mainUI.patientID, self.ID)
            case 'DOCTORS':
                sql = "SQL/Deletes/DeleteDoctor.sql"
                params = (self.ID,)
            case other:
                print("No matching type found deleting: ", self.type)
                return result
        result = RunScript(sql, params)

        self.fillBox()
        return result

    def listDblClicked(self, item):
        self.editListItem()

    def getCheckedStatus(self, item):
        if item.checkState() == QtCore.Qt.CheckState.Checked:
            return 1
        else:
            return 0

    def thisItemClicked(self, item):
        print("Item clicked: ", item.value)
        if item.value > 0:
            self.ID = item.value
            result = self.updateCheckedStatus(self.getCheckedStatus(item), item)
            self.itemChangedSignal.emit(self.ID)

    def listItemChanged(self):
        items = self.selectedItems()
        if len(items) > 0:
            self.ID = items[0].value
        print('list item changed:', self.ID)
        self.itemChangedSignal.emit(self.ID)

    def updateCheckedStatus(self, checkedStatus, item):
        result = None
        sql = None
        params = None
        if self.mainUI.patientID == -1 and self.type != "PATIENTS": return result
        match self.type:
            case 'PATIENTS':
                sql = "SQL/UpdateCheckBoxes/UpdatePatientsUsed.sql"
                params = (checkedStatus, self.ID,)
            case 'ADDRESSES':
                sql = "SQL/UpdateCheckBoxes/UpdateAddressesUsed.sql"
                params = (checkedStatus, self.mainUI.patientID, self.ID)
            case 'EMAILS':
                sql = "SQL/UpdateCheckBoxes/UpdateEmailsUsed.sql"
                params = (checkedStatus, self.mainUI.patientID, self.ID)
            case 'TELEPHONES':
                sql = "SQL/UpdateCheckBoxes/UpdateTelephonesUsed.sql"
                params = (checkedStatus, self.mainUI.patientID, self.ID)
            case 'REFERRING_DOCTORS':
                sql = "SQL/UpdateCheckBoxes/UpdateReferringDoctorsUsed.sql"
                params = (checkedStatus, self.mainUI.patientID, self.ID)
            case "DOCTORS":
                sql = "SQL/UpdateCheckBoxes/UpdateDoctorsUsed.sql"
                params = (checkedStatus, self.ID)
            case other:
                print("No matching type found updating check box: ", self.type)
                return result
        result = RunScript(sql, params)
        return result

    def fillBox(self):
        self.clear()
        self.ID = -1
        result = self.getSQLresult()
        if not result:
            print('no results')
            self.currentRowChanged.emit(-1)
            return
        for i in result:
            item = QListWidgetItem(i['TXT'])
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            if i['USE'] == 1:
                item.setCheckState(QtCore.Qt.CheckState.Checked)
            else:
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            item.value = i['ID']
            self.addItem(item)
        self.setCurrentRow(0)
        self.listItemChanged()

    def getSQLresult(self):
        # These sql should return ROWID, DISPLAY_TEXT, USE (for checkbox)
        result = None
        sql = None
        params = None
        if self.mainUI.patientID == -1 and (self.type != "PATIENTS" and self.type != 'DOCTORS'): return result
        match self.type:
            case 'PATIENTS':
                sql = "SQL/Patients lists/Patients Containing.sql"
                params = (self.searchTerm,)
            case 'ADDRESSES':
                sql = 'SQL/Patients lists/Addresses Patient.sql'
                params = (self.mainUI.patientID,)
            case 'TELEPHONES':
                sql = 'SQL/Patients lists/Telephones Patient.sql'
                params = (self.mainUI.patientID,)
            case 'EMAILS':
                sql = "SQL/Patients lists/Emails Patient.sql"
                params = (self.mainUI.patientID,)
            case 'REFERRING_DOCTORS':
                sql = "SQL/Patients lists/Referring Doctors Patient.sql"
                params = (self.mainUI.patientID,)
            case "DOCTORS":
                sql = "SQL/Patients lists/Doctors Containing.sql"
                params = (self.searchTerm,)
            case "LETTERS":
                sql = "SQL/Patients lists/Letters.sql"
                params = (self.searchTerm,)
            case other:
                print('No matching type found loading: ', self.type)
                return result

        result = RunScript(sql, params)
        return result
class ListBoxPatients(ListBox):

    def __init__(self, mainUI, type):
        super().__init__(mainUI, type)
        self.mainUI = mainUI
        self.type = 'PATIENTS'  # the type of listbox: Addresses, Telephones, Emails, RefDoctors etc

    def getTable(self):
        table = {'name': 'PATIENTS',
                 'columns': ['First_Name', 'Second_Name', 'Title', 'Date_of_birth', 'NHS_no', 'Occupation'],
                 'patientID': False}
        return table

    def deleteListItem(self):
        result = None
        sql = None
        params = None
        if self.ID == -1: return result
        sql = "SQL/Deletes/DeletePatient.sql"
        params = (self.ID,)
        result = RunScript(sql, params)
        return result

    def updateCheckedStatus(self, checkedStatus, item):
        result = None
        sql = None
        params = None
        sql = "SQL/UpdateCheckBoxes/UpdatePatientsUsed.sql"
        params = (checkedStatus, self.ID,)
        result = RunScript(sql, params)
        return result

    def getSQLresult(self):
        result = None
        sql = None
        params = None
        sql = "SQL/Patients lists/Patients Containing.sql"
        params = (self.searchTerm,)
        result = RunScript(sql, params)
        return result
class ListBoxAddresses(ListBox):

    def __init__(self, mainUI, type):
        super().__init__(mainUI, type)
        self.mainUI = mainUI
        self.type = 'ADDRESSES'  # the type of listbox: Addresses, Telephones, Emails, RefDoctors etc

    def getTable(self):
        table = {'name': 'ADDRESSES',
                 'columns': ['Address', 'Post_Code', 'Country'],
                 'patientID': True}
        return table

    def deleteListItem(self):
        result = None
        sql = None
        params = None
        if self.ID == -1: return result
        sql = "SQL/Deletes/DeleteAddress.sql"
        params = (self.ID,)
        result = RunScript(sql, params)
        return result

    def updateCheckedStatus(self, checkedStatus, item):
        result = None
        sql = None
        params = None
        sql = "SQL/UpdateCheckBoxes/UpdateAddressesUsed.sql"
        params = (checkedStatus, self.ID,)
        params = (checkedStatus, self.mainUI.patientID, self.ID)
        return result

    def getSQLresult(self):
        result = None
        sql = None
        params = None
        sql = "SQL/Patients lists/Addresses Patient.sql"
        params = (self.searchTerm,)
        result = RunScript(sql, params)
        return result
class ListBoxEmails(ListBox):

    def __init__(self, mainUI, type):
        super().__init__(mainUI, type)
        self.mainUI = mainUI
        self.type = 'EMAILS'  # the type of listbox: Addresses, Telephones, Emails, RefDoctors etc

    def getTable(self):
        table = {'name': 'EMAILS',
                 'columns': ['Email'],
                 'patientID': True}
        return table

    def deleteListItem(self):
        result = None
        sql = None
        params = None
        if self.ID == -1: return result
        sql = "SQL/Deletes/DeleteEmail.sql"
        params = (self.ID,)
        result = RunScript(sql, params)
        return result

    def updateCheckedStatus(self, checkedStatus, item):
        result = None
        sql = None
        params = None
        sql = "SQL/UpdateCheckBoxes/UpdateEmailsUsed.sql"
        params = (checkedStatus, self.mainUI.patientID, self.ID)
        result = RunScript(sql, params)
        return result

    def getSQLresult(self):
        result = None
        sql = None
        params = None
        sql = "SQL/Patients lists/Emails Patient.sql"
        params = (self.mainUI.patientID,)
        result = RunScript(sql, params)
        return result
class ListBoxTelephones(ListBox):

    def __init__(self, mainUI, type):
        super().__init__(mainUI, type)
        self.mainUI = mainUI
        self.type = 'TELEPHONES'  # the type of listbox: Addresses, Telephones, Emails, RefDoctors etc

    def getTable(self):
        table = {'name': 'TELEPHONES',
                 'columns': ['Telephone'],
                 'patientID': True}
        return table

    def deleteListItem(self):
        result = None
        sql = None
        params = None
        if self.ID == -1: return result
        sql = "SQL/Deletes/DeleteTelephone.sql"
        params = (self.ID,)
        result = RunScript(sql, params)
        return result

    def updateCheckedStatus(self, checkedStatus, item):
        result = None
        sql = None
        params = None
        sql = "SQL/UpdateCheckBoxes/UpdateTelephonesUsed.sql"
        params = (checkedStatus, self.mainUI.patientID, self.ID)
        result = RunScript(sql, params)
        return result

    def getSQLresult(self):
        result = None
        sql = None
        params = None
        sql = "SQL/Patients lists/Telephones Patient.sql"
        params = (self.mainUI.patientID,)
        result = RunScript(sql, params)
        return result
class ListBoxReferringDoctors(ListBox):

    def __init__(self, mainUI, type):
        super().__init__(mainUI, type)
        self.mainUI = mainUI
        self.type = 'REFERRING_DOCTORS'  # the type of listbox: Addresses, Telephones, Emails, RefDoctors etc

    def getTable(self):
        table = {'name': 'DOCTORS',
                 'columns': ['Title', 'First_Name', 'Second_Name', 'Job_Title',
                             'Address', 'Post_Code', 'Country', 'Telephone', 'Email'],
                 'patientID': False}
        return table

    def deleteListItem(self):
        result = None
        sql = None
        params = None
        if self.ID == -1: return result
        sql = "SQL/Deletes/DeleteReferringDoctor.sql"
        params = (self.mainUI.patientID, self.ID)
        result = RunScript(sql, params)
        return result

    def updateCheckedStatus(self, checkedStatus, item):
        result = None
        sql = None
        params = None
        sql = "SQL/UpdateCheckBoxes/UpdateReferringDoctorsUsed.sql"
        params = (checkedStatus, self.mainUI.patientID, self.ID)
        result = RunScript(sql, params)
        return result

    def getSQLresult(self):
        result = None
        sql = None
        params = None
        sql = "SQL/Patients lists/Referring Doctors Patient.sql"
        params = (self.mainUI.patientID,)
        result = RunScript(sql, params)
        return result
class ListBoxSearchable(QVBoxLayout):
    def __init__(self, mainUI, type):
        super().__init__()
        self.mainUI = mainUI
        self.type = type  # the type of listbox: Addresses, Telephones, Emails, RefDoctors etc

        # LineEditor
        self.lnEdit = QLineEdit(self.mainUI)
        f = self.lnEdit.font()
        f.setPointSize(27)  # sets the size to 27
        self.lnEdit.setFont(f)
        self.lnEdit.setPlaceholderText("Search")

        # This class loads results of SQL query into list box with id
        # ID label
        self.labelID = QLabel(self.mainUI)
        f = self.labelID.font()
        f.setPointSize(27)  # sets the size to 27
        self.labelID.setFont(f)
        self.labelID.setText('ID: ')

        # ID lineedit
        self.lnEditID = QLineEdit(self.mainUI)
        f = self.lnEditID.font()
        f.setPointSize(27)  # sets the size to 27
        self.lnEditID.setFont(f)
        self.lnEditID.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.lnEditID.setPlaceholderText("ID")

        # the list box
        self.setListBox()

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.lnEdit)
        hlayout1.addWidget(self.labelID)
        hlayout1.addWidget(self.lnEditID)

        self.hlayout2 = QHBoxLayout()
        self.hlayout2.addWidget(self.list)

        # add the widgets
        self.addLayout(hlayout1)
        self.addLayout(self.hlayout2)

        # connections
        self.lnEdit.textChanged.connect(self.lnEditChanged)
        self.lnEditID.textChanged.connect(self.lnEditIDChanged)

        self.list.itemClicked.connect(self.setID)
        self.list.itemDoubleClicked.connect(self.setID)
        self.list.currentRowChanged.connect(self.setID)
        self.list.itemChangedSignal.connect(self.setID)

    def setListBox(self):
        self.list = ListBox(self.mainUI, type)
        self.list.setMaximumHeight(100)
        self.list.setMinimumHeight(100)

    def setID(self):
        print('setting ID')
        if self.list.ID == -1:
            self.lnEditID.setText('')
        else:
            self.lnEditID.setText(str(self.list.ID).zfill(6))

    def lnEditChanged(self):
        self.list.searchTerm = self.lnEdit.text()
        self.list.fillBox()

    def lnEditIDChanged(self):
        pass
class ListBoxSearchableWithPhoto(ListBoxSearchable):
    def __init__(self, mainUI, type):
        super().__init__(mainUI, type)
        self.mainUI = mainUI
        self.type = type  # the type of listbox: Addresses, Telephones, Emails, RefDoctors etc

        self.photo = label_PhotoClone(self.mainUI, self.type)
        self.hlayout2.addWidget(self.photo)

    def setID(self):
        super().setID()
        self.photo.ID = self.list.ID
        self.photo.fillPhoto()


class ListBoxSearchablePatients(ListBoxSearchable):
    def __init__(self, mainUI, type):
        super().__init__(mainUI, type)

    def setListBox(self):
        self.list = ListBoxPatients(self.mainUI, type)
        self.list.setMaximumHeight(100)
        self.list.setMinimumHeight(100)


class ListBoxSearchablePatientsWithPhoto(ListBoxSearchablePatients):
    def __init__(self, mainUI, type):
        super().__init__(mainUI, type)
        self.mainUI = mainUI
        self.type = type  # the type of listbox: Addresses, Telephones, Emails, RefDoctors etc

        self.photo = label_PhotoClone(self.mainUI, self.type)
        self.hlayout2.addWidget(self.photo)

    def setID(self):
        super().setID()
        self.photo.ID = self.list.ID
        self.photo.fillPhoto()
