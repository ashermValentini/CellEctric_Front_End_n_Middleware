from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator
import sys
import defaults
import resources_rc
import application_style
from views.roundprogressBar import QRoundProgressBar

class SucroseEthanolFrame(QtWidgets.QFrame):
    def __init__(self, title, default_flow_rate, default_volume):
        super(SucroseEthanolFrame, self).__init__()
        self.title = title  # Store title as an instance attribute
        self.default_flow_rate = default_flow_rate  # Store default_flow_rate as an instance attribute
        self.default_volume = default_volume 
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.setObjectName("frame_sucrose_ethanol")

        layout= QtWidgets.QVBoxLayout(self)  # create layout for sucrose frame
        self.setLayout(layout)  # set layout to sucrose frame
        layout.setAlignment(QtCore.Qt.AlignCenter)

        # region: label
        label = QtWidgets.QLabel(self)
        label.setStyleSheet(application_style.main_window_title_style)
        label.setText(self.title)
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)  # add label to layout
        layout.addSpacing(20)     # Add a fixed amount of vertical space  # Adjust the number for more or less space
        # endregion

        # region: progress bar and button
        progress_button_layout = QtWidgets.QHBoxLayout()  # create layout for progress bar and button

        self.progress_bar = QRoundProgressBar()  # create progress bar
        self.progress_bar.setFixedSize(175, 175)
        self.progress_bar.setRange(0, 60)
        self.progress_bar.setValue(0)
        self.progress_bar.setBarColor('#0796FF')
        self.progress_bar.setDecimals(2)
        self.progress_bar.setDonutThicknessRatio(0.85)
        
        progress_button_layout.addSpacing(20)  # add fixed space of 20 pixels
        progress_button_layout.addWidget(self.progress_bar)  # add progress bar to the layout
        progress_button_layout.addSpacing(5)  # add fixed space of 20 pixels

        self.button = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/play_pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button.setIcon(icon)
        self.button.setIconSize(QtCore.QSize(50, 50))  # Adjust size as needed
        self.button.setStyleSheet("""
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

        progress_button_layout.addWidget(self.button)  # add button to the layout

        layout.addLayout(progress_button_layout)  # add layout for progress bar and button to main layout
        # endregion
       
        # region : Inputs
        group_boxes_layout = QtWidgets.QHBoxLayout()  # create layout for both group boxes
        # region: Groupbox 1
        group_box = QtWidgets.QGroupBox(self)  # create groupbox
        group_box.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box.setAlignment(QtCore.Qt.AlignCenter)
        group_box_layout = QtWidgets.QHBoxLayout(group_box)  # create layout for groupbox
        group_box.setLayout(group_box_layout)  # set layout to groupbox

        unit_label = QtWidgets.QLabel("ml/min")
        unit_label.setStyleSheet(application_style.main_window_input_style)

        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 25px; }")
        self.line_edit.setText(f"{self.default_flow_rate}")

        group_box_layout.addWidget(self.line_edit)
        group_box_layout.addWidget(unit_label)
        # endregion
        # region: Groupbox 2
        group_box_2 = QtWidgets.QGroupBox(self)  # create second groupbox
        group_box_2.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_box_2.setAlignment(QtCore.Qt.AlignCenter)
        group_box_layout_2 = QtWidgets.QHBoxLayout(group_box_2)  # create layout for second groupbox
        group_box_2.setLayout(group_box_layout_2)  # set layout to second groupbox

        unit_label_2 = QtWidgets.QLabel("ml")  # unit for time variable
        unit_label_2.setStyleSheet(application_style.main_window_input_style)

        self.line_edit_2 = QtWidgets.QLineEdit()
        self.line_edit_2.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 25px; }")
        self.line_edit_2.setText(f"{self.default_volume}")

        group_box_layout_2.addWidget(self.line_edit_2)
        group_box_layout_2.addWidget(unit_label_2)
        # endregion
        group_boxes_layout.addWidget(group_box)
        group_boxes_layout.addWidget(group_box_2)
        layout.addLayout(group_boxes_layout) 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temperature Display")
        self.resize(500, 300)
        self.setCentralWidget(SucroseEthanolFrame('SUCROSE', 5, 10))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())