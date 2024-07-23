from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap

import sys
import os 

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
import styling.application_style as application_style
import resources_rc

#===============================
# EXPERIMENT PAGE CLASSES
#===============================
class CustomExperimentFrame(QtWidgets.QFrame):
    def __init__(self, title, icon_paths):
        super().__init__()
        
        self.setStyleSheet("background-color: #222222; border-radius: 15px;")
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Label
        self.label = QtWidgets.QLabel(title)
        self.label.setStyleSheet("QLabel { color : #FFFFFF; font-family: Archivo; font-size: 25px;  }")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Action items layout
        self.button_layout = QtWidgets.QHBoxLayout()
        
        # Start/stop button
        self.start_stop_button = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_paths["start_stop"]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.start_stop_button.setIcon(icon)
        self.start_stop_button.setIconSize(QtCore.QSize(30, 30))
        self.start_stop_button.setStyleSheet("""
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

        
        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid white;
                border-radius: 3px;
                background-color: #222222;
                text-align: center;
                height: 50px;  /* Adjust as necessary */
            }

            QProgressBar::chunk {
                background-color: rgba(7, 150, 255, 0.7);
            }
            QProgressBar {
                color: white;  /* Color of the text */
                font-size: 15px;  /* Size of the text */
            }
            """
        )
            
        self.progress_bar.setValue(0)
        
        # Reset button
        self.reset_button = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_paths["reset"]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reset_button.setIcon(icon)
        self.reset_button.setIconSize(QtCore.QSize(30, 30))
        self.reset_button.setStyleSheet("""
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

        
        # Add items to button layout
        self.button_layout.addWidget(self.start_stop_button)
        self.button_layout.addWidget(self.progress_bar)
        self.button_layout.addWidget(self.reset_button)
        
        # Add widgets to main layout
        layout.addWidget(self.label)
        layout.addSpacing(10)
        layout.addLayout(self.button_layout)

        self.setLayout(layout)