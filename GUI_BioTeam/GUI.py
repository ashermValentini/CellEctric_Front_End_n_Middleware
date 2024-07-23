
import sys
from PyQt5 import QtWidgets, QtGui

from views.login_dialog import LoginDialog
from views.login_dialog import CustomMessageBox
from controllers.functionality import Functionality  # Ensure functionality.py is correctly referenced


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

