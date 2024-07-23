        

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QDoubleValidator, QIntValidator
import sys
import defaults
import resources_rc
import application_style

class BloodFrame(QtWidgets.QFrame):
    def __init__(self):
        super(BloodFrame, self).__init__()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.setObjectName("frame_blood")

        layout_blood = QtWidgets.QVBoxLayout(self)  # create layout for ethanol frame
        self.setLayout(layout_blood)  # set layout to blood frame
        layout_blood.setAlignment(QtCore.Qt.AlignCenter)

        # region: label and gear symbol
        layout_label_n_gear = QtWidgets.QHBoxLayout()

        label_blood = QtWidgets.QLabel(self)
        label_blood.setStyleSheet(application_style.main_window_title_style)
        label_blood.setText("BLOOD")
        layout_label_n_gear.addSpacing(120) 
        label_blood.setAlignment(QtCore.Qt.AlignCenter)
        layout_label_n_gear.addWidget(label_blood)  # add label to layout
        layout_label_n_gear.addStretch(1) 

        self.blood_gear = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/gear.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.blood_gear.setIcon(icon)
        self.blood_gear.setIconSize(QtCore.QSize(15, 15))  # Adjust size as needed
        self.set_button_style(self.blood_gear, 30, True)
        layout_label_n_gear.addWidget(self.blood_gear)  # add label to layout

        layout_blood.addLayout(layout_label_n_gear) # add label to layout
        # endregion
        layout_blood.addSpacing(20)     # Add a fixed amount of vertical space  # Adjust the number for more or less space
        # region: movement buttons
        progress_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.button_blood_top = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/top_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_blood_top.setIcon(icon)
        self.button_blood_top.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.button_blood_top.setStyleSheet("""
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

        self.button_blood_up = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/up_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_blood_up.setIcon(icon)
        self.button_blood_up.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_blood_up, 30, False)

        self.button_blood_down = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/down_slow_w.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_blood_down.setIcon(icon)
        self.button_blood_down.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_blood_down, 30, False)

        self.button_blood_play_pause = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/play_pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_blood_play_pause.setIcon(icon)
        self.button_blood_play_pause.setIconSize(QtCore.QSize(30, 30))  # Adjust size as needed
        self.set_button_style(self.button_blood_play_pause, 30, False)

        progress_button_layout.addWidget(self.button_blood_top)  # add button to the layout
        progress_button_layout.addWidget(self.button_blood_up)
        progress_button_layout.addWidget(self.button_blood_down)
        progress_button_layout.addWidget(self.button_blood_play_pause)  # add button to the layout
        layout_blood.addLayout(progress_button_layout)  # add layout for progress bar and button to main layout
        # endregion
        # region : Inputs
        group_boxes_layout = QtWidgets.QHBoxLayout()  # create layout for both group boxes
        # region: Groupbox 1
        group_box_blood = QtWidgets.QGroupBox(self)  # create groupbox
        group_box_blood.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_blood.setAlignment(QtCore.Qt.AlignCenter)
        group_box_layout= QtWidgets.QHBoxLayout(group_box_blood)  # create layout for groupbox
        group_box_blood.setLayout(group_box_layout)  # set layout to groupbox

        unit_label = QtWidgets.QLabel("ml/min")
        unit_label.setStyleSheet(application_style.main_window_input_style)

        self.line_edit_blood = QtWidgets.QLineEdit()
        self.line_edit_blood.setValidator(QDoubleValidator(0.0001, 10000.0, 10, self.line_edit_blood))
        self.line_edit_blood.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 25px; }")
        self.line_edit_blood.setText("0.25")
        group_box_layout.addWidget(self.line_edit_blood)
        group_box_layout.addWidget(unit_label)
        # endregion
        # region: Groupbox 2
        group_box_blood_2 = QtWidgets.QGroupBox(self)  # create second groupbox
        group_box_blood_2.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_blood_2.setAlignment(QtCore.Qt.AlignCenter)
        group_box_layout_2 = QtWidgets.QHBoxLayout(group_box_blood_2)  # create layout for second groupbox
        group_box_blood_2.setLayout(group_box_layout_2)  # set layout to second groupbox

        unit_label_2 = QtWidgets.QLabel("ml")  # unit for time variable
        unit_label_2.setStyleSheet(application_style.main_window_input_style)

        self.line_edit_blood_2 = QtWidgets.QLineEdit()
        self.line_edit_blood_2.setValidator(QDoubleValidator(0.0001, 10000.0, 10, self.line_edit_blood_2))
        self.line_edit_blood_2.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 25px;}")
        self.line_edit_blood_2.setText("1")

        group_box_layout_2.addWidget(self.line_edit_blood_2)
        group_box_layout_2.addWidget(unit_label_2)
        # endregion
        group_boxes_layout.addWidget(group_box_blood)
        group_boxes_layout.addWidget(group_box_blood_2)
        layout_blood.addLayout(group_boxes_layout)  # add layout for group boxes to main layout
        #endregion
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
        self.setCentralWidget(BloodFrame())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())