import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from credentials import usernames, passwords
import application_style

class CustomMessageBox(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super(CustomMessageBox, self).__init__(parent)
        self.setStyleSheet("""
            QMessageBox {
                background-color: #222222;
                color: white;
                font-size: 20px;
            }
            QMessageBox QLabel {
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #444444;
                border: 2px solid white;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }
            QMessageBox QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("Login")
        self.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.setObjectName("login_dialog")
        self.setFixedSize(700, 600)

        layout = QtWidgets.QVBoxLayout()

        # Logo
        self.sidebar_logo = QtWidgets.QLabel()
        self.sidebar_logo.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        logo_pixmap = QtGui.QPixmap(":/images/logo_small_white.png")
        self.sidebar_logo.setPixmap(logo_pixmap.scaled(400, 160, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        layout.addWidget(self.sidebar_logo)

        # Title
        self.title_label = QtWidgets.QLabel("Welcome")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet(application_style.main_window_header_style)
        layout.addWidget(self.title_label)

        # Instructions
        self.instructions_label = QtWidgets.QLabel("Please enter your username and password below.")
        self.instructions_label.setAlignment(QtCore.Qt.AlignCenter)
        self.instructions_label.setStyleSheet(application_style.main_window_input_style)
        layout.addWidget(self.instructions_label)

        self.username_label = QtWidgets.QLabel("Username:")
        self.username_label.setStyleSheet(application_style.main_window_text_style)

        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setStyleSheet("""
            QLineEdit {
                color: white;
                background-color: #222222;
                font-size: 25px;
                border: 2px solid white;
                border-radius: 10px;
                padding: 10px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(7, 150, 255, 0.7);
            }
        """)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QtWidgets.QLabel("Password:")
        self.password_label.setStyleSheet(application_style.main_window_text_style)

        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setStyleSheet("""
            QLineEdit {
                color: white;
                background-color: #222222;
                font-size: 30px;
                border: 2px solid white;
                border-radius: 10px;
                padding: 10px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(7, 150, 255, 0.7);
            }
        """)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 10px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 30px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Check if the username is in the list and the password matches the corresponding entry
        if username in usernames:
            user_index = usernames.index(username)
            if passwords[user_index] == password:
                self.accept()
            else:
                self.show_error_message("Invalid username or password")
        else:
            self.show_error_message("Invalid username or password")

    def show_error_message(self, message):
        msg_box = CustomMessageBox(self)
        msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec_()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
        print("Login successful")
    else:
        print("Login failed")
    sys.exit(app.exec_())
