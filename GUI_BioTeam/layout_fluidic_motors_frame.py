        
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator
import sys
import defaults
import resources_rc
import application_style

class FluidicMotorsFrame(QtWidgets.QFrame): 
    def __init__(self):
        super(FluidicMotorsFrame, self).__init__()
        self.initUI()
    
    def initUI(self):

        self.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.setObjectName("frame_d_cartridgeMotors")

        layout = QtWidgets.QVBoxLayout(self)  # create layout for ethanol frame
        self.setLayout(layout)  # set layout to cartridge frame
        layout.setAlignment(QtCore.Qt.AlignCenter)

        # region: label
        label = QtWidgets.QLabel(self)
        label.setStyleSheet(application_style.main_window_title_style)
        label.setText("FLUIDICS")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)  # add label to layout
        layout.addSpacing(20)     # Add a fixed amount of vertical space  # Adjust the number for more or less space
        # endregion

        # region: movement buttons
        progress_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.button_bottom = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        pixmap = QtGui.QPixmap(":/images/top_w.png")

        transform = QtGui.QTransform().rotate(180)
        rotated_pixmap = pixmap.transformed(transform)
        icon.addPixmap(rotated_pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        
        self.button_bottom.setIcon(icon)
        self.button_bottom.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_bottom, 30, True)

        self.button_up  = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/up_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_up.setIcon(icon)
        self.button_up.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_up, 30, False)

        self.button_down = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/down_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_down.setIcon(icon)
        self.button_down.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_down, 30, False)

        progress_button_layout.addWidget(self.button_bottom)  # add button to the layout
        progress_button_layout.addWidget(self.button_up)
        progress_button_layout.addWidget(self.button_down)
        layout.addLayout(progress_button_layout)  # add layout for progress bar and button to main layout

    def set_button_style(self, button, font_size=30, enabled=True):
        if enabled:
            button.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #222222;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: {font_size}px;
                }}

                QPushButton:hover {{
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }}

                QPushButton:pressed {{
                    background-color: #0796FF;
                }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid #444444;
                    border-radius: 10px;
                    background-color: #333333;
                    color: #AAAAAA;
                    font-family: Archivo;
                    font-size: {font_size}px;
                }}
            """)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temperature Display")
        self.resize(500, 300)
        self.setCentralWidget(FluidicMotorsFrame())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())