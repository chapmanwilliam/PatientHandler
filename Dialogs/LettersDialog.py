from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QPushButton
from PyQt6 import QtCore
from PyQt6.uic import loadUi
from SQL import executeScriptsFromFile as RunScript, executeScript


from ListBoxes.ListBoxes import ListBoxSearchable
from FormLayout.EditFormLayout_Clone import EditFormLayoutClone

class LettersDialog(QDialog):
    def __init__(self,mainUI):
        super(LettersDialog, self).__init__(mainUI)
        loadUi('Dialogs/LettersDialog.ui', self)
        self.mainUI=mainUI
        listBox=ListBoxSearchable(self.mainUI, "LETTERS")
        self.hLayout.addLayout(listBox)
