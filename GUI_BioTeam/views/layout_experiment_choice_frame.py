from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator
import sys
import defaults
import resources_rc
import application_style

class ExperimentChoiceFrame(QtWidgets.QFrame): 
    def __init__(self, username):
        super(ExperimentChoiceFrame, self).__init__()
        self.username = username
        self.initUI()
    
    def initUI(self):
        self.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.setObjectName("frame_e_user_info")

        layout_user_info = QtWidgets.QHBoxLayout(self)
        self.setLayout(layout_user_info)

        # region: add label for which application
        label_application = QtWidgets.QLabel(self)
        label_application.setStyleSheet(application_style.main_window_input_style)
        label_application.setText("Application: ")
        #endregion

        # region: add combobox to select which application to use
        self.application_combobox = QtWidgets.QComboBox()
        combobox_button_style = """
        QComboBox, QPushButton {
            color: #FFFFFF;
            background-color: rgba(255, 255, 255, 0.1);
            font-family: Archivo;
            font-size: 20px;   /* adjust this as needed */
            border: 2px solid rgba(255, 255, 255, 0.7);
            border-radius: 5px;
            padding: 5px 15px;
        }
        QComboBox::drop-down, QPushButton {
            border: none;
        }
        QComboBox:hover, QPushButton:hover {
            background-color: rgba(7, 150, 255, 0.7);  
        }
        QComboBox QAbstractItemView {
        color: #FFFFFF;
        background-color: rgba(255, 255, 255, 0.1);
        font-family: Archivo;
        font-size: 20px;   /* adjust this as needed */
        border: 2px solid rgba(255, 255, 255, 0.7);
        border-radius: 5px;
        selection-background-color: rgba(7, 150, 255, 0.5);  
        }
        """   
        
        self.application_combobox.setStyleSheet(combobox_button_style)
        if self.username == 'LBI':
            self.application_combobox.addItems(["Mouse Blood", "Human Blood"])  # Add more emails as needed
        else: 
            self.application_combobox.addItems(["POCII", "Ethanol to Sucrose Flush", "CG2 QC", "Autotune", "Demonstration"])  # Add more emails as needed
        
        #endregion

        # region: add choice lockin button 
        self.user_info_lockin_button = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.user_info_lockin_button.setIcon(icon)
        self.user_info_lockin_button.setIconSize(QtCore.QSize(20, 20))  # Adjust size as needed
        self.user_info_lockin_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        #endregion

        layout_user_info.addWidget(label_application)
        layout_user_info.addWidget(self.application_combobox)
        layout_user_info.addWidget(self.user_info_lockin_button)
        layout_user_info.addStretch(1)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Experiment Choice Frame")
        self.resize(500, 300)
        self.setCentralWidget(ExperimentChoiceFrame("LBI"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())