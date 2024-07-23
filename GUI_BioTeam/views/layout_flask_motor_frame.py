from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator
import sys
import os 

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
import constants.defaults
import resources_rc
import styling.application_style as application_style

class FlaskMotorsFrame(QtWidgets.QFrame): 
    def __init__(self):
        super(FlaskMotorsFrame, self).__init__()
        self.initUI()
    
    def initUI(self):
        self.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.setObjectName("frame_d_flaskMotors")

        layout_flask = QtWidgets.QVBoxLayout(self)  # create layout for ethanol frame
        self.setLayout(layout_flask)  # set layout to flask frame
        layout_flask.setAlignment(QtCore.Qt.AlignCenter)

        # region: label
        label_flask = QtWidgets.QLabel(self)
        label_flask.setStyleSheet(application_style.main_window_title_style)
        label_flask.setText("FLASKS")
        label_flask.setAlignment(QtCore.Qt.AlignCenter)
        layout_flask.addWidget(label_flask)  # add label to layout
        layout_flask.addSpacing(20)     # Add a fixed amount of vertical space  # Adjust the number for more or less space
        # endregion

        # region: flask up down buttons
        flask_up_down_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.button_flask_bottom = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/bottom_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_flask_bottom.setIcon(icon)
        self.button_flask_bottom.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.button_flask_bottom.setStyleSheet("""
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

        self.button_flask_up  = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/up_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_flask_up.setIcon(icon)
        self.button_flask_up.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_flask_up, 30, False)

        self.button_flask_down = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/down_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_flask_down.setIcon(icon)
        self.button_flask_down.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_flask_down, 30, False)

        flask_up_down_button_layout.addWidget(self.button_flask_bottom)  # add button to the layout
        flask_up_down_button_layout.addWidget(self.button_flask_up)
        flask_up_down_button_layout.addWidget(self.button_flask_down)

        layout_flask.addLayout(flask_up_down_button_layout)  # add layout for progress bar and button to main layout 
        # endregion
        
        # region: flask left right
        flask_left_right_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.button_flask_leftmost = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        # Load the pixmap from the resource file
        pixmap = QtGui.QPixmap(":/images/rightmost_w.png")
        # Create a transformation and rotate it 180 degrees
        transform = QtGui.QTransform().rotate(180)
        rotated_pixmap = pixmap.transformed(transform)
        icon.addPixmap(rotated_pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_flask_leftmost.setIcon(icon)
        self.button_flask_leftmost.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.button_flask_leftmost.setStyleSheet("""
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

        self.button_flask_left  = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/left_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_flask_left.setIcon(icon)
        self.button_flask_left.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_flask_left, 30, False)

        self.button_flask_right = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/right_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_flask_right.setIcon(icon)
        self.button_flask_right.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_flask_right, 30, False)

        flask_left_right_button_layout.addWidget(self.button_flask_leftmost)  # add button to the layout
        flask_left_right_button_layout.addWidget(self.button_flask_left)
        flask_left_right_button_layout.addWidget(self.button_flask_right)

        layout_flask.addLayout(flask_left_right_button_layout)  # add layout for progress bar and button to main layout
        # endregion


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
        self.setWindowTitle("Plotting Frame Display")
        self.resize(500, 300)
        self.setCentralWidget(FlaskMotorsFrame())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())