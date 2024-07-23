from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QProgressBar, QDialog, QVBoxLayout, QLabel, QTextEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch
from matplotlib.transforms import Bbox

import sys
import os 

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
import resources_rc
import styling.application_style as application_style
import constants.defaults

#===============================
# LIVE DATA POP UPS
#===============================

class PopupWindow(QDialog):
    def __init__(self, title="Default Title", description="Default Description"):
        super().__init__()
        self.title = title
        self.description = description
        self.initUI()

    def initUI(self):
        
        main_vertical_layout = QVBoxLayout()
        #================================================================================================================================================================
        # TITLE AND DESCRIPTION
        #================================================================================================================================================================
        # region :
        self.label_LDA_title = QLabel(self.title)
        self.label_LDA_title.setStyleSheet(application_style.title_style)
        
        self.label_LDA_instructions = QLabel(self.description)
        self.label_LDA_instructions.setStyleSheet(application_style.input_style)
        self.label_LDA_instructions.setFixedWidth(800)  
        self.label_LDA_instructions.setWordWrap(True)
        # endregion
        #================================================================================================================================================================
        # USER INFORMATION
        #================================================================================================================================================================
        # region: 
        layout_LDA_user_information = QtWidgets.QHBoxLayout()

        layout_LDA_folder_name = QtWidgets.QVBoxLayout()
        self.label_LDA_folder_name = QLabel("Folder: ")
        self.label_LDA_folder_name.setStyleSheet(application_style.input_style)
        self.line_edit_LDA_folder_name = QtWidgets.QLineEdit()
        self.line_edit_LDA_folder_name.setStyleSheet(application_style.line_edit_style)
        self.line_edit_LDA_folder_name.setText("Data")
        layout_LDA_folder_name.addWidget(self.label_LDA_folder_name)
        layout_LDA_folder_name.addWidget(self.line_edit_LDA_folder_name)

        layout_LDA_user_name = QtWidgets.QVBoxLayout()
        self.label_LDA_user_name = QLabel("Name: ")
        self.label_LDA_user_name.setStyleSheet(application_style.input_style)
        self.combobox_LDA_user_name = QtWidgets.QComboBox()
        self.combobox_LDA_user_name.setStyleSheet(application_style.combobox_button_style)
        self.combobox_LDA_user_name.addItems(["","Dora", "Julia", "Asher"]) 
        layout_LDA_user_name.addWidget(self.label_LDA_user_name) 
        layout_LDA_user_name.addWidget(self.combobox_LDA_user_name)

        layout_LDA_flask_holder = QtWidgets.QVBoxLayout()
        self.label_LDA_flask_holder = QLabel("Flask Holder")
        self.label_LDA_flask_holder.setStyleSheet(application_style.input_style)
        self.combobox_LDA_flask_holder = QtWidgets.QComboBox()
        self.combobox_LDA_flask_holder.setStyleSheet(application_style.combobox_button_style)
        self.combobox_LDA_flask_holder.addItems(["Bactalert", "Falcons"])     
        layout_LDA_flask_holder.addWidget(self.label_LDA_flask_holder)
        layout_LDA_flask_holder.addWidget(self.combobox_LDA_flask_holder)

        layout_LDA_user_information.addLayout(layout_LDA_folder_name)
        layout_LDA_user_information.addStretch(1)
        layout_LDA_user_information.addLayout(layout_LDA_user_name)
        layout_LDA_user_information.addStretch(1)
        layout_LDA_user_information.addLayout(layout_LDA_flask_holder)
        layout_LDA_user_information.addStretch(1)
        
        #endregion
        #================================================================================================================================================================
        # EXPERIMENT INFORMATION
        #================================================================================================================================================================
        # region : 
        layout_LDA_experiment_information = QtWidgets.QHBoxLayout()

        layout_LDA_experiment_purpose = QtWidgets.QVBoxLayout()
        self.label_LDA_experiment_purpose = QLabel("Purpose: ")
        self.label_LDA_experiment_purpose.setStyleSheet(application_style.input_style)
        self.line_edit_LDA_experiment_purpose = QtWidgets.QLineEdit()
        self.line_edit_LDA_experiment_purpose.setStyleSheet(application_style.line_edit_style)
        layout_LDA_experiment_purpose.addWidget(self.label_LDA_experiment_purpose) 
        layout_LDA_experiment_purpose.addWidget(self.line_edit_LDA_experiment_purpose)

        layout_LDA_experiment_number = QtWidgets.QVBoxLayout()
        self.label_LDA_experiment_number = QLabel("ID")
        self.label_LDA_experiment_number.setStyleSheet(application_style.input_style)
        self.line_edit_LDA_experiment_number = QtWidgets.QLineEdit()
        self.line_edit_LDA_experiment_number.setStyleSheet(application_style.line_edit_style)
        layout_LDA_experiment_number.addWidget(self.label_LDA_experiment_number) 
        layout_LDA_experiment_number.addWidget(self.line_edit_LDA_experiment_number)

        layout_LDA_strain = QtWidgets.QVBoxLayout()
        self.label_LDA_strain = QLabel("Strain Name: ")
        self.label_LDA_strain.setStyleSheet(application_style.input_style)
        self.combobox_LDA_strain = QtWidgets.QComboBox()
        self.combobox_LDA_strain.setStyleSheet(application_style.combobox_button_style)
        self.combobox_LDA_strain.addItems(["","Pathogen x", "Pathogen y", "Pathogen z", "N/A"]) 
        layout_LDA_strain.addWidget(self.label_LDA_strain) 
        layout_LDA_strain.addWidget(self.combobox_LDA_strain)

        layout_LDA_fresh_sucrose = QtWidgets.QVBoxLayout()
        self.label_LDA_fresh_sucrose = QLabel("Fresh Sucrose: ")
        self.label_LDA_fresh_sucrose.setStyleSheet(application_style.input_style)
        self.combobox_LDA_fresh_sucrose = QtWidgets.QComboBox()
        self.combobox_LDA_fresh_sucrose.setStyleSheet(application_style.combobox_button_style)
        self.combobox_LDA_fresh_sucrose.addItems(["","Yes", "No", "N/A"]) 
        layout_LDA_fresh_sucrose.addWidget(self.label_LDA_fresh_sucrose) 
        layout_LDA_fresh_sucrose.addWidget(self.combobox_LDA_fresh_sucrose)
        
        layout_LDA_experiment_information.addLayout(layout_LDA_experiment_purpose)
        layout_LDA_experiment_information.addStretch(1)

        layout_LDA_experiment_information.addLayout(layout_LDA_experiment_number)
        layout_LDA_experiment_information.addStretch(1)

        layout_LDA_experiment_information.addLayout(layout_LDA_strain)
        layout_LDA_experiment_information.addStretch(1)

        layout_LDA_experiment_information.addLayout(layout_LDA_fresh_sucrose)
        layout_LDA_experiment_information.addStretch(1)

        
        #endregion
        #================================================================================================================================================================
        # VARIABLE OPTIONS 
        #================================================================================================================================================================
        # region : 
        self.label_LDA_variable_information= QLabel("Data to Track: ")
        self.label_LDA_variable_information.setStyleSheet(application_style.input_style)
        layout_variable_options = QtWidgets.QHBoxLayout()

        #region : temperature and pressure buttons
        layout_variable_options_c1 = QtWidgets.QVBoxLayout()
        self.label_LDA_temperature= QLabel("Temperature: ")
        self.label_LDA_temperature.setStyleSheet(application_style.input_style)
        self.label_LDA_pressure= QLabel("Pressure: ")
        self.label_LDA_pressure.setStyleSheet(application_style.input_style)
        layout_variable_options_c1.addWidget(self.label_LDA_temperature)
        #layout_variable_options_c1.addWidget(self.label_LDA_pressure)

        layout_variable_options_c2 = QtWidgets.QVBoxLayout()

        self.button_LDA_temperature = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_LDA_temperature.setIcon(icon)
        self.button_LDA_temperature.setIconSize(QtCore.QSize(20, 20)) 
        self.reset_button_style(self.button_LDA_temperature)

        self.button_LDA_pressure = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_LDA_pressure.setIcon(icon)
        self.button_LDA_pressure.setIconSize(QtCore.QSize(20, 20)) 
        self.reset_button_style(self.button_LDA_pressure)
        layout_variable_options_c2.addWidget(self.button_LDA_temperature)
        #layout_variable_options_c2.addWidget(self.button_LDA_pressure)

        #endregion 

        #region : voltage and current buttons
        layout_variable_options_c3 = QtWidgets.QVBoxLayout()
        self.label_LDA_current= QLabel("Current: ")
        self.label_LDA_current.setStyleSheet(application_style.input_style)
        self.label_LDA_voltage= QLabel("Voltage: ")
        self.label_LDA_voltage.setStyleSheet(application_style.input_style)
        layout_variable_options_c3.addWidget(self.label_LDA_current)
        layout_variable_options_c3.addWidget(self.label_LDA_voltage)

        layout_variable_options_c4 = QtWidgets.QVBoxLayout()

        self.button_LDA_current = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_LDA_current.setIcon(icon)
        self.button_LDA_current.setIconSize(QtCore.QSize(20, 20)) 
        self.reset_button_style(self.button_LDA_current)

        self.button_LDA_voltage = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_LDA_voltage.setIcon(icon)
        self.button_LDA_voltage.setIconSize(QtCore.QSize(20, 20)) 
        self.reset_button_style(self.button_LDA_voltage)

        layout_variable_options_c4.addWidget(self.button_LDA_current)
        layout_variable_options_c4.addWidget(self.button_LDA_voltage)

        #endregion

        #region : ethanol and sucrose buttons
        layout_variable_options_c5 = QtWidgets.QVBoxLayout()
        self.label_LDA_Ethanol_FR= QLabel("Ethanol Flowrate: ")
        self.label_LDA_Ethanol_FR.setStyleSheet(application_style.input_style)
        self.label_LDA_Sucrose_FR= QLabel("Sucrose Flowrate: ")
        self.label_LDA_Sucrose_FR.setStyleSheet(application_style.input_style)
        layout_variable_options_c5.addWidget(self.label_LDA_Ethanol_FR)
        layout_variable_options_c5.addWidget(self.label_LDA_Sucrose_FR)

        layout_variable_options_c6 = QtWidgets.QVBoxLayout()

        self.button_LDA_Sucrose = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_LDA_Sucrose.setIcon(icon)
        self.button_LDA_Sucrose.setIconSize(QtCore.QSize(20, 20)) 
        self.reset_button_style(self.button_LDA_Sucrose)

        self.button_LDA_Ethanol = QtWidgets.QPushButton()  # create button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/check.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_LDA_Ethanol.setIcon(icon)
        self.button_LDA_Ethanol.setIconSize(QtCore.QSize(20, 20)) 
        self.reset_button_style(self.button_LDA_Ethanol)
        layout_variable_options_c6.addWidget(self.button_LDA_Ethanol)
        layout_variable_options_c6.addWidget(self.button_LDA_Sucrose)
        #endregion

        layout_variable_options.addLayout(layout_variable_options_c1)
        layout_variable_options.addLayout(layout_variable_options_c2)
        layout_variable_options.addStretch(1)
        layout_variable_options.addLayout(layout_variable_options_c3)
        layout_variable_options.addLayout(layout_variable_options_c4)
        layout_variable_options.addStretch(1)
        layout_variable_options.addLayout(layout_variable_options_c5)
        layout_variable_options.addLayout(layout_variable_options_c6)
        layout_variable_options.addStretch(1)
        #endregion
        #================================================================================================================================================================
        # APPLY AND GO LIVE BUTTONS
        #================================================================================================================================================================
        # region : 
        layout_LDA_apply_live = QtWidgets.QHBoxLayout()

        self.button_LDA_apply = QtWidgets.QPushButton("Apply")  # Set the text to empty since we are using an image
        self.reset_button_style(self.button_LDA_apply)

        self.button_LDA_go_live = QtWidgets.QPushButton("Go Live")  # Set the text to empty since we are using an image
        self.button_LDA_go_live.setEnabled(False)
        self.set_button_style(self.button_LDA_go_live, 23, False)


        layout_LDA_apply_live.addWidget(self.button_LDA_apply)
        layout_LDA_apply_live.addStretch(1)
        layout_LDA_apply_live.addWidget(self.button_LDA_go_live)
        layout_LDA_apply_live.addSpacing(10)
        
        main_vertical_layout.addWidget(self.label_LDA_title)
        main_vertical_layout.addWidget(self.label_LDA_instructions)
        main_vertical_layout.addSpacing(20) 
        main_vertical_layout.addLayout(layout_LDA_user_information)
        main_vertical_layout.addSpacing(20) 
        main_vertical_layout.addLayout(layout_LDA_experiment_information)
        main_vertical_layout.addSpacing(20)
        main_vertical_layout.addWidget(self.label_LDA_variable_information)
        main_vertical_layout.addSpacing(20) 
        main_vertical_layout.addLayout(layout_variable_options)
        main_vertical_layout.addSpacing(40) 
        main_vertical_layout.addLayout(layout_LDA_apply_live)
        # endregion

        self.setLayout(main_vertical_layout)
        self.setStyleSheet("background-color: #222222;")


    def reset_button_style(self, button, font_size=23):
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

    def set_button_style(self, button, font_size=23, enabled=True):
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

class EndPopupWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        input_style = "QLabel { color : #FFFFFF; font-family: Archivo; font-size: 23px;  }"
        main_vertical_layout = QtWidgets.QVBoxLayout()
        self.label_end_LDA_title = QLabel("Click Confirm to end this live data aquisiton session: ")
        self.label_end_LDA_title.setStyleSheet(input_style)

        layout_confirm_button = QtWidgets.QHBoxLayout()
        self.button_end_LDA = QtWidgets.QPushButton("Confirm")  # Set the text to empty since we are using an image
        self.button_end_LDA.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 5px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 23px;
                padding: 7px;

            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)
        layout_confirm_button.addWidget(self.button_end_LDA)
        layout_confirm_button.addStretch(1)
        
        main_vertical_layout.addWidget(self.label_end_LDA_title)
        main_vertical_layout.addSpacing(20)
        main_vertical_layout.addLayout(layout_confirm_button)


        self.setLayout(main_vertical_layout)
        self.setStyleSheet("background-color: #222222;")

#=================================
# SYRINGE DIAMETER SETTINGS POP UP
#=================================
class SyringeSettingsPopupWindow(QDialog):
    def __init__(self, title="Default Title", description="Default Description"):
        super().__init__()
        self.title = title
        self.description = description
        self.initUI()

    def initUI(self):
        
        main_vertical_layout = QVBoxLayout()
        #================================================================================================================================================================
        # TITLE AND DESCRIPTION
        #================================================================================================================================================================
        # region :
        self.title = QLabel(self.title)
        self.title.setStyleSheet(application_style.input_style)
        
        self.instructions = QLabel(self.description)
        self.instructions.setStyleSheet(application_style.input_style)
        self.instructions.setFixedWidth(200)  
        self.instructions.setWordWrap(True)
        # endregion
        #================================================================================================================================================================
        # USER INFORMATION
        #================================================================================================================================================================
        # region: 
        layout_h_options = QtWidgets.QHBoxLayout()

        layout_v_options = QtWidgets.QVBoxLayout()
        label= QLabel("Standard Diameters [ml]: ")
        label.setStyleSheet(application_style.input_style)
        self.combobox_options = QtWidgets.QComboBox()
        self.combobox_options.setStyleSheet(application_style.combobox_button_style)
        self.combobox_options.addItems(["9.71","16", "4.75"]) 
        layout_v_options.addWidget(label) 
        layout_v_options.addWidget(self.combobox_options)

        layout_h_options.addLayout(layout_v_options)
        #layout_LDA_user_information.addStretch(1)
        #endregion
        #================================================================================================================================================================
        # APPLY AND GO LIVE BUTTONS
        #================================================================================================================================================================
        # region : 
        layout_apply = QtWidgets.QHBoxLayout()

        self.button_apply = QtWidgets.QPushButton("Apply")  # Set the text to empty since we are using an image
        self.reset_button_style(self.button_apply, 20)
        layout_apply.addWidget(self.button_apply, 20)
        layout_apply.addSpacing(10)
        #endregion
        #================================================================================================================================================================
        # ADDING WIDGETS TO THE PARENT LAYOUT
        #================================================================================================================================================================
        # region :         
        #main_vertical_layout.addWidget(self.title)
        #main_vertical_layout.addWidget(self.instructions)
        #main_vertical_layout.addSpacing(20) 
        main_vertical_layout.addSpacing(20) 
        main_vertical_layout.addLayout(layout_h_options)
        main_vertical_layout.addSpacing(20) 
        #main_vertical_layout.addLayout(layout_apply)
        # endregion
        self.setLayout(main_vertical_layout)
        self.setStyleSheet("background-color: #222222;")

    def reset_button_style(self, button, font_size=23):
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

    def set_button_style(self, button, font_size=23, enabled=True):
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