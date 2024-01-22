from PyQt6.QtWidgets import QMainWindow, QApplication, QListWidgetItem, QListWidget, QDialog, QLineEdit
from PyQt6.uic import loadUi
from PyQt6.QtCore import QSortFilterProxyModel, Qt
import sys
import os, subprocess, platform
from os import sep
from datetime import datetime
import dropbox as Dropbox
from dropbox.exceptions import ApiError
from dropbox.files import WriteMode
from pathlib import Path
import shutil
from SQL import executeScriptsFromFile as RunScript
from docxtpl import DocxTemplate
import json
from DoctorDialog import DoctorDialog

INFO_PATHS = ["%APPDATA%\Dropbox\info.json",
              "%LOCALAPPDATA%\Dropbox\info.json", " ~/.dropbox/info.json"]

APP_PATH = "/Apps/Patient Handler"



class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        loadUi('MainWindow.ui', self)

        # Letter buttons
        self.pushButton_LetterNew.clicked.connect(self.NewLetter)
        self.pushButton_LetterFollowUp.clicked.connect(self.FollowUpLetter)
        self.pushButton_LetterPrescription.clicked.connect(self.PrescriptionLetter)

        self.lineEditName.textChanged.connect(self.sync_lineEdit)
        self.listWidgetPatients.clicked.connect(self.listPatientsClicked)
        self.comboBoxLocation.activated.connect(self.ComboBoxLocationsChanged)

        self.listWidgetReferringDoctors.itemClicked.connect(self.listReferringDoctorsChanged)
        self.listWidgetAddresses.itemClicked.connect(self.listAddressesChanged)
        self.listWidgetEmails.itemClicked.connect(self.listEmailsChanged)
        self.listWidgetTel.itemClicked.connect(self.listTelsChanged)

        self.listWidgetReferringDoctors.itemDoubleClicked.connect(self.listReferringDoctorsDblClicked)



        self.patientID = -1
        self.locationID = -1
        self.dbx = Dropbox.Dropbox(
            'ABC')

        self.fillListBox()
        self.fillComboBoxLocations()

    def refreshMain(self):
        self.fillAddresses()
        self.fillEmails()
        self.fillDoctors()
        self.fillTel()

    def getPatientFolder(self):
        if self.patientID == -1: return None
        items = self.listWidgetPatients.selectedItems()
        if len(items) > 0:
            name = items[0].data(0)
            id = self.patientID
            return os.path.join(getAppPath(), name + " {PID" + str(id).zfill(6) + "}")

    def getTimeStamp(self):
        t = datetime.now()
        return t.strftime('"%y-%m-%d %H%M"').replace('\"', "")

    def sync_lineEdit(self):
        self.fillListBox()
        self.listWidgetPatients.setCurrentRow(0)
        items = self.listWidgetPatients.selectedItems()
        self.patientID = -1  # default none selected
        if len(items) > 0: self.patientID = items[0].value
        print(self.patientID)
        self.refreshMain()

    def listPatientsClicked(self):
        items = self.listWidgetPatients.selectedItems()
        self.patientID = -1  # default none selected
        if len(items) > 0: self.patientID = items[0].value
        self.refreshMain()

    def listTelsChanged(self, item):
        print(item.value, self.patientID)
        if item.checkState()==Qt.CheckState.Checked:
            x=1
        else:
            x=0
        if item.value>0 and self.patientID>0:
            result=RunScript('SQL/UpdateTelsUsed.sql',(x,self.patientID,item.value))
        return


    def listEmailsChanged(self, item):
        print(item.value, self.patientID)
        if item.checkState()==Qt.CheckState.Checked:
            x=1
        else:
            x=0
        if item.value>0 and self.patientID>0:
            result=RunScript('SQL/UpdateEmailsUsed.sql',(x,self.patientID,item.value))
        return

    def listAddressesChanged(self, item):
        print(item.value, self.patientID)
        if item.checkState()==Qt.CheckState.Checked:
            x=1
        else:
            x=0
        if item.value>0 and self.patientID>0:
            result=RunScript('SQL/UpdateAddressesUsed.sql',(x,self.patientID,item.value))
        return

    def listReferringDoctorsChanged(self, item):
        print(item.value, self.patientID)
        if item.checkState()==Qt.CheckState.Checked:
            x=1
        else:
            x=0
        if item.value>0 and self.patientID>0:
            result=RunScript('SQL/UpdateReferringDoctorsUsed.sql', (x, self.patientID, item.value))
        return

    def listReferringDoctorsDblClicked(self,item):
        dlg=DoctorDialog(self, item.value, "DoctorDialog.ui")
        dlg.exec()
        print(item.value)
    def fillComboBoxLocations(self):
        self.comboBoxLocation.clear()
        result = RunScript('SQL/All Locations.sql')
        for i in result:
            self.comboBoxLocation.addItem(i[1], i[0])
        self.comboBoxLocation.setCurrentIndex(0) #set to first in list
        self.ComboBoxLocationsChanged()

    def ComboBoxLocationsChanged(self):
        index = self.comboBoxLocation.currentIndex()
        if index > -1:
            self.locationID = self.comboBoxLocation.itemData(index)

    def fillListBox(self):
        self.listWidgetPatients.clear()
        result = RunScript('SQL/List Patients Containing.sql', (self.lineEditName.text(),))
        for i in result:
            item = QListWidgetItem(i[1])
            item.value = i[0]  # the patient id
            self.listWidgetPatients.addItem(item)

    def fillAddresses(self):
        self.listWidgetAddresses.clear()
        if self.patientID == -1: return
        result = RunScript('SQL/Addresses Patient.sql', (self.patientID,))
        for i in result:
            item = QListWidgetItem(i[1])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if i[2] == 1:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            item.value = i[0]
            self.listWidgetAddresses.addItem(item)

    def fillEmails(self):
        self.listWidgetEmails.clear()
        if self.patientID == -1: return
        result = RunScript('SQL/Emails Patient.sql', (self.patientID,))
        for i in result:
            item = QListWidgetItem(i[1])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if i[2] == 1:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            item.value = i[0]
            self.listWidgetEmails.addItem(item)

    def fillTel(self):
        self.listWidgetTel.clear()
        if self.patientID == -1: return
        result = RunScript('SQL/Tels Patient.sql', (self.patientID,))
        for i in result:
            item = QListWidgetItem(i[1])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if i[2] == 1:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            item.value = i[0]
            self.listWidgetTel.addItem(item)


    def fillDoctors(self):
        self.listWidgetReferringDoctors.clear()
        if self.patientID == -1: return
        result = RunScript('SQL/Doctors.sql', (self.patientID,))
        for i in result:
            item = QListWidgetItem(i[2] + ' (' + i[3] + ')')
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if i[4] == 1:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            item.value = i[0]
            self.listWidgetReferringDoctors.addItem(item)

    def openWord(self, filepath):
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(filepath)
        else:  # linux variants
            subprocess.call(('xdg-open', filepath))

    def uploadFile(self, filepath, destpath):
        path = Path(filepath)
        dest = Path(destpath)
        d = "".join('/' + d for d in dest.joinpath(path.name).parts if d != sep)
        with path.open('rb') as f:
            metadata = self.dbx.files_upload(f.read(), d, WriteMode('overwrite'))
            print(metadata.id)
            print(d)

    def copyFile(self, filepath, destpath, counter=0):
        path = Path(filepath)
        dest = Path(destpath)
        try:
            shutil.copyfile(path, dest)
        except shutil.Error:
            counter += 1
            self.copyFile(filepath, destpath + " " + str(counter))

    def safeCopyFile(self, filepath, destpath, dst=None):
        """Safely copy a file to the specified directory. If a file with the same name already
        exists, the copied file name is altered to preserve both.

        :param str file_path: Path to the file to copy.
        :param str out_dir: Directory to copy the file into.
        :param str dst: New name for the copied file. If None, use the name of the original
            file.
        """
        path = Path(filepath)
        dest = Path(destpath)
        name = dst or os.path.basename(dest)
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest):
            shutil.copy(path, dest)
            return dest
        else:
            base, extension = os.path.splitext(name)
            i = 1
            while os.path.exists(os.path.join(dest_dir, '{} v{}{}'.format(base, i, extension))):
                i += 1
            shutil.copy(path, os.path.join(dest_dir, '{} v{}{}'.format(base, i, extension)))
            return os.path.join(dest_dir, '{} v{}{}'.format(base, i, extension))

    def formatAddress(self, s):
        x = s.split(",")
        return '\n'.join(x)

    def getBasicContext(self):
        context = {}
        context.update({'date':datetime.now().strftime('%d-%m-%Y')})
        if self.locationID > -1:
            result = RunScript('SQL/Locations.sql', (self.locationID,))
            y = dict(result.fetchall()[0])
            context.update({'location': y.get('Name')})
            context.update({'location_address': y.get('Address')})
        if self.patientID > -1:
            result = RunScript('SQL/Details New Letter.sql', (self.patientID,))
            y = dict(result.fetchall()[0])
            context.update({"name": y.get('Name'), "full_details": y.get('FullName') + " " + y.get('DOB')})
            if y.get('NHS_NO'): context["nhs_no"] = "NHS No: " + y.get('NHS_NO')

            #Addresses
            result = RunScript('SQL/Addresses Patient Used.sql', (self.patientID,))
            addresses=[]
            for i in result:
                y=dict(i)
                addresses.append(self.formatAddress(y.get('Address')))
            if len(addresses)>0:
                a='\n\n'.join(addresses)
                context.update({'address':a})

            #Telephone
            result = RunScript('SQL/Tel Patient Used.sql', (self.patientID,))
            tels=[]
            for i in result:
                y=dict(i)
                tels.append("t: "+y.get('TEL_NO'))
            if len(tels)>0:
                t='\n'.join(tels)
                context.update({'tel':t})

            #Referring doctors
            result = RunScript('SQL/Referring Doctors.sql', (self.patientID,))
            drs=[]
            for i in result:
                y = dict(i)
                x = []
                x.append(y.get('Doctor'))
                if y.get('Job_Title'): x.append(y.get('Job_Title'))
                drs.append(", ".join(x))
            if len(drs)>0:
                d="Cc'd"+ "\n"+'\n'.join(drs)
                context.update({'referring_doctors':d})

            #Emails
            result = RunScript('SQL/Emails Patient Used.sql', (self.patientID,))
            emails=[]
            for i in result:
                y = dict(i)
                emails.append(y.get('Email'))
            if len(emails)>0:
                e="Also by email:"+ "\n"+'\n'.join(emails)
                context.update({'emails':e})



        return context

    def Letter(self, type):
        if self.patientID == -1: return
        f = None
        g = 'generic'
        PID = "{" + str(self.patientID).zfill(6) + "}"
        context = self.getBasicContext()

        match type:
            case 'NEW':
                f = os.path.join("Letters", "NEW PATIENT LETTER.docx")
                g = "new"
            case "FOLLOW_UP":
                f = os.path.join("Letters", "FOLLOW UP PATIENT LETTER.docx")
                g = "follow up"
            case "PRESCRIPTION":
                f = os.path.join("Letters", "PRESCRIPTION LETTER.docx")
                g = "prescription"
            case _:
                return
        Path(self.getPatientFolder()).mkdir(parents=True, exist_ok=True)
        destpath = os.path.join(self.getPatientFolder(), self.getTimeStamp() + " " + g + " " + PID + '.docx')
        print(destpath)
        d = self.safeCopyFile(f, destpath)
        doc = DocxTemplate(d)
        doc.render(context)
        doc.save(d)
        self.openWord(d)

    def NewLetter(self):
        self.Letter('NEW')

    def FollowUpLetter(self):
        self.Letter('FOLLOW_UP')

    def PrescriptionLetter(self):
        self.Letter("PRESCRIPTION")

    # Drag and drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # TODO: check the file is fully downloaded from Dropbox
        if self.patientID == -1: return
        PID = "{" + str(self.patientID).zfill(6) + "}"
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            name = os.path.basename(f)
            base, extension = os.path.splitext(name)
            dest = os.path.join(self.getPatientFolder(), self.getTimeStamp() + " " + base + " " + PID + extension)
            self.safeCopyFile(f, dest)
            print(dest)


def find_dbx_path(path):
    """ Try and open info.json to retreive Dropbox path """
    try:
        with open(os.path.expandvars(path), "r") as f:
            data = json.load(f)
            print(data.values)
            return list(data.values())[0]["path"]
    except:
        pass


""" Look for file """


def findDBPath():
    for path in INFO_PATHS:
        dbx_path = find_dbx_path(path)
        # if path found stop searching
        if dbx_path:
            break
    if dbx_path is None: dbx_path = "/Users/William/Dropbox (Personal)"
    return dbx_path


def getAppPath():
    return findDBPath() + APP_PATH


if __name__ == '__main__':
    print(getAppPath())
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()
