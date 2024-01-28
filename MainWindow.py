from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QHBoxLayout, QListWidgetItem, QLabel, QComboBox
from PyQt6.uic import loadUi
from PyQt6 import QtCore
import sys
import os, subprocess, platform
from os import sep
from datetime import datetime
import dropbox as Dropbox
from dropbox.files import WriteMode
from pathlib import Path
import shutil
from SQL import executeScriptsFromFile as RunScript
from docxtpl import DocxTemplate
import json
from ListBoxes.label_PhotoClone import label_PhotoClone
from ListBoxes.ListBox_Clone import ListBox_Clone
from ListBoxes.ListBoxSearchable_CloneWithPhoto import ListBoxSearchable_CloneWithPhoto
from Dialogs.DoctorsDialog import DoctorsDialog
from ListBoxes.CDropLabel import dropLabel

INFO_PATHS = ["%APPDATA%\Dropbox\info.json",
              "%LOCALAPPDATA%\Dropbox\info.json", " ~/.dropbox/info.json"]

APP_PATH = "/Apps/Patient Handler"


class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        loadUi('MainWindow.ui', self)
        self.patientID = -1
        self.locationID = -1

        # Photo label

        self.childListBoxes = {}  # stores dict of the boxes
        self.addSearhablePatientListBox()
        self.addPatientButtons()
        self.addPatientListBoxes()
        self.fillComboBoxLocations()

        self.dropLabel=dropLabel(self)
        self.gridLayout_Right.addWidget(self.dropLabel)

        self.actionDoctors_Show.triggered.connect(self.showDoctors)


        self.comboBoxLocation.activated.connect(self.ComboBoxLocationsChanged)


        self.dbx = Dropbox.Dropbox(
            'ABC')

    def showDoctors(self):
        doctorsDialog = DoctorsDialog(self)
        doctorsDialog.exec()

    def updateDoctorItem(self,ID):
        self.childListBoxes['REFERRING_DOCTORS'].RowEditedSignalled(ID)

    def deleteDoctorItem(self,ID):
        self.childListBoxes['REFERRING_DOCTORS'].fillBox()


    @QtCore.pyqtSlot(int)
    def patientChanged(self, ID):
        self.setPatientID(ID)
        for k,v in self.childListBoxes.items(): v.fillBox()
#        self.label_Photo.ID=self.patientID
#        self.label_Photo.fillPhoto()
        print('Patient ID set, ',self.patientID)

    def addSearhablePatientListBox(self):
        #Photo for locations
        self.location_photo=label_PhotoClone(self, "LOCATIONS")
        #Combobox for locations
        self.comboBoxLocation=QComboBox(self)
        f = self.comboBoxLocation.font()
        f.setPointSize(27)  # sets the size to 27
        self.comboBoxLocation.setFont(f)
        #add to hlayout
        self.horizontalLayout_Top.addWidget(self.location_photo)
        self.horizontalLayout_Top.addWidget(self.comboBoxLocation)

        hlayout=QHBoxLayout()
        self.searchablePatientList = ListBoxSearchable_CloneWithPhoto(self, "PATIENTS")
        self.verticalLayout_Top.addLayout(hlayout)
        self.verticalLayout_Top.addLayout(self.searchablePatientList)
        self.searchablePatientList.list.itemChangedSignal.connect(self.patientChanged)
        self.patientChanged(self.searchablePatientList.list.ID)

    def addPatientListBoxes(self):
        # Add the patient listboxes to verticalLayoutLeft
        lst=('ADDRESSES','TELEPHONES','EMAILS','REFERRING_DOCTORS')

        for l in lst:
            label=QLabel(self); label.setText(str.capitalize((l.replace('_',' '))+":"))
            box=ListBox_Clone(self,l)
            self.verticalLayoutLeft.addWidget(label)
            self.verticalLayoutLeft.addWidget(box);self.childListBoxes.update({l:box})

    def addPatientButtons(self):
        # Letter buttons
        self.button_newPatient = QPushButton(self);
        self.button_newPatient.setText('NEW PATIENT')
        self.button_Prescription = QPushButton(self);
        self.button_Prescription.setText('PRESCRIPTION')
        self.button_FollowUp = QPushButton(self);
        self.button_FollowUp.setText('FOLLOW UP')
        self.HLayout = QHBoxLayout()
        self.HLayout.addWidget(self.button_newPatient)
        self.HLayout.addWidget(self.button_FollowUp)
        self.HLayout.addWidget(self.button_Prescription)
        self.verticalLayout_Top.addLayout(self.HLayout)

        self.button_newPatient.clicked.connect(self.NewLetter)
        self.button_FollowUp.clicked.connect(self.FollowUpLetter)
        self.button_Prescription.clicked.connect(self.PrescriptionLetter)


    def setPatientID(self, ID):
        self.patientID = ID

    def getPatientFolder(self):
        if self.patientID == -1: return None
        items = self.searchablePatientList.list.selectedItems()
        if len(items) > 0:
            name = items[0].data(0)
            id = self.patientID
            return os.path.join(getAppPath(), name + " {PID" + str(id).zfill(6) + "}")

    def getTimeStamp(self):
        t = datetime.now()
        return t.strftime('"%y-%m-%d %H%M"').replace('\"', "")


    def fillComboBoxLocations(self):
        self.comboBoxLocation.clear()
        result = RunScript('SQL/All Locations.sql')
        for i in result:
            self.comboBoxLocation.addItem(i[1], i[0])
        self.comboBoxLocation.setCurrentIndex(0)  # set to first in list
        self.ComboBoxLocationsChanged()

    def ComboBoxLocationsChanged(self):
        index = self.comboBoxLocation.currentIndex()
        if index > -1:
            self.locationID = self.comboBoxLocation.itemData(index)
            self.location_photo.ID=self.locationID
            self.location_photo.fillPhoto()

    def fillPatients(self):
        self.listWidgetPatients.clear()
        result = RunScript('SQL/Patients lists/Patients Containing.sql', (self.lineEditName.text(),))
        for i in result:
            item = QListWidgetItem(i[1])
            item.value = i[0]  # the patient id
            self.listWidgetPatients.addItem(item)
        self.refreshMain()

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
        x=[y.strip() for y in x]
        return '\n'.join(x)

    def getBasicContext(self):
        context = {}
        # date
        context.update({'date': 'Dated: '+ datetime.now().strftime('%d-%m-%Y')})

        # locatiion
        if self.locationID > -1:
            result = RunScript('SQL/Locations.sql', (self.locationID,))
            if result:
                y = dict(result.fetchall()[0])
                context.update({'location': y.get('Name')})
                context.update({'location_address': y.get('Address')})

        # patient details
        if self.patientID > -1:
            # patients id
            context.update({'patient_id':str(self.patientID).zfill(6)})
            # personal details
            result = RunScript('SQL/Details New Letter.sql', (self.patientID,))
            if result:
                y = result.fetchall()[0]
                context.update({"name": y['Name'], "full_details": y['FullName'] + ", " + y['DOB']})
                if y['NHS_NO']: context["full_details"] += "; NHS No: " + y['NHS_NO']

            # Addresses
            result = RunScript('SQL/Addresses Patient Used.sql', (self.patientID,))
            addresses = []
            if result:
                for i in result:
                    addresses.append(self.formatAddress(i['TXT']))
                if len(addresses) > 0:
                    a = '\n\n'.join(addresses)
                    context.update({'address': a})

            # Telephone
            result = RunScript('SQL/Tel Patient Used.sql', (self.patientID,))
            tels = []
            if result:
                for i in result:
                    tels.append("t: " + i['TXT'])
                if len(tels) > 0:
                    t = '\n'.join(tels)
                    context.update({'tel': t})

            # Referring doctors
            result = RunScript('SQL/Referring Doctors Patient Used.sql', (self.patientID,))
            drs = []
            if result:
                for i in result:
                    drs.append(i['TXT'])
                if len(drs) > 0:
                    d = "Cc'd" + "\n" + '\n'.join(drs)
                    context.update({'referring_doctors': d})

            # Emails
            result = RunScript('SQL/Emails Patient Used.sql', (self.patientID,))
            emails = []
            if result:
                for i in result:
                    emails.append(i['TXT'])
                if len(emails) > 0:
                    e = "Also by email:" + "\n" + '\n'.join(emails)
                    context.update({'emails': e})

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
