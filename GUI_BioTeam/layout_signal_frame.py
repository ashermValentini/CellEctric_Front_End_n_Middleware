from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator
import sys
import defaults
import resources_rc
import application_style

class SignalFrame(QtWidgets.QFrame):
    def __init__(self):
        super(SignalFrame, self).__init__()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #222222; border-radius: 15px;")
        self.setObjectName("frame_d_signal")

        layout = QtWidgets.QVBoxLayout(self)  # Main vertical layout for the frame
        
        # Frame Label
        label = QtWidgets.QLabel("SIGNAL")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet(application_style.main_window_title_style)
        layout.addWidget(label)
        
        layout.addSpacing(20)  # Vertical spacing

        # Setup group boxes for Pulse Length and Repetition Rate
        self.line_edit_pulse_length, self.pulse_length_group_box = self.setupGroupBox(layout, "Pulse Length:", "uS", defaults.pulse_length_min, defaults.pulse_length_max, "75")
        self.line_edit_rep_rate, self.rep_rate_group_box = self.setupGroupBox(layout, "Repetition Rate:", "Hz", defaults.rep_rate_min, defaults.rep_rate_max, "200")

        # Horizontal layout for voltage settings and PSU button
        voltage_and_button_layout = QtWidgets.QHBoxLayout()
        
        # Group boxes for min and max voltage
        voltage_layout = QtWidgets.QVBoxLayout()  # Vertical layout for voltage group boxes
        self.line_edit_max_signal, self.max_voltage_group_box = self.setupGroupBox(voltage_layout, "Vp+ :", "V", defaults.voltage_min, defaults.voltage_max, "80")
        self.line_edit_min_signal, self.min_voltage_group_box = self.setupGroupBox(voltage_layout, "Vp- :", "V", defaults.voltage_min, defaults.voltage_max, "-80")
        
        voltage_and_button_layout.addLayout(voltage_layout)

        # PSU Button with an icon
        psu_and_pg_button_layout = QtWidgets.QVBoxLayout()

        self.psu_button = QtWidgets.QPushButton("PSU")
        #icon = QtGui.QIcon(":/images/lightning_symbol.png")
        #self.psu_button.setIcon(icon)
        #self.psu_button.setIconSize(QtCore.QSize(64, 120))
        self.psu_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                padding: 20px;  
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);
            }
            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        
        self.pg_button = QtWidgets.QPushButton("PG")
        #icon = QtGui.QIcon(":/images/lightning_symbol.png")
        #self.pg_button.setIcon(icon)
        #self.pg_button.setIconSize(QtCore.QSize(64, 120))
        self.pg_button.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                padding: 20px;  
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);
            }
            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        psu_and_pg_button_layout.addWidget(self.psu_button)
        psu_and_pg_button_layout.addWidget(self.pg_button)
        
        voltage_and_button_layout.addLayout(psu_and_pg_button_layout)
        layout.addLayout(voltage_and_button_layout)

    def setupGroupBox(self, parent_layout, label_text, unit_text, min_val, max_val, default_val):
        group_box = QtWidgets.QGroupBox()
        group_box.setStyleSheet("QGroupBox { border: 2px solid white; border-radius: 10px; background-color: #222222; }")
        group_layout = QtWidgets.QHBoxLayout(group_box)
        
        label = QtWidgets.QLabel(label_text)
        label.setStyleSheet(application_style.main_window_voltage_style)
        
        line_edit = QtWidgets.QLineEdit()
        line_edit.setValidator(QIntValidator(min_val, max_val))
        line_edit.setStyleSheet("QLineEdit { color: white; background-color: #222222; font-size: 20px; }")
        line_edit.setText(default_val)
        
        unit_label = QtWidgets.QLabel(unit_text)
        unit_label.setStyleSheet(application_style.main_window_voltage_style)
        
        group_layout.addWidget(label)
        group_layout.addStretch(1)
        group_layout.addWidget(line_edit)
        group_layout.addWidget(unit_label)
        
        parent_layout.addWidget(group_box)

        return line_edit, group_box  # Return the line edit and the group box for further reference
    
    def set_button_style(self, button, font_size = 20, padding = 20):
        print('button on')
        button.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid white;
                border-radius: 6px;
                background-color: #0796FF;
                color: #FFFFFF;
                font-family: Archivo;
                padding: {padding}px;  
                font-size: {font_size}px;
            }}

            QPushButton:hover {{
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }}
        """)

    def reset_button_style(self, button, font_size=20, padding=20):
        print("Resetting style")  # Debugging print statement
        button.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid white;
                border-radius: 6px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                padding: {padding}px;  
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }}
            QPushButton:pressed {{
                background-color: #0796FF;
            }}
        """)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temperature Display")
        self.resize(500, 300)
        self.setCentralWidget(SignalFrame())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())