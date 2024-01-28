import os.path
from PyQt6.QtWidgets import QLabel, QFileDialog
from PyQt6 import QtCore
from PyQt6.QtGui import *
from SQL import executeScriptsFromFile as RunScript, convert_into_binary, executeScript



class label_PhotoClone(QLabel):
    def __init__(self, mainUI, table_name):
        super().__init__(mainUI)
        self.mainUI = mainUI
        self.table_name = table_name  # assumes table name has columns Photo and PhotoExt
        self.ID=-1  # rowid of table

        self.setAcceptDrops(True)
        self.setScaledContents(True)
        self.setStyleSheet("border: 1px solid black;")
        self.setMaximumSize(90,90)
        self.setMinimumSize(90,90)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        self.sizePolicy().setHeightForWidth(True)

        #actions
        self.actionRemove = QAction("Remove...", self)
        self.actionRemove.triggered.connect(self.removeHeadPhoto)
        self.addAction(self.actionRemove)

        self.actionAdd = QAction("Add...", self)
        self.actionAdd.triggered.connect(self.getPhotoFileFromFile)
        self.addAction(self.actionAdd)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if (len(files)):
            matches = ['.heic', '.jpg', '.png', '.bmp', '.jpeg']
            base, ext = os.path.splitext(files[0])
            if any(x == ext for x in matches):  # check its one of the valid types
                self.addHeadPhoto(files[0])

    def getPhotoFileFromFile(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open file", ".", "Image Files (*.png *.jpg *.bmp *.heic)"
        )
        if not file_name:
            return None
        self.addHeadPhoto(file_name)

    def addHeadPhoto(self, file_name=None):
        # adds photo from file
        print('ID of photo for table ', self.ID, self.table_name)
        if self.ID == -1: return
        self.clearPhoto()

        base, ext = os.path.splitext(file_name)
        blob = convert_into_binary(file_name)
        sql="UPDATE " +self.table_name + " SET Photo=?, PhotoExt=? WHERE ROWID=?"
        result=executeScript(sql,(blob,ext,self.ID))
        if result is None:
            print("Didn't add photo to database")
        self.loadPhoto(file_name)

    def loadPhoto(self, f):
        self.pix = QPixmap(f)
        self.setPixmap(self.pix)

    def clearPhoto(self):
        self.clear()

    def removeHeadPhoto(self):
        sql="UPDATE " +self.table_name + " SET Photo=?, PhotoExt=? WHERE ROWID=?"
        result=executeScript(sql,(None,None,self.ID))
        if result is None:
            print('Did not remove photo from database')
        self.clearPhoto()

    def fillPhoto(self):
        # fills photo from db
        self.clearPhoto()
        if self.ID == -1: return

        sql = "SELECT * FROM {} WHERE ROWID ={}".format(self.table_name,self.ID)
        result=executeScript(sql)

        if result:
            first_row = result.fetchone()

            if not first_row: return

            blob = first_row['Photo']
            ext = first_row['PhotoExt']
            if not blob: return
            # write to temp file
            with open("temp" + ext, 'wb') as File:
                File.write(blob)
                File.close()
            self.loadPhoto('temp' + ext)
