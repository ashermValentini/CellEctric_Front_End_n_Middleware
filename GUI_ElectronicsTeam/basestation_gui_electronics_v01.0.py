import sys

# from ..Communication_Functions.pgpsu_communication_functions import *
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Communication_Functions.pgpsu_communication_functions import *


from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QLabel, QButtonGroup
from PyQt5.QtCore import pyqtSlot, QFile, QTextStream
from pathlib import Path

from Ui_GUI_Design_01 import Ui_MainWindow

#import psu_pg_functions


SUCROSE_FLOWRATE_MAX = 10
ETHANOL_FLOWRATE_MAX = 10
BLOOD_FLOWRATE_MAX = 5





class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # VARIABLES

        # FLAGS TEST
        self.flag_psu_on = False
        self.flag_pg_on = False
        self.flag_3pac_on = False

        self.flag_suceth_on = False
        self.flag_blood_on = False

        self.flag_valve1 = False
        self.flag_valve1 = False
        self.flag_valve1 = False

        self.flag_state = 0


        # SETUP
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.stackedWidget.setCurrentIndex(0)


        # SET PROGRESS BARS TO ZERO & LABEL TO "OFF"
        style_sheets = """
            QFrame{
                border-radius: 80px;
                background-color: qconicalgradient(cx:0.5, cy:0.5, angle:230, stop:0.9 rgba(138, 201, 38, 0), stop:1.0 rgba(138, 201, 38, 255));
                }"""
        self.ui.circularProgress_suc_eth.setStyleSheet(style_sheets)
        self.ui.circularProgress_blood.setStyleSheet(style_sheets)

        self.ui.value_flowrate_suc_eth.setText("OFF")
        self.ui.value_flowrate_blood.setText("OFF")

        # SET INDIVIDUAL VALVE BUTTONS DISABLED AT STARTUP
        self.ui.button_toggle_valve1.setEnabled(False)
        self.ui.button_toggle_valve2.setEnabled(False)
        self.ui.button_toggle_valve3.setEnabled(False)

        # SETUP BUTTON GROUPS
        self.ui.btngroup_valve_states.setExclusive(True)

        # BUTTON CLICKS
        self.ui.button_toggle_psu_enable.clicked.connect(self.psu_button_toggle)
        self.ui.button_toggle_pg_enable.clicked.connect(self.pg_button_toggle)
        self.ui.button_toggle_3pac_enable.clicked.connect(self.pac_button_toggle)

        self.ui.button_toggle_sucethflow.clicked.connect(self.toggle_flow_suceth)
        self.ui.button_toggle_bloodflow.clicked.connect(self.toggle_flow_blood)

        self.ui.button_update_sucethflow.clicked.connect(self.update_flowrate_suceth)
        self.ui.button_update_bloodflow.clicked.connect(self.update_flowrate_blood)

        self.ui.button_valvestate_sucrose.clicked.connect(self.change_valve_state_sucrose)
        self.ui.button_valvestate_ethanol.clicked.connect(self.change_valve_state_ethanol)
        self.ui.button_valvestate_cleaning.clicked.connect(self.change_valve_state_cleaning)


        # =================
        # START SERIAL CONNECTION TO DEVICES
        # =================
        self.device_serials = serial_start_connections()
        self.ui.display_system_log.append("Connection to Devices established:")
        for device_serial in self.device_serials:
            self.ui.display_system_log.append("Port: " + device_serial.name)


    # =================================================
    # FLOW RATES - UPDATES & TOGGLES
    # =================================================

    def update_flowrate_suceth(self):

        # READ AND CHECK INPUT
        input_value_float, input_value_string = self.input_check_suceth()
        if input_value_float == -1:
            return

        # UPDATE LABEL
        if self.flag_suceth_on:
            self.ui.value_flowrate_suc_eth.setText(input_value_string)

        # PROGRESS BAR VALUE
        # needs to be inverted: 1.0 is empty, 0.0 is full
        progress_value = 1 - (input_value_float / SUCROSE_FLOWRATE_MAX)  # SCALING AND INVERTING
        stop_1 = str(progress_value - 0.001)
        stop_2 = str(progress_value)

        style_sheet = """
        QFrame{
            border-radius: 80px;
            background-color: qconicalgradient(cx:0.5, cy:0.5, angle:230, stop:{STOP_1} rgba(138, 201, 38, 0), stop:{STOP_2} rgba(138, 201, 38, 255));
            }""".replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)
            
        self.ui.circularProgress_suc_eth.setStyleSheet(style_sheet)
        
    
    def update_flowrate_blood(self):
        
        # READ AND CHECK INPUT
        input_value_float, input_value_string = self.input_check_blood()
        if input_value_float == -1:
            return

        # UPDATE LABEL
        if self.flag_blood_on:
            self.ui.value_flowrate_blood.setText(input_value_string)

        # PROGRESS BAR VALUE
        # needs to be inverted: 1.0 is empty, 0.0 is full
        progress_value = 1 - (input_value_float / BLOOD_FLOWRATE_MAX)  # SCALING AND INVERTING
        stop_1 = str(progress_value - 0.001)
        stop_2 = str(progress_value)

        style_sheet = """
        QFrame{
            border-radius: 80px;
            background-color: qconicalgradient(cx:0.5, cy:0.5, angle:230, stop:{STOP_1} rgba(138, 201, 38, 0), stop:{STOP_2} rgba(138, 201, 38, 255));
            }""".replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)
            
        self.ui.circularProgress_blood.setStyleSheet(style_sheet)


    def toggle_flow_suceth(self):
        if self.flag_suceth_on:
            self.ui.value_flowrate_suc_eth.setText("OFF")
            self.ui.display_system_log.append("SUC/ETH: OFF")
            self.flag_suceth_on = False

        else:
            input_value_float, input_value_string = self.input_check_suceth()
            self.ui.value_flowrate_suc_eth.setText(input_value_string)
            self.ui.display_system_log.append("SUC/ETH: ON")
            self.flag_suceth_on = True


    def toggle_flow_blood(self):
        if self.flag_blood_on:
            self.ui.value_flowrate_blood.setText("OFF")
            self.ui.display_system_log.append("Blood: OFF")
            self.flag_blood_on = False

        else:
            input_value_float, input_value_string = self.input_check_suceth()
            self.ui.value_flowrate_blood.setText(input_value_string)
            self.ui.display_system_log.append("Blood: ON")
            self.flag_blood_on = True
        
    # INPUT CHECK
    def input_check_suceth(self):
        # READ INPUT VALUE
        input_value = self.ui.userInput_flowrate_suceth.text()

        # IF NO VALUE IS ENTERED
        if input_value == "":
            input_value_float = 0.00
            input_value_string = "0.00"
        else:
            try:
                input_value_float = float(input_value)

                # CHECK RANGE
                if input_value_float < 0 :
                    input_value_float = 0.00
                
                if input_value_float > SUCROSE_FLOWRATE_MAX:
                    input_value_float = SUCROSE_FLOWRATE_MAX

                input_value_string = "{0:.2f}".format(input_value_float)
                
            except:
                self.ui.userInput_flowrate_suceth.setText("")
                self.ui.display_system_log.append("NUMBER FORMAT ERROR")
                return -1, "ERR"
            
        self.ui.userInput_flowrate_suceth.setText(input_value_string)    
        self.ui.display_system_log.append("SUC/ETH flowrate set to {} ml/min".format(input_value_string))

        return input_value_float, input_value_string


    def input_check_blood(self):
        # READ INPUT VALUE
        input_value = self.ui.userInput_flowrate_blood.text()

        # IF NO VALUE IS ENTERED
        if input_value == "":
            input_value_float = 0.00
            input_value_string = "0.00"
        else:
            try:
                input_value_float = float(input_value)

                # CHECK RANGE
                if input_value_float < 0 :
                    input_value_float = 0.00
                
                if input_value_float > BLOOD_FLOWRATE_MAX:
                    input_value_float = BLOOD_FLOWRATE_MAX

                input_value_string = "{0:.2f}".format(input_value_float)
                
            except:
                self.ui.userInput_flowrate_blood.setText("")
                self.ui.display_system_log.append("NUMBER FORMAT ERROR")
                return -1, "ERR"
            
        self.ui.userInput_flowrate_blood.setText(input_value_string)    
        self.ui.display_system_log.append("Blood flowrate set to {} ml/min".format(input_value_string))

        return input_value_float, input_value_string





    # =================================================
    # DEVICE TOGGLES
    # =================================================

    def psu_button_toggle(self):
        # PSU IS SWITCHING OFF
        if self.flag_psu_on:
            sucess = send_PSU_enable(self.device_serials[0], 1)

            # CHECK IF DATA WAS SENT SUCESSFULLY
            if sucess:                                          # SENDING SUCESSFUL
                self.ui.display_system_log.append("PSU: OFF")   # LOG TO GUI
                self.flag_psu_on = False                        # SET FLAG FOR PSU STATE
            else:                                                                       # SENDING NOT POSSIBLE (5 tries)
                self.ui.display_system_log.append("ERROR: Could not switch PSU OFF")    # LOG TO GUI
                self.ui.button_toggle_psu_enable.setChecked(True)                       # SET THE BUTTON TO "ON" AGAIN

        # PSU IS SWITCHING ON
        else:
            sucess = send_PSU_disable(self.device_serials[0], 1)
            if sucess:
                self.ui.display_system_log.append("PSU: ON")
                self.flag_psu_on = True
            else: 
                self.ui.display_system_log.append("ERROR: Could not switch PSU ON")
                self.ui.button_toggle_psu_enable.setChecked(False)


    def pg_button_toggle(self):
        if self.flag_pg_on:
            self.ui.display_system_log.append("PG: OFF")
            self.flag_pg_on = False
        else:
            self.ui.display_system_log.append("PG: ON")
            self.flag_pg_on = True

    def pac_button_toggle(self):
        if self.flag_3pac_on:
            self.ui.display_system_log.append("3PAC: OFF")
            self.flag_3pac_on = False
        else:
            self.ui.display_system_log.append("3PAC: ON")
            self.flag_3pac_on = True

    # VALVE CONTROL

    def change_valve_state_sucrose(self):
        self.ui.display_system_log.append("VALVES: SUCROSE")

    def change_valve_state_ethanol(self):
        self.ui.display_system_log.append("VALVES: ETHANOL")

    def change_valve_state_cleaning(self):
        self.ui.display_system_log.append("VALVES: CLEANING")

    



# =================================================
# .___  ___.      ___       __  .__   __. 
# |   \/   |     /   \     |  | |  \ |  | 
# |  \  /  |    /  ^  \    |  | |   \|  | 
# |  |\/|  |   /  /_\  \   |  | |  . `  | 
# |  |  |  |  /  _____  \  |  | |  |\   | 
# |__|  |__| /__/     \__\ |__| |__| \__| 
#                                         
# =================================================

if __name__ == "__main__":
    # OPEN THE WINDOW
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('GUI_ElectronicsTeam/style.qss').read_text())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
