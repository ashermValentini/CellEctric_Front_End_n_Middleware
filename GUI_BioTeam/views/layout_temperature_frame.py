
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap

import sys

import application_style
import resources_rc

class TemperatureFrame(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        
        # Set the style directly on the current frame (self), not a new QFrame
        self.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.setObjectName("frame_temperature")

        # Use QVBoxLayout on self to manage its layout
        self.temp_layout = QtWidgets.QVBoxLayout(self)

        # Title for temperature frame
        title_label = QtWidgets.QLabel("TEMPERATURE")
        title_label.setStyleSheet(application_style.main_window_title_style)
        title_label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        self.temp_layout.addWidget(title_label)
        self.temp_layout.addSpacing(45)

        # Layout for image and stats
        temp_details_layout = QtWidgets.QHBoxLayout()
        self.temp_layout.addLayout(temp_details_layout)

        # Labels layout
        temp_stats_labels_layout = QtWidgets.QVBoxLayout()
        temp_details_layout.addLayout(temp_stats_labels_layout)

        # Max temperature label
        max_temp_label = QtWidgets.QLabel("Max")
        max_temp_label.setStyleSheet(application_style.main_window_temperature_number_style)
        temp_stats_labels_layout.addWidget(max_temp_label, alignment=QtCore.Qt.AlignTop)

        # Min temperature label
        min_temp_label = QtWidgets.QLabel("Current")
        min_temp_label.setStyleSheet(application_style.main_window_temperature_number_style)
        temp_stats_labels_layout.addWidget(min_temp_label, alignment=QtCore.Qt.AlignBottom)

        # Temperature statistics layout
        temp_stats_layout = QtWidgets.QVBoxLayout()
        temp_details_layout.addLayout(temp_stats_layout)

        self.max_temp_data = QtWidgets.QLabel("-")
        self.max_temp_data.setStyleSheet(application_style.main_window_temperature_number_style)
        temp_stats_layout.addWidget(self.max_temp_data, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.current_temp_data = QtWidgets.QLabel("-")
        self.current_temp_data.setStyleSheet(application_style.main_window_temperature_number_style)
        temp_stats_layout.addWidget(self.current_temp_data, alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)

        # Temperature control layout
        temp_control_layout = QtWidgets.QHBoxLayout()
        temp_control_label = QtWidgets.QLabel("Control")
        temp_control_label.setStyleSheet(application_style.main_window_temperature_number_style)
        temp_control_layout.addWidget(temp_control_label)
        
        # Temperature control button
        self.temp_control_button = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/snowflake.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.temp_control_button.setIcon(icon)
        self.temp_control_button.setIconSize(QtCore.QSize(38, 50))
        self.temp_control_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
            }
            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);
            }
            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        temp_control_layout.addStretch(1)
        temp_control_layout.addWidget(self.temp_control_button)
        temp_control_layout.addSpacing(36)
        self.temp_layout.addLayout(temp_control_layout)
        self.temp_layout.addSpacing(20)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temperature Display")
        self.resize(500, 300)
        self.setCentralWidget(TemperatureFrame())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())