from PyQt6.QtWidgets import QMainWindow, QApplication, QListWidgetItem
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
        self.patientID=-1
        self.dbx = Dropbox.Dropbox(
            'ABC')

        self.fillListBox()

    def refreshMain(self):
        self.fillAddresses()
        self.fillEmails()
        self.fillDoctors()
        print(self.getPatientFolder())

    def getPatientFolder(self):
        if self.patientID==-1: return None
        items=self.listWidgetPatients.selectedItems()
        if len(items)>0:
            name=items[0].data(0)
            id=self.patientID
            return os.path.join(getAppPath(), name + " {PID" + str(id).zfill(6) + "}")

    def getTimeStamp(self):
        t=datetime.now()
        return t.strftime('"%y-%m-%d %H%M"').replace('\"',"")

    def sync_lineEdit(self):
        self.fillListBox()
        self.listWidgetPatients.setCurrentRow(0)
        items=self.listWidgetPatients.selectedItems()
        self.patientID=-1 #default none selected
        if len(items)>0: self.patientID=items[0].value
        print(self.patientID)
        self.refreshMain()

    def listPatientsClicked(self):
        items=self.listWidgetPatients.selectedItems()
        self.patientID=-1 #default none selected
        if len(items)>0: self.patientID=items[0].value
        print(self.patientID)
        self.refreshMain()

    def fillListBox(self):
        self.listWidgetPatients.clear()
        result = RunScript('SQL/List Patients Containing.sql', self.lineEditName.text())
        for i in result:
            item = QListWidgetItem(i[1])
            item.value=i[0] #the patient id
            self.listWidgetPatients.addItem(item)

    def fillAddresses(self):
        self.listWidgetAddresses.clear()
        if self.patientID==-1: return
        result = RunScript('SQL/Addresses Patient.sql', self.patientID)
        for i in result:
            item=QListWidgetItem(i[1])
            item.value=i[0]
            self.listWidgetAddresses.addItem(item)

    def fillEmails(self):
        self.listWidgetEmails.clear()
        if self.patientID==-1: return
        result = RunScript('SQL/Emails Patient.sql', self.patientID)
        for i in result:
            item=QListWidgetItem(i[1])
            item.value=i[0]
            self.listWidgetEmails.addItem(item)

    def fillDoctors(self):
        self.listWidgetReferringDoctors.clear()
        if self.patientID==-1: return
        result = RunScript('SQL/Doctors Patient.sql', self.patientID)
        for i in result:
            item=QListWidgetItem(i[1])
            item.value=i[0]
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

    def Letter(self,type):
        if self.patientID==-1: return
        f=None
        g='generic'
        PID="{"+str(self.patientID).zfill(6)+"}"
        context=None
        match type:
            case 'NEW':
                f=os.path.join("Letters","NEW PATIENT LETTER.docx")
                g="new"
                result = RunScript('SQL/Details New Letter.sql', self.patientID)
                x=result.fetchall()
                print('hello')
                print(x[0])
                context = {"name": x[0]}
            case "FOLLOW_UP":
                f=os.path.join("Letters","FOLLOW UP PATIENT LETTER.docx")
                g="follow up"
                context = {"company_name": "The Company"}
            case "PRESCRIPTION":
                f=os.path.join("Letters", "PRESCRIPTION LETTER.docx")
                g="prescrition"
                context = {'company_name': "The Company"}
            case _:
                return
        Path(self.getPatientFolder()).mkdir(parents=True, exist_ok=True)
        destpath = os.path.join(self.getPatientFolder(),self.getTimeStamp() + " " + g + " " + PID + '.docx')
        print(destpath)
        d=self.safeCopyFile(f, destpath)
#        doc = DocxTemplate(d)
#        doc.render(context)
#        doc.save(d)
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
        #TODO: check the file is fully downloaded from Dropbox
        if self.patientID==-1: return
        PID="{"+str(self.patientID).zfill(6)+"}"
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
