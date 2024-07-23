
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator
import sys
import defaults
import resources_rc
import application_style

class PlottingFrame(QtWidgets.QFrame): 
    def __init__(self):
        super(PlottingFrame, self).__init__()
        self.initUI()
    
    def initUI(self):
        self.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.setObjectName("frame_d_voltageSignal")
                
        # Create a layout for the frame
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(layout)
        # Label
        label = QtWidgets.QLabel()
        label.setStyleSheet(application_style.main_window_title_style)
        label.setText("PLOTS")
        label.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(label)  
        layout.addSpacing(30)   
        
        # button creation
        self.temp_button = QtWidgets.QPushButton("Electrode Temperature")  # Set the text to empty since we are using an image
        self.temp_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 10px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 30px;

            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        self.voltage_button = QtWidgets.QPushButton("Voltage Signal")  # Set the text to empty since we are using an image
        self.voltage_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 10px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 30px;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        
        self.current_button = QtWidgets.QPushButton("Current Signal")  # Set the text to empty since we are using an image
        self.current_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 10px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 30px;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        
        layout.addWidget(self.temp_button) 
        layout.addWidget(self.voltage_button) 
        layout.addWidget(self.current_button) 
        layout.addSpacing(0) 


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plotting Frame Display")
        self.resize(500, 300)
        self.setCentralWidget(PlottingFrame())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())