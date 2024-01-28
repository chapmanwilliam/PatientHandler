from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6 import QtCore

import os

class dropLabel(QLabel):
    def __init__(self,mainUI):
        super().__init__(mainUI)
        self.mainUI=mainUI
        self.setAcceptDrops(True)
        self.setText('DROP FILES HERE')

        f = self.font()
        f.setPointSize(50)  # sets the size to 50
        self.setFont(f)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # TODO: check the file is fully downloaded from Dropbox
        if self.mainUI.patientID == -1: return
        PID = "{" + str(self.mainUI.patientID).zfill(6) + "}"
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            name = os.path.basename(f)
            base, extension = os.path.splitext(name)
            dest = os.path.join(self.mainUI.getPatientFolder(), self.mainUI.getTimeStamp() + " " + base + " " + PID + extension)
            self.mainUI.safeCopyFile(f, dest)
            print(dest)
