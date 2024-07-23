from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator
import sys
import os 

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
import constants.defaults
import resources_rc
import styling.application_style as application_style

class ConnectionsFrame(QtWidgets.QFrame):
    def __init__(self):
        super(ConnectionsFrame, self).__init__()
        self.initUI()

    def initUI(self):
        # region : Frame for connections
        self.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.setObjectName("frame_d_coms_status")

        # Create a layout for the frame
        layout = QtWidgets.QVBoxLayout(self)

        # Create the label and add it to the layout
        label = QtWidgets.QLabel()
        label.setStyleSheet(application_style.main_window_title_style)
        label.setText("CONNECTIONS")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)  # Add the label to the layout

        # Add a spacer for some vertical space
        layout.addSpacing(10)
    
        # List of module names
        module_names = ["Pulse Generator", "PSU", "Temperature Sensor", "Pumps", "Motors", "Flow Rate Sensor"]

        # Dictionary to hold the circles
        self.circles = {}

        for module in module_names:
            # Create a layout for the module name and circle
            module_layout = QtWidgets.QHBoxLayout()
            
            # Create the module label and add it to the layout
            module_label = QtWidgets.QLabel()
            module_label.setStyleSheet(application_style.main_window_15p_style) 
            module_label.setText(module)
            module_label.setAlignment(QtCore.Qt.AlignLeft)
            module_layout.addWidget(module_label)
            
            # Add stretch to push the next widget to the right
            module_layout.addStretch(1)
            
            # Create the circle (using a radio button) and add it to the layout
            circle = QtWidgets.QRadioButton()
            circle.setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")
            circle.setEnabled(False)  # Initially set as disabled so it appears as white
            module_layout.addWidget(circle)

            # Add the circle to the dictionary
            self.circles[module] = circle

            # Add the module layout to the main layout
            layout.addLayout(module_layout)

        layout.addSpacing(30) 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plotting Frame Display")
        self.resize(500, 300)
        self.setCentralWidget(ConnectionsFrame())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())