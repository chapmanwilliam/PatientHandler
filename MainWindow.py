from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.uic import loadUi
import sys
import os, subprocess, platform
from os import sep
import dropbox as Dropbox
from dropbox.exceptions import ApiError
from dropbox.files import WriteMode
from pathlib import Path
import shutil

import json

INFO_PATHS = ["%APPDATA%\Dropbox\info.json",
              "%LOCALAPPDATA%\Dropbox\info.json"," ~/.dropbox/info.json"]

APP_PATH = "/Apps/Patient Handler"

class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        loadUi('MainWindow.ui', self)

        #Letter buttons
        self.pushButton_LetterNew.clicked.connect(self.NewLetter)
        self.pushButton_LetterFollowUp.clicked.connect(self.FollowUpLetter)
        self.pushButton_LetterPrescription.clicked.connect(self.PrescriptionLetter)


        self.dbx=Dropbox.Dropbox('sl.BuEy6m4MyrTS9zLRh0m_BPO9vtOpX-zctYyDr16tXSxropBR4SUZw6-CUQexaKwoM9CUd1MO6iAA-rqVL2gkRV35qvFJ36EyGv3GkAq-GRgjkrRwVVbrlbloFuwPEnJH5kcEIVYQ9QVSlxYeymYl')

        self.patientFolder='10'

    def openWord(self, filepath):
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(filepath)
        else:  # linux variants
            subprocess.call(('xdg-open', filepath))

    def uploadFile(self, filepath, destpath):
        path=Path(filepath)
        dest=Path(destpath)
        d = "".join('/' + d for d in dest.joinpath(path.name).parts if d != sep)
        with path.open('rb') as f:
            metadata = self.dbx.files_upload(f.read(),d,WriteMode('overwrite'))
            print(metadata.id)
            print (d)

    def copyFile(self, filepath, destpath, counter=0):
        path=Path(filepath)
        dest=Path(destpath)
        try:
            shutil.copyfile(path,dest)
        except shutil.Error:
            counter +=1
            self.copyFile(filepath,destpath + " " + str(counter))

    def safeCopyFile(self, filepath, destpath, dst=None):
        """Safely copy a file to the specified directory. If a file with the same name already
        exists, the copied file name is altered to preserve both.

        :param str file_path: Path to the file to copy.
        :param str out_dir: Directory to copy the file into.
        :param str dst: New name for the copied file. If None, use the name of the original
            file.
        """
        path=Path(filepath)
        dest=Path(destpath)
        name = dst or os.path.basename(dest)
        dest_dir=os.path.dirname(dest)
        if not os.path.exists(dest):
            shutil.copy(path, dest)
        else:
            base, extension = os.path.splitext(name)
            i = 1
            while os.path.exists(os.path.join(dest_dir, '{} v{}{}'.format(base, i, extension))):
                i += 1
            shutil.copy(path, os.path.join(dest_dir, '{} v{}{}'.format(base, i, extension)))

    def NewLetter(self):
        print('hello new')
        filepath="Letters/NEW PATIENT LETTER.docx"
        destpath=getAppPath() + "/test.docx"
        self.safeCopyFile(filepath,destpath)
        self.openWord(destpath)

    def FollowUpLetter(self):
        print('hello follow up')
        filepath="Letters/FOLLOW UP PATIENT LETTER.docx"
        destpath=getAppPath() + "/test.docx"
        self.safeCopyFile(filepath,destpath)
        self.openWord(destpath)

    def PrescriptionLetter(self):
        print('hello prescription')
        filepath="Letters/PRESCRIPTION LETTER.docx"
        destpath=getAppPath() + "/test.docx"
        self.safeCopyFile(filepath,destpath)
        self.openWord(destpath)

    #Drag and drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            name=os.path.basename(f)
            dest=os.path.join(getAppPath(), name)
            self.safeCopyFile(f, dest)
            print(dest)


def find_dbx_path(path):
    """ Try and open info.json to retreive Dropbox path """
    try:
        with open(os.path.expandvars(path), "r") as f:
            data = json.load(f)
            print(data.values)
            return list(data.values())[0]["path"]
    except: pass

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
    return findDBPath()+APP_PATH

if __name__ == '__main__':
    print(getAppPath())
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()
