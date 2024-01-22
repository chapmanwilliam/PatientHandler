import sys
from PyQt6 import QtWidgets, QtCore,

class Table(QtWidgets.QTableWidget):
    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        index = self.indexAt(event.pos())
        someAction = menu.addAction('')
        if index.isValid():
            someAction.setText('Selected item: "{}"'.format(index.data()))
        else:
            someAction.setText('No selection')
            someAction.setEnabled(False)
        anotherAction = menu.addAction('Do something')

        res = menu.exec_(event.globalPos())
        if res == someAction:
            print('first action triggered')


class Example(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)
        self.table = Table(10, 4)
        layout.addWidget(self.table)
        layout.addStretch()

        central.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        central.customContextMenuRequested.connect(self.emptySpaceMenu)

    def emptySpaceMenu(self):
        menu = QtWidgets.QMenu()
        menu.addAction('You clicked on the empty space')
        menu.exec_(QtGui.QCursor.pos())


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    example = Example()
    example.show()
    sys.exit(app.exec_())