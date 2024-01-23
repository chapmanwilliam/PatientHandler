from PyQt6 import QtCore, QtWidgets

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    date_str = "1-Feb-2020"
    # convert str to QDate
    qdate = QtCore.QDate.fromString(date_str, "d-MMM-yyyy")

    widget_date = QtWidgets.QDateEdit()
    # Set the format of how the QDate will be displayed in the widget
    widget_date.setDisplayFormat("d-MMM-yyyy")

    widget_date.setDate(qdate)

    widget_date.show()

    sys.exit(app.exec())