'''
import sys
import os
from PyQt5 import QtWidgets, QtGui
from layout import Ui_MainWindow
from functionality import Functionality


app = QtWidgets.QApplication(sys.argv)
QtGui.QFontDatabase.addApplicationFont(":/fonts/static/Archivo-Regular.ttf")

window = Functionality()
window.show()
sys.exit(app.exec_())
'''

import sys
from PyQt5 import QtWidgets, QtGui
from login_dialog import LoginDialog
from login_dialog import CustomMessageBox
from layout import Ui_MainWindow  # Ensure layout.py is correctly referenced
from functionality import Functionality  # Ensure functionality.py is correctly referenced


def main():
    app = QtWidgets.QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont(":/fonts/static/Archivo-Regular.ttf")

    login_dialog = LoginDialog()

    if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
        logged_in_user = login_dialog.username  # Get the logged-in username
        window = Functionality(logged_in_user)  # Pass the username to Functionality
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__ == "__main__":
    main()

