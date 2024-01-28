from PyQt6.QtWidgets import QLineEdit, QFormLayout, QLabel, QDateEdit
from PyQt6 import QtCore
from SQL import executeScript

class lineEditOverride(QLineEdit):
    def __init__(self,parentForm):
        super().__init__()
        self.parentForm=parentForm

class dateEditOverride(QDateEdit):
    def __init__(self, parentForm):
        super().__init__()
        self.parentForm=parentForm

class FormLayoutBase(QFormLayout):
    """Edit base QFormLayout."""
    itemChangedSignal = QtCore.pyqtSignal(int)
    focusLossedSignal = QtCore.pyqtSignal()

    def __init__(self, mainUI, table, ID):
        super().__init__()
        self.entries = {}  # to store entries

        # Takes sql which returns Txt for lineedits and the cols are the labels
        self.mainUI = mainUI
        self.table = table  # as dic {name:name,columns:[col1,col2,col3]}
        self.ID = ID
        self.filled=True #if true fills with data
        self.listEdits=[] #list of the lineEdits
        self.loadWidgets()

    def getLoadSql(self):
        #returns dic [col_name1: col_value2, col_name2, col_value2}
        dic={}
        #if there are no entries
        if (self.ID==-1):
            for c_name in self.table['columns']:
              dic.update({c_name:''})
            return dic
        #if there is an entry selected
        sql = "SELECT\n" + ',\n'.join(self.table['columns']) + '\nFROM ' + self.table[
            'name'] + '\nWHERE ROWID = ' + str(self.ID)
        result = executeScript(sql)
        if result:
            i = result.fetchone()
            if i:
                dic = dict(i)
                return dic
        return None

    def getEntriesDic(self):
        d = self.getLoadSql()
        if d:
            for key in d:
                if 'Date' in key:
                    d[key] = self.entries[key].date().toString('yyyy-MM-dd')
                else:
                    d[key] = self.entries[key].text()
            return d
        return None

    def getSaveSql(self):
        result = None
        d=self.getEntriesDic()
        if d:
            result = ",\n".join([key + "=\"" + value + "\"" for key, value in d.items()])
            result = "UPDATE " + self.table['name'] + "\nSET\n" + result + '\nWHERE ROWID=' + str(self.ID)
        return result

    def saveDataWidgets(self):
        # Save it to SQL
        result = executeScript(self.getSaveSql())
        return result

    def fillForm(self):
        #on the assumption the widgets have already been loaded
        dic = self.getLoadSql()
        if dic is None: return
        for e in self.listEdits:
            ref=e.objectName().replace('dateEdit_','').replace('lineEdit_','')
            if e.metaObject().className()=='lineEditOverride':
                e.setText(dic[ref])
            if e.metaObject().className()=='dateEditOverride':
                qD = QtCore.QDate.fromString(dic[ref], "yyyy-MM-dd")
                e.setDate(qD)


    def loadWidgets(self):
        dic = self.getLoadSql()
        if dic is None: return

        for key, txt in dic.items():
            # label
            l = QLabel()
            l.setObjectName('labelEdit_' + key)
            l.setText(key.replace('_', ' ') + ":")
            # edit
            if 'Date' in key:
                qD = QtCore.QDate.fromString(txt, "yyyy-MM-dd")
                e = dateEditOverride(self)
                e.setObjectName("dateEdit_" + key)
                if self.filled: e.setDate(qD)
            else:
                e = lineEditOverride(self)
                e.setMinimumSize(200, 0)
                e.setObjectName("lineEdit_" + key)
                if self.filled: e.setText(txt)
            e.editingFinished.connect(self.possible_save)
            e.sizePolicy().horizontalPolicy().MinimumExpanding
            self.entries.update({key: e})
            self.addRow(l, e)
            self.listEdits.append(e)

    @QtCore.pyqtSlot()
    def possible_save(self):
        self.focusLossedSignal.emit()
