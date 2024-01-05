# =======================================================
# ██ ███    ███ ██████   ██████  ██████  ████████ ███████
# ██ ████  ████ ██   ██ ██    ██ ██   ██    ██    ██     
# ██ ██ ████ ██ ██████  ██    ██ ██████     ██    ███████
# ██ ██  ██  ██ ██      ██    ██ ██   ██    ██         ██
# ██ ██      ██ ██       ██████  ██   ██    ██    ███████
# =======================================================
import sys                                                                              # IMPORT SYSTEM: TO GET THE ABSOLUTE PATH
import os                                                                               # IMPORT OPERATING SYSTEM: TO GET THE ABSOLUTE PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))            # GET THE ABSOLUT PATH FOR THE WHOLE PROJECT: TO FIND THE "communication_functions.py" FILE
from Communication_Functions.communication_functions import *                           # IMPORT ALL COMMUNICATION FUNCTIONS

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QLabel, QButtonGroup, QVBoxLayout    # TODO: DELETE THE IMPORTS THAT ARE NOT NEEDED
from PyQt5.QtCore import Qt, pyqtSlot, QFile, QTextStream, QTimer                                                   # TODO: DELETE THE IMPORTS THAT ARE NOT NEEDED
from PyQt5.QtGui import QColor                                                                                      # TODO: DELETE THE IMPORTS THAT ARE NOT NEEDED
from PyQt5.uic import loadUi
from pathlib import Path

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas    # IMPORT GRAPH LIBRARY MATPLOTLIB FOR QT
from matplotlib.figure import Figure                                                # IMPORT GRAPHS (NOT USED)
import matplotlib.ticker as ticker                                                  # IMPORT TICKER FOR GRAPH UPDATES (NOT USED)

import numpy as np                                                                  

from Ui_GUI_Design_01 import Ui_MainWindow


# ==============================================================================
#  ██████  ██████  ███    ██ ███████ ████████  █████  ███    ██ ████████ ███████
# ██      ██    ██ ████   ██ ██         ██    ██   ██ ████   ██    ██    ██     
# ██      ██    ██ ██ ██  ██ ███████    ██    ███████ ██ ██  ██    ██    ███████
# ██      ██    ██ ██  ██ ██      ██    ██    ██   ██ ██  ██ ██    ██         ██
#  ██████  ██████  ██   ████ ███████    ██    ██   ██ ██   ████    ██    ███████
# ==============================================================================
# DEBUGGING
DEBUG = True

# FLOWRATES 
SUCROSE_FLOWRATE_MAX = 10   # MAXIMUM FLOW RATE FOR SUCROSE
ETHANOL_FLOWRATE_MAX = 10   # MAXIMUM FLOW RATE FOR ETHANOL
BLOOD_FLOWRATE_MAX = 2.5    # MAXIMUM FLOW RATE FOR BLOOD

# VOLTAGE PULSE
VOLTAGE_PSU_MAX = 60            # MAXIMUM POSITIVE AND NEGATIVE VOLTAGE FOR THE PSU
REPETITION_FREQUENCY_MIN = 1    # MINIMUM REPETITION FREQUENCY FOR PULSE
REPETITION_FREQUENCY_MAX = 500  # MAXIMUM REPETITION FREQUENCY FOR PULSE
PULSE_LENGTH_MIN = 10           # MINIMUM PULSE LENGTH FOR PULSE
PULSE_LENGTH_MAX = 250          # MAXIMUM PULSE LENGTH FOR PULSE
ON_TIME_MIN = 5                 # MINIMUM ON-TIME FOR PULSE
ON_TIME_MAX = 248               # MAXIMUM ON-TIME FOR PULSE


# DIRECTIONS
DIR_M1_UP = -1              # DIRECTION FOR MOTOR 1 (BLOOD): UP
DIR_M1_DOWN = -DIR_M1_UP    # DIRECTION FOR MOTOR 1 (BLOOD): DOWN
DIR_M2_UP = 1               # DIRECTION FOR MOTOR 2 (CARTRIDGE CONNECTOR): UP
DIR_M2_DOWN = -DIR_M2_UP    # DIRECTION FOR MOTOR 2 (CARTRIDGE CONNECTOR): DOWN
DIR_M3_RIGHT = -1           # DIRECTION FOR MOTOR 3 (FLASK X-AXIS): RIGHT
DIR_M3_LEFT = -DIR_M3_RIGHT # DIRECTION FOR MOTOR 3 (FLASK X-AXIS): LEFT
DIR_M4_UP = 1               # DIRECTION FOR MOTOR 4 (FLASK Z-AXIS): UP
DIR_M4_DOWN = -DIR_M4_UP    # DIRECTION FOR MOTOR 4 (FLASK Z-AXIS): DOWN




# ==================================================================================================================================================================================================
# ███    ███  █████  ██ ███    ██     ██     ██ ██ ███    ██ ██████   ██████  ██     ██        ██         ██████  ██████  ███    ██ ███    ██ ███████  ██████ ████████ ██  ██████  ███    ██ ███████
# ████  ████ ██   ██ ██ ████   ██     ██     ██ ██ ████   ██ ██   ██ ██    ██ ██     ██        ██        ██      ██    ██ ████   ██ ████   ██ ██      ██         ██    ██ ██    ██ ████   ██ ██     
# ██ ████ ██ ███████ ██ ██ ██  ██     ██  █  ██ ██ ██ ██  ██ ██   ██ ██    ██ ██  █  ██     ████████     ██      ██    ██ ██ ██  ██ ██ ██  ██ █████   ██         ██    ██ ██    ██ ██ ██  ██ ███████
# ██  ██  ██ ██   ██ ██ ██  ██ ██     ██ ███ ██ ██ ██  ██ ██ ██   ██ ██    ██ ██ ███ ██     ██  ██       ██      ██    ██ ██  ██ ██ ██  ██ ██ ██      ██         ██    ██ ██    ██ ██  ██ ██      ██
# ██      ██ ██   ██ ██ ██   ████      ███ ███  ██ ██   ████ ██████   ██████   ███ ███      ██████        ██████  ██████  ██   ████ ██   ████ ███████  ██████    ██    ██  ██████  ██   ████ ███████
# ==================================================================================================================================================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()  # START THE MAIN WINDOW

        # ===============================
        #  _____ __    _____ _____ _____ 
        # |   __|  |  |  _  |   __|   __|
        # |   __|  |__|     |  |  |__   |
        # |__|  |_____|__|__|_____|_____|
        # ===============================
        self.flag_connections = [False, False, False, False]        # CONNECTION FLAGS TO DISPLAY THE DEVICE STATUS (CONNECTED / NOT CONNECTED / ERROR)
        #                       [PSU  , PG   , 3PAC , TEMPSENS]

        self.flag_psu_on = False        # FLAG FOR PSU-STATUS (ON / OFF)
        self.flag_pg_on = False         # FLAG FOR PG-STATUS (ON / OFF)
        self.flag_3pac_on = False       # FLAG FOR 3PAC-STATUS (ON / OFF)

        self.flag_suc_on = False        # FLAG FOR SUCROSE-PUMP & VALVE STATUS (ON / OFF)
        self.flag_eth_on = False        # FLAG FOR ETHANOL-PUMP & VALVE STATUS (ON / OFF)
        self.flag_suc_pid = False       # FLAG FOR SUCROSE-PUMP PID-MODE
        self.flag_eth_pid = False       # FLAG FOR ETHANOL-PUMP PID-MODE
        self.flag_blood_on = False      # FLAG FOR THE BLOOD-SYRINGE-PUMP (ON / OFF)

        self.flag_valve1 = False        # FLAG FOR THE VALVE STATUS OF VALVE1
        self.flag_valve1 = False        # FLAG FOR THE VALVE STATUS OF VALVE1
        self.flag_valve1 = False        # FLAG FOR THE VALVE STATUS OF VALVE1

        self.flag_state = 0             # TODO: NOT USED YET. DON'T KNOW WHAT I THOUGHT I WOULD NEED IT FOR

        # FLASK POSITIONS
        self.POS_FLASK_PARK_X = 30      # X-POSITION FOR FLASK: PARKING POSITION
        self.POS_FLASK_PARK_Z = 5       # Z-POSITION FOR FLASK: PARKING POSITION
        self.POS_FLASK1       = 0       # X-POSITION FOR FLASK NUMBER 1
        self.POS_FLASK2       = 60      # X-POSITION FOR FLASK NUMBER 1
        self.POS_FLASK3       = 120     # X-POSITION FOR FLASK NUMBER 1
        self.POS_FLASK4       = 180     # X-POSITION FOR FLASK NUMBER 1
        self.POS_FLASK_DOWN   = 0       # Z-POSITION FOR FLASK: DISCONNECTED (DOWN)
        self.POS_FLASK_UP     = 13      # Z-POSITION FOR FLASK: CONNECTED (UP)

        # TIMERS
        self.flow_timer = QTimer()
        self.flow_timer.setInterval(self.interval)
        self.flow_timer.timeout.connect(self.update_flowrate_suceth)

        self.plot_timer = QTimer()
        self.plot_timer.setInterval(self.interval)
        self.plot_timer.timeout.connect(self.update_plot)

        # ================================================================
        #  _____ _____ _____ _____    _ _ _ _____ _____ ____  _____ _ _ _ 
        # |     |  _  |     |   | |  | | | |     |   | |    \|     | | | |
        # | | | |     |-   -| | | |  | | | |-   -| | | |  |  |  |  | | | |
        # |_|_|_|__|__|_____|_|___|  |_____|_____|_|___|____/|_____|_____|
        # ================================================================
        self.ui = Ui_MainWindow()                   # START THE MAIN WINDOW
        self.ui.setupUi(self)                       # SETUP THE MAIN WINDOW
        self.ui.stackedWidget.setCurrentIndex(0)    # SET THE TAB TO THE MAIN TAB (DASHBOARD)


        # ========================================================================================
        #  _____ _____ _____ _____ _____ _____ _____    _____ _____ __ __ __    _____ _____ _____ 
        # |   __|_   _|  _  | __  |_   _|  |  |  _  |  |   __|_   _|  |  |  |  |     |   | |   __|
        # |__   | | | |     |    -| | | |  |  |   __|  |__   | | | |_   _|  |__|-   -| | | |  |  |
        # |_____| |_| |__|__|__|__| |_| |_____|__|     |_____| |_|   |_| |_____|_____|_|___|_____|
        # ========================================================================================
        # SET PROGRESS BARS TO ZERO & LABEL TO "OFF"
        style_sheets = """
            QFrame{
                border-radius: 60px;
                background-color: qconicalgradient(cx:0.5, cy:0.5, angle:230, stop:0.9 rgba(7, 150, 255, 0), stop:1.0 rgba(7, 150, 255, 255));
                }"""
        self.ui.circularProgress_suc_eth.setStyleSheet(style_sheets)    # ADD "OFF" STYLE SHEET TO SUCROSE/ETHANOL GRAPH
        self.ui.circularProgress_blood.setStyleSheet(style_sheets)      # ADD "OFF" STYLE SHEET TO BLOOD GRAPH
        self.ui.value_flowrate_suc_eth.setText("OFF")                   # SET TEXT TO "OFF"
        self.ui.value_flowrate_blood.setText("OFF")                     # SET TEXT TO "OFF"

        # SET INDIVIDUAL VALVE BUTTONS "DISABLED" AT STARTUP
        self.ui.button_toggle_valve1.setEnabled(False)
        self.ui.button_toggle_valve2.setEnabled(False)
        self.ui.button_toggle_valve3.setEnabled(False)
        # SET VALVE BUTTON GROUP TO OFF
        self.ui.button_valvestate_off.setChecked(True)
        # SETUP BUTTON GROUPS
        self.ui.btngroup_valve_states.setExclusive(True)

        # ===========================================================================================
        #  _____ _____ _____ _____ _____ _____ _____    _____ _____ _____ _____ _____ _____ _____ 
        # |     |     |   | |   | |   __|     |_   _|  | __  |  |  |_   _|_   _|     |   | |   __|
        # |   --|  |  | | | | | | |   __|   --| | |    | __ -|  |  | | |   | | |  |  | | | |__   |
        # |_____|_____|_|___|_|___|_____|_____| |_|    |_____|_____| |_|   |_| |_____|_|___|_____|
        # ===========================================================================================

        #  _____                _____     _   _               
        # |     |___ ___ _ _   | __  |_ _| |_| |_ ___ ___ ___ 
        # | | | | -_|   | | |  | __ -| | |  _|  _| . |   |_ -|
        # |_|_|_|___|_|_|___|  |_____|___|_| |_| |___|_|_|___|
        #
        # SET THE SIDEBAR MENU
        self.ui.menu_dashboard_button_1.clicked.connect(self.menu_button_dashboard_click)       # SET SIDEBAR TO "DASHBOARD"
        self.ui.menu_control_button_1.clicked.connect(self.menu_button_control_click)           # SET SIDEBAR TO "CONTROL"
        self.ui.menu_graphs_button_1.clicked.connect(self.menu_button_graphs_click)             # SET SIDEBAR TO "GRAPHS"   (TODO: STILL EMPTY, MAYBE NOT NEEDED)
        self.ui.menu_settings_button_1.clicked.connect(self.menu_button_settings_click)         # SET SIDEBAR TO "SETTINGS" (TODO: STILL EMPTY, MAYBE NOT NEEDED)

        #  ____          _            _____     _   _               
        # |    \ ___ _ _|_|___ ___   | __  |_ _| |_| |_ ___ ___ ___ 
        # |  |  | -_| | | |  _| -_|  | __ -| | |  _|  _| . |   |_ -|
        # |____/|___|\_/|_|___|___|  |_____|___|_| |_| |___|_|_|___|
        #
        # Toggle PG, PSU, 3PAC
        self.ui.button_toggle_psu_enable.clicked.connect(self.psu_button_toggle)                    # TOGGLE PSU: ENABLE/DISABLE
        self.ui.button_toggle_pg_enable.clicked.connect(self.pg_button_toggle)                      # TOGGLE PG: ENABLE/DISABLE

        self.ui.button_toggle_sucflow.clicked.connect(self.toggle_flow_suc)                         # TOGGLE SUCROSE FLOW: ON/OFF
        self.ui.button_toggle_ethflow.clicked.connect(self.toggle_flow_eth)                         # TOGGLE ETHANOL FLOW: ON/OFF
        self.ui.button_toggle_bloodflow.clicked.connect(self.toggle_flow_blood)                     # TOGGLE BLOOD FLOW: ON/OFF

        self.ui.button_valvestate_off.clicked.connect(lambda: self.change_valve_state_path(0))      # TOGGLE VALVE PATH: COMPLETELY OFF
        self.ui.button_valvestate_sucrose.clicked.connect(lambda: self.change_valve_state_path(1))  # TOGGLE VALVE PATH: SUCROSE PATH
        self.ui.button_valvestate_ethanol.clicked.connect(lambda: self.change_valve_state_path(2))  # TOGGLE VALVE PATH: ETHANOL PATH
        self.ui.button_valvestate_cleaning.clicked.connect(lambda: self.change_valve_state_path(3)) # TOGGLE VALVE PATH: CLEANING PATH
        
        # OLD VALVE IMPLEMENTATION
        #self.ui.button_valvestate_sucrose.clicked.connect(self.change_valve_state_sucrose)         # TOGGLE VALVE PATH: SUCROSE PATH
        #self.ui.button_valvestate_ethanol.clicked.connect(self.change_valve_state_ethanol)         # TOGGLE VALVE PATH: ETHANOL PATH
        #self.ui.button_valvestate_cleaning.clicked.connect(self.change_valve_state_cleaning)       # TOGGLE VALVE PATH: CLEANING PATH
        #self.ui.button_valvestate_off.clicked.connect(self.change_valve_state_off)                 # TOGGLE VALVE PATH: COMPLETELY OFF

        self.ui.button_toggle_valve1.clicked.connect(self.change_single_valve)                      # TOGGLE INDIVIDUAL VALVE: VALVE 1
        self.ui.button_toggle_valve2.clicked.connect(self.change_single_valve)                      # TOGGLE INDIVIDUAL VALVE: VALVE 2
        self.ui.button_toggle_valve3.clicked.connect(self.change_single_valve)                      # TOGGLE INDIVIDUAL VALVE: VALVE 3


        # PSU BUTTONS
        self.ui.button_apply_voltages.clicked.connect(self.psu_set_voltage)                         # SET PSU VOLTAGE

        # PG BUTTONS
        self.ui.button_toggle_logging.clicked.connect(self.pg_logging_toggle)                       # TOGGLE DATA LOGGING FOR PG

        # PRESSURE UP SYSTEM
        self.ui.button_apply_system_pressure.clicked.connect(self.apply_pressure)                   # SET THE PRESSURE THAT NEEDS TO BE APPLIED



        #  _____                           _      _____     _   _               
        # |     |___ _ _ ___ _____ ___ ___| |_   | __  |_ _| |_| |_ ___ ___ ___ 
        # | | | | . | | | -_|     | -_|   |  _|  | __ -| | |  _|  _| . |   |_ -|
        # |_|_|_|___|\_/|___|_|_|_|___|_|_|_|    |_____|___|_| |_| |___|_|_|___|
        #
        # ALL MOTOR FUNCTIONS
        # HOMING
        self.ui.button_homing_all.clicked.connect(lambda: self.movement_homing(0))              # BUTTON: HOME ALL MOTORS --> CALL FUNCTION "movement_homing(motornumber=0)"
        self.ui.button_homing_blood.clicked.connect(lambda: self.movement_homing(1))            # BUTTON: HOME ALL MOTORS --> CALL FUNCTION "movement_homing(motornumber=1)"
        self.ui.button_homing_cartridge.clicked.connect(lambda: self.movement_homing(2))        # BUTTON: HOME ALL MOTORS --> CALL FUNCTION "movement_homing(motornumber=2)"
        self.ui.button_homing_flasks_lr.clicked.connect(lambda: self.movement_homing(3))        # BUTTON: HOME ALL MOTORS --> CALL FUNCTION "movement_homing(motornumber=3)"
        self.ui.button_homing_flasks_ud.clicked.connect(lambda: self.movement_homing(4))        # BUTTON: HOME ALL MOTORS --> CALL FUNCTION "movement_homing(motornumber=4)"

        # JOGGING BLOOD
        self.ui.move_blood_upfast.pressed.connect(lambda: self.movement_startjogging(1, DIR_M1_UP, True))       # PRESSED: START JOGGING BLOOD UP FAST --> CALL FUNCTION "movement_startjogging(motornumber=1, direction=M1_UP, fast=True)"
        self.ui.move_blood_upfast.released.connect(lambda: self.movement_stopjogging(1))                        # RELEASED: STOP JOGGING BLOOD

        self.ui.move_blood_upslow.pressed.connect(lambda: self.movement_startjogging(1, DIR_M1_UP, False))      # PRESSED: START JOGGING BLOOD UP SLOW --> CALL FUNCTION "movement_startjogging(motornumber=1, direction=M1_UP, fast=False)"
        self.ui.move_blood_upslow.released.connect(lambda: self.movement_stopjogging(1))                        # RELEASED: STOP JOGGING BLOOD

        self.ui.move_blood_downfast.pressed.connect(lambda: self.movement_startjogging(1, DIR_M1_DOWN, True))   # PRESSED: START JOGGING BLOOD DOWN FAST --> CALL FUNCTION "movement_startjogging(motornumber=1, direction=M1_DOWN, fast=True)"
        self.ui.move_blood_downfast.released.connect(lambda: self.movement_stopjogging(1))                      # RELEASED: STOP JOGGING BLOOD

        self.ui.move_blood_downslow.pressed.connect(lambda: self.movement_startjogging(1, DIR_M1_DOWN, False))  # PRESSED: START JOGGING BLOOD UP FAST --> CALL FUNCTION "movement_startjogging(motornumber=1, direction=M1_DOWN, fast=False)"
        self.ui.move_blood_downslow.released.connect(lambda: self.movement_stopjogging(1))                      # RELEASED: STOP JOGGING BLOOD

        # JOGGING CARTRIDGE
        self.ui.move_cartridge_upfast.pressed.connect(lambda: self.movement_startjogging(2, DIR_M2_UP, True))     #(self, motornumber, direction, fast)
        self.ui.move_cartridge_upfast.released.connect(lambda: self.movement_stopjogging(2))               #(self, motornumber)

        self.ui.move_cartridge_upslow.pressed.connect(lambda: self.movement_startjogging(2, DIR_M2_UP, False))
        self.ui.move_cartridge_upslow.released.connect(lambda: self.movement_stopjogging(2))

        self.ui.move_cartridge_downfast.pressed.connect(lambda: self.movement_startjogging(2, DIR_M2_DOWN, True))
        self.ui.move_cartridge_downfast.released.connect(lambda: self.movement_stopjogging(2))

        self.ui.move_cartridge_downslow.pressed.connect(lambda: self.movement_startjogging(2, DIR_M2_DOWN, False))
        self.ui.move_cartridge_downslow.released.connect(lambda: self.movement_stopjogging(2))

        # JOGGING FLASKS HORIZONTAL
        self.ui.move_flasks_leftfast.pressed.connect(lambda: self.movement_startjogging(3, DIR_M3_LEFT, True))     #(self, motornumber, direction, fast)
        self.ui.move_flasks_leftfast.released.connect(lambda: self.movement_stopjogging(3))               #(self, motornumber)

        self.ui.move_flasks_leftslow.pressed.connect(lambda: self.movement_startjogging(3, DIR_M3_LEFT, False))
        self.ui.move_flasks_leftslow.released.connect(lambda: self.movement_stopjogging(3))

        self.ui.move_flasks_rightfast.pressed.connect(lambda: self.movement_startjogging(3, DIR_M3_RIGHT, True))
        self.ui.move_flasks_rightfast.released.connect(lambda: self.movement_stopjogging(3))

        self.ui.move_flasks_rightslow.pressed.connect(lambda: self.movement_startjogging(3, DIR_M3_RIGHT, False))
        self.ui.move_flasks_rightslow.released.connect(lambda: self.movement_stopjogging(3))

        # JOGGING FLASKS VERTICAL
        self.ui.move_flasks_upfast.pressed.connect(lambda: self.movement_startjogging(4, DIR_M4_UP, True))     #(self, motornumber, direction, fast)
        self.ui.move_flasks_upfast.released.connect(lambda: self.movement_stopjogging(4))               #(self, motornumber)

        self.ui.move_flasks_upslow.pressed.connect(lambda: self.movement_startjogging(4, DIR_M4_UP, False))
        self.ui.move_flasks_upslow.released.connect(lambda: self.movement_stopjogging(4))

        self.ui.move_flasks_downfast.pressed.connect(lambda: self.movement_startjogging(4, DIR_M4_DOWN, True))
        self.ui.move_flasks_downfast.released.connect(lambda: self.movement_stopjogging(4))

        self.ui.move_flasks_downslow.pressed.connect(lambda: self.movement_startjogging(4, DIR_M4_DOWN, False))
        self.ui.move_flasks_downslow.released.connect(lambda: self.movement_stopjogging(4))

        # TRAVEL BLOOD
        self.ui.move_blood_up_10.clicked.connect(lambda: self.movement_relative(1, DIR_M1_UP*10))                 #(self, motornumber, distance)
        self.ui.move_blood_up_1.clicked.connect(lambda: self.movement_relative(1, DIR_M1_UP*1))
        self.ui.move_blood_up_01.clicked.connect(lambda: self.movement_relative(1, DIR_M1_UP*0.1))
        self.ui.move_blood_down_10.clicked.connect(lambda: self.movement_relative(1, DIR_M1_DOWN*10))
        self.ui.move_blood_down_1.clicked.connect(lambda: self.movement_relative(1, DIR_M1_DOWN*1))
        self.ui.move_blood_down_01.clicked.connect(lambda: self.movement_relative(1, DIR_M1_DOWN*0.1))

        self.ui.move_blood_bottom.clicked.connect(lambda: self.movement_relative(1, DIR_M1_DOWN*200))           # JUST MOVE VERY FAR (1m) AND REACH THE END
        self.ui.move_blood_top.clicked.connect(lambda: self.movement_relative(1, DIR_M1_UP*200))

        # TRAVEL CARTRIDGE
        self.ui.move_cartridge_up_10.clicked.connect(lambda: self.movement_relative(2, DIR_M2_UP*10))                 #(self, motornumber, distance)
        self.ui.move_cartridge_up_1.clicked.connect(lambda: self.movement_relative(2, DIR_M2_UP*1))
        self.ui.move_cartridge_up_01.clicked.connect(lambda: self.movement_relative(2, DIR_M2_UP*0.1))
        self.ui.move_cartridge_down_10.clicked.connect(lambda: self.movement_relative(2, DIR_M2_DOWN*10))
        self.ui.move_cartridge_down_1.clicked.connect(lambda: self.movement_relative(2, DIR_M2_DOWN*1))
        self.ui.move_cartridge_down_01.clicked.connect(lambda: self.movement_relative(2, DIR_M2_DOWN*0.1))

        self.ui.move_cartridge_bottom.clicked.connect(lambda: self.movement_relative(2, DIR_M2_DOWN*200))           # JUST MOVE VERY FAR (1m) AND REACH THE END
        self.ui.move_cartridge_top.clicked.connect(lambda: self.movement_relative(2, DIR_M2_UP*200))

        # TRAVEL FLASKS HORIZONTAL
        self.ui.move_flasks_left_10.clicked.connect(lambda: self.movement_relative(3, DIR_M3_LEFT*10))                 #(self, motornumber, distance)
        self.ui.move_flasks_left_1.clicked.connect(lambda: self.movement_relative(3, DIR_M3_LEFT*1))
        self.ui.move_flasks_left_01.clicked.connect(lambda: self.movement_relative(3, DIR_M3_LEFT*0.1))
        self.ui.move_flasks_right_10.clicked.connect(lambda: self.movement_relative(3, DIR_M3_RIGHT*10))
        self.ui.move_flasks_right_1.clicked.connect(lambda: self.movement_relative(3, DIR_M3_RIGHT*1))
        self.ui.move_flasks_right_01.clicked.connect(lambda: self.movement_relative(3, DIR_M3_RIGHT*0.1))

        self.ui.move_flasks_rightmost.clicked.connect(lambda: self.movement_relative(3, DIR_M3_RIGHT*200))           # JUST MOVE VERY FAR (1m) AND REACH THE END
        self.ui.move_flasks_leftmost.clicked.connect(lambda: self.movement_relative(3, DIR_M3_LEFT*200))

        # TRAVEL FLASKS VERTICAL
        self.ui.move_flasks_up_10.clicked.connect(lambda: self.movement_relative(4, DIR_M4_UP*10))                 #(self, motornumber, distance)
        self.ui.move_flasks_up_1.clicked.connect(lambda: self.movement_relative(4, DIR_M4_UP*1))
        self.ui.move_flasks_up_01.clicked.connect(lambda: self.movement_relative(4, DIR_M4_UP*0.1))
        self.ui.move_flasks_down_10.clicked.connect(lambda: self.movement_relative(4, DIR_M4_DOWN*10))
        self.ui.move_flasks_down_1.clicked.connect(lambda: self.movement_relative(4, DIR_M4_DOWN*1))
        self.ui.move_flasks_down_01.clicked.connect(lambda: self.movement_relative(4, DIR_M4_DOWN*0.1))

        self.ui.move_flasks_bottom.clicked.connect(lambda: self.movement_relative(4, DIR_M4_DOWN*200))           # JUST MOVE VERY FAR (1m) AND REACH THE END
        self.ui.move_flasks_top.clicked.connect(lambda: self.movement_relative(4, DIR_M4_UP*200))

        # TRAVEL TO POSITION
        self.ui.button_blood_setpos.clicked.connect(lambda: self.movement_absoluteposition(1))
        self.ui.button_cartridge_setpos.clicked.connect(lambda: self.movement_absoluteposition(2))
        self.ui.button_set_flasks_pos_ud.clicked.connect(lambda: self.movement_absoluteposition(4))
        self.ui.button_set_flasks_pos_lr.clicked.connect(lambda: self.movement_absoluteposition(3))
        # OLD IMPLEMENTATION
        #self.ui.button_blood_setpos.clicked.connect(lambda: self.movement_absoluteposition_blood)
        #self.ui.button_cartridge_setpos.clicked.connect(self.movement_absoluteposition_cartridge)
        #self.ui.button_set_flasks_pos_ud.clicked.connect(self.movement_absoluteposition_flasks_ud)
        #self.ui.button_set_flasks_pos_lr.clicked.connect(self.movement_absoluteposition_flasks_lr)

        # TRAVEL TO FLASK NUMBER
        self.ui.button_flaskpos_1.clicked.connect(lambda: self.movement_flasknumber(1))
        self.ui.button_flaskpos_2.clicked.connect(lambda: self.movement_flasknumber(2))
        self.ui.button_flaskpos_3.clicked.connect(lambda: self.movement_flasknumber(3))
        self.ui.button_flaskpos_4.clicked.connect(lambda: self.movement_flasknumber(4))

        #  _____                  _____     _   _               
        # |  _  |_ _ _____ ___   | __  |_ _| |_| |_ ___ ___ ___ 
        # |   __| | |     | . |  | __ -| | |  _|  _| . |   |_ -|
        # |__|  |___|_|_|_|  _|  |_____|___|_| |_| |___|_|_|___|
        #                 |_|                                   
        # TODO




        # ====================================================================================================
        #  _____ _____ _____ _____ _____ __       _____ _____ _____ _____ _____ _____ _____ _____ _____ _____ 
        # |   __|   __| __  |     |  _  |  |     |     |     |   | |   | |   __|     |_   _|     |     |   | |
        # |__   |   __|    -|-   -|     |  |__   |   --|  |  | | | | | | |   __|   --| | | |-   -|  |  | | | |
        # |_____|_____|__|__|_____|__|__|_____|  |_____|_____|_|___|_|___|_____|_____| |_| |_____|_____|_|___|
        # ====================================================================================================
        self.device_serials = serial_start_connections()    # START ALL SERIAL CONNECTIONS 

        self.ui.display_system_log.append("Connection to Devices established:")                     # LOGGING: ADD MESSAGE TO MONITOR
        # CHECK CONNECTION STATUS
        if self.device_serials[0].isOpen():
            self.ui.display_system_log.append("PSU OPEN @ PORT " + self.device_serials[0].name)     # LOGGING: ADD MESSAGE TO MONITOR
            self.flag_connections[0] = True                                                         # SET CONNECTION FLAG FOR PSU
        if self.device_serials[1].isOpen():
            self.ui.display_system_log.append("PG OPEN @ PORT " + self.device_serials[1].name)      # LOGGING: ADD MESSAGE TO MONITOR
            self.flag_connections[1] = True                                                         # SET CONNECTION FLAG FOR PG
        if self.device_serials[2].isOpen():
            self.ui.display_system_log.append("3PAC OPEN @ PORT " + self.device_serials[2].name)    # LOGGING: ADD MESSAGE TO MONITOR
            self.flag_connections[2] = True                                                         # SET CONNECTION FLAG FOR 3PAC
        if self.device_serials[3] is not None:
            self.ui.display_system_log.append("TEMP-SENS. OPENED")                                  # LOGGING: ADD MESSAGE TO MONITOR
            self.flag_connections[3] = True                                                         # SET CONNECTION FLAG FOR TEMPERATURE SENSOR

        # ITERATE THROUGH ALL DEVICES AND PRINT ALL CONNECTION INFO (INFO: NOT NEEDED, JUST DEBUGGING INFO)
        print("CONNECTION FLAGS:")
        for device in range(4):
            print(self.flag_connections[device])

        # HANDSHAKES WITH DEVICES
        if self.flag_connections[2]:
            handshake_3PAC(self.device_serials[2], print_handshake_message=True)

        # CHANGE STYLE SHEETS FOR CONNECTION INDICATORS
        self.set_connection_indicators(self.flag_connections)


        # ===========================================================================================================================================
        #  _____ _____ _____ _____ _____ _____ __    _____ _____ _____    ____  _____ _____ _____ _____ _____    _____ _____ _____ _____ _____ _____ 
        # |     |   | |     |_   _|     |  _  |  |  |     |__   |   __|  |    \|   __|  |  |     |     |   __|  |   __|_   _|  _  |_   _|   __|   __|
        # |-   -| | | |-   -| | | |-   -|     |  |__|-   -|   __|   __|  |  |  |   __|  |  |-   -|   --|   __|  |__   | | | |     | | | |   __|__   |
        # |_____|_|___|_____| |_| |_____|__|__|_____|_____|_____|_____|  |____/|_____|\___/|_____|_____|_____|  |_____| |_| |__|__| |_| |_____|_____|
        # ===========================================================================================================================================

        # INITIALIZE SCALING VALUES FOR PLOTS
        self.zerodata = [2000, 2000]
        self.maxval_pulse = 10  
        self.minval_pulse = -10

        self.start_plotting()

        # INIT 3PAC
        if self.flag_connections[2]:
            # INITIALIZE VALVE STATES (ALL CLOSED) TODO: NEEDS TO BE CHANGED SOON. MAYBE ADD A GLOBAL VARIABLE AT THE BEGINNING FOR INITIAL STATES
            # Construct the message
            msg = f'wVS-111\n'
            # Write the message
            self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
            msg = self.device_serials[2].readline()
            print("RESPONSE: " + msg.decode())
            time.sleep(2)

            # INITIALIZE PID STATES (ALL CLOSED)
            #print("MESSAGE: PID On")
            #msg = "wPS-22"
            #self.device_serials[2].write(msg.encode())
            #msg = self.device_serials[2].readline()
            #print("RESPONSE: " + msg.decode())
            #time.sleep(2)
            #self.start_flowrate_suceth_update()

        

        
        
    # =========================================================================
    # ███████ ██    ██ ███    ██  ██████ ████████ ██  ██████  ███    ██ ███████
    # ██      ██    ██ ████   ██ ██         ██    ██ ██    ██ ████   ██ ██     
    # █████   ██    ██ ██ ██  ██ ██         ██    ██ ██    ██ ██ ██  ██ ███████
    # ██      ██    ██ ██  ██ ██ ██         ██    ██ ██    ██ ██  ██ ██      ██
    # ██       ██████  ██   ████  ██████    ██    ██  ██████  ██   ████ ███████
    # =========================================================================

    # =============================================================================================================
    #  _____ __    _____ _ _ _    _____ _____ _____ _____    _____ _____ _____ _____ _____ _____ _____ _____ _____ 
    # |   __|  |  |     | | | |  | __  |  _  |_   _|   __|  |   __|  |  |   | |     |_   _|     |     |   | |   __|
    # |   __|  |__|  |  | | | |  |    -|     | | | |   __|  |   __|  |  | | | |   --| | | |-   -|  |  | | | |__   |
    # |__|  |_____|_____|_____|  |__|__|__|__| |_| |_____|  |__|  |_____|_|___|_____| |_| |_____|_____|_|___|_____|
    # =============================================================================================================
    
    # TIMER CALL: UPDATE THE FLOW RATE FOR SUCROSE OR ETHANOL
    def update_flowrate_suceth(self):

        flow_value_float = read_flowrate(self.device_serials[2])
        print("Flowrate: {}".format(flow_value_float))

        # UPDATE LABEL
        if self.flag_suc_on or self.flag_eth_on:
            self.ui.value_flowrate_suc_eth.setText(str(flow_value_float))

        # PROGRESS BAR VALUE
        # needs to be inverted: 1.0 is empty, 0.0 is full
        if flow_value_float is None or flow_value_float<0:
            flow_value_float = 0.0
        
        if flow_value_float > SUCROSE_FLOWRATE_MAX:
            flow_value_float = SUCROSE_FLOWRATE_MAX

        progress_value = 1 - (flow_value_float / SUCROSE_FLOWRATE_MAX)  # SCALING AND INVERTING
        stop_1 = str(progress_value - 0.001)
        stop_2 = str(progress_value)

        style_sheet = """
        QFrame{
            border-radius: 60px;
            background-color: qconicalgradient(cx:0.5, cy:0.5, angle:230, stop:{STOP_1} rgba(7, 150, 255, 0), stop:{STOP_2} rgba(7, 150, 255, 255));
            }""".replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)
            
        self.ui.circularProgress_suc_eth.setStyleSheet(style_sheet)

        # TODO: CHANGE THE ACTUAL MESSAGE TO THE 3PAC, IF SUCROSE OR ETHANOL IS ALREADY ON
        
    # UPDATE THE FLOW RATE VALUE FOR BLOOD
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
            border-radius: 60px;
            background-color: qconicalgradient(cx:0.5, cy:0.5, angle:230, stop:{STOP_1} rgba(138, 201, 38, 0), stop:{STOP_2} rgba(138, 201, 38, 255));
            }""".replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)
            
        self.ui.circularProgress_blood.setStyleSheet(style_sheet)

        # TODO: CHANGE THE ACTUAL MESSAGE TO THE 3PAC, IF BLOOD IS ALREADY ON

    # BUTTON CALLBACK: FUNCTION FOR THE TOGGLE-BUTTON FOR SUCROSE
    def toggle_flow_suc(self):
        if DEBUG: self.ui.display_system_log.append("BUTTON: TOGGLE FLOW SUCROSE")

        # IF ETHANOL IS ON
        if self.flag_eth_on:
            self.ui.display_system_log.append("SWITCH OFF ETH BEFORE")
            self.ui.button_toggle_sucflow.setChecked(False)

        else:
            # ALREADY ON --> SWITCH IT OFF
            if self.flag_suc_on:
                # Construct the message for PUMPS OFF
                msg = f'wPS-00'
                # Write the message
                self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
                msg = self.device_serials[2].readline()
                print("RESPONSE: " + msg.decode())

                self.flag_suc_on = False
                self.ui.value_flowrate_suc_eth.setText("OFF")

            # OFF --> SWITCH IT ON
            else:
                self.ui.display_system_log.append("SWITCHED ON SUC")
                input_value_float, input_value_string = self.input_check_suceth()

                # Construct the message for PUMP1 IN PID MODE
                msg = f'wPS-20'
                # Write the message
                self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
                msg = self.device_serials[2].readline()
                print("RESPONSE: " + msg.decode())

                time.sleep(1)

                writePumpFlowRate(self.device_serials[2], input_value_float, input_value_float)

                self.flag_suc_on = True

    # BUTTON CALLBACK: FUNCTION FOR THE TOGGLE-BUTTON FOR ETHANOL
    def toggle_flow_eth(self):
        if DEBUG: self.ui.display_system_log.append("BUTTON: TOGGLE FLOW ETHANOL")

        # IF SUCROSE IS ON
        if self.flag_suc_on:
            self.ui.display_system_log.append("SWITCH OFF SUC BEFORE")
            self.ui.button_toggle_ethflow.setChecked(False)

        else:
            # ALREADY ON --> SWITCH IT OFF
            if self.flag_eth_on:
                # Construct the message for PUMPS OFF
                msg = f'wPS-00'
                # Write the message
                self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
                msg = self.device_serials[2].readline()
                print("RESPONSE: " + msg.decode())

                self.flag_eth_on = False
                self.ui.value_flowrate_suc_eth.setText("OFF")

            # OFF --> SWITCH IT ON
            else:
                self.ui.display_system_log.append("SWITCHED ON ETH")
                input_value_float, input_value_string = self.input_check_suceth()

                # Construct the message for PUMP2 IN PID MODE
                msg = f'wPS-02'
                # Write the message
                self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
                msg = self.device_serials[2].readline()
                print("RESPONSE: " + msg.decode())

                time.sleep(1)

                writePumpFlowRate(self.device_serials[2], input_value_float, input_value_float)

                self.flag_eth_on = True

    # BUTTON CALLBACK: FUNCTION FOR THE TOGGLE-BUTTON FOR BLOOD
    def toggle_flow_blood(self):
        if DEBUG: self.ui.display_system_log.append("BUTTON: TOGGLE FLOW BLOOD")

        if self.flag_blood_on:
            writeBloodSyringe(self.device_serials[2], 0.00, 0.00)
            self.ui.value_flowrate_blood.setText("OFF")
            self.ui.display_system_log.append("Blood: OFF")
            self.flag_blood_on = False

        else:
            input_value_float, input_value_string = self.input_check_blood()
            writeBloodSyringe(self.device_serials[2], 9.99, input_value_float)
            self.ui.value_flowrate_blood.setText(input_value_string)
            self.ui.display_system_log.append("Blood: ON")
            self.flag_blood_on = True
        
    # HELPER FUNCTION: CHECK THE INPUT VALUE FOR SUCROSE OR ETHANOL (ERROR HANDLING)
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

    # HELPER FUNCTION: CHECK THE INPUT VALUE FOR BLOOD (ERROR HANDLING)
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


    # ====================================================================================================================================================
    #  _____ __    _____ _____ _____ _____ _____ _____    _| |_    _____ _____ _____ _____ _____    _____ _____ _____ _____ _____ _____ _____ _____ _____ 
    # |  _  |  |  |     |_   _|_   _|     |   | |   __|  |   __|  |   __| __  |  _  |  _  |  |  |  |   __|  |  |   | |     |_   _|     |     |   | |   __|
    # |   __|  |__|  |  | | |   | | |-   -| | | |  |  |  |   __|  |  |  |    -|     |   __|     |  |   __|  |  | | | |   --| | | |-   -|  |  | | | |__   |
    # |__|  |_____|_____| |_|   |_| |_____|_|___|_____|  |_   _|  |_____|__|__|__|__|__|  |__|__|  |__|  |_____|_|___|_____| |_| |_____|_____|_|___|_____|
    # ====================================================================================================================================================

    # START TIMER FOR FLOWRATE-UPDATE
    def start_flowrate_suceth_update(self):
        # TIMER
        self.flow_timer = QTimer()
        self.flow_timer.setInterval(self.interval)
        self.flow_timer.timeout.connect(self.update_flowrate_suceth)
        self.flow_timer.start()

    # START PLOTTING --> PREPARE & START TIMER
    def start_plotting(self):
        #dynamic x axis 
        self.temp_x = np.linspace(0, 499, 500)  # This creates an array from 0 to 499 with 500 elements.
        self.tempmax = np.zeros(500)
        self.tempmax.fill(37)
        self.voltage_x = np.linspace(0, 499, 500)

        # Plotting variables
        self.interval = 2000  # ms
        self.tempplotdata = np.zeros(500)   # initialize Temperature values with 0
        self.temp_y = self.tempplotdata
        self.voltageplotdata = np.zeros(500)   # initialize Temperature values with 0

        # TIMER
        self.plot_timer = QTimer()
        self.plot_timer.setInterval(self.interval)
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start()

    # TIMER CALLBACK: UPDATE THE PLOT
    def update_plot(self):
        # READ TEMPERATURE
        if self.flag_connections[3]:
            temperature = read_temperature(self.device_serials[3])
        else:
            temperature = 0

        # UPDATE TEMP PLOT
        if temperature is not None:
            self.tempplotdata = np.roll(self.tempplotdata, -1)
            self.tempplotdata[-1:] = temperature
            self.temp_y = self.tempplotdata
            
            self.temp_x = np.roll(self.temp_x, -1)
            self.temp_x[-1] = self.temp_x[-2] + 1  # This will keep increasing the count on the x-axis

        # READ PULSE
        if self.flag_connections[1]:
            self.voltage_y, _ = read_next_PG_pulse(self.device_serials[1])  # READ NEXT PULSE
        else:
            self.voltage_y = np.zeros((1500,2))

        # PROCESS PULSE
        # CUT THE LAST PART
        new_length = round(self.voltage_y.shape[0]/2)
        self.voltage_y = self.voltage_y[:new_length]
        # REMOVE OFFSET
        self.voltage_y[:, 0] -= self.zerodata[0]    # ZERO THE VOLTAGE DATA
        self.voltage_y[:, 1] -= self.zerodata[1]    # ZERO THE CURRENT DATA
        # SCALING
        self.voltage_y[:, 0] *= 0.15                # SCALE THE VOLTAGE DATA
        self.voltage_y[:, 1] *= 0.15                # SCALE THE CURRENT DATA


        # CALCULATE SOME VARIABLES TO DISPLAY
        maxval_pulse_new = self.voltage_y.max(axis=0)[0]    # GET MAX VALUE FROM VOLTAGE PULSE
        minval_pulse_new = self.voltage_y.min(axis=0)[0]    # GET MIN VALUE FROM VOLTAGE PULSE

        if maxval_pulse_new > self.maxval_pulse:        # CHECK MAX VALUE OVER TIME
            self.maxval_pulse = maxval_pulse_new
            
        if minval_pulse_new < self.minval_pulse:        # CHECK MIN VALUE OVER TIME
            self.minval_pulse = minval_pulse_new
        
        self.ui.value_voltage_max.setText("{:.2f}".format(maxval_pulse_new))    # SET GUI TEXT
        self.ui.value_voltage_min.setText("{:.2f}".format(minval_pulse_new))    # SET GUI TEXT


        
        self.voltage_x = np.linspace(0, self.voltage_y.shape[0]-1, self.voltage_y.shape[0])
    
        # UPDATE PLOT
        # CLEAR PLOTS
        self.ui.MplWidget.canvas.axes1.clear()
        self.ui.MplWidget.canvas.axes2.clear()
        self.ui.MplWidget.canvas.axes3.clear()

        #self.ui.MplWidget.canvas.axes1.set_title("Voltage")
        self.ui.MplWidget.canvas.axes1.set_ylabel("Voltage [V]")
        #self.ui.MplWidget.canvas.axes1.set_ylim(self.minval_pulse-10, self.maxval_pulse+10)
        #self.ui.MplWidget.canvas.axes1.set_ylim(self.minval_pulse-10, self.maxval_pulse+10)

        #self.ui.MplWidget.canvas.axes2.set_title("Current")
        self.ui.MplWidget.canvas.axes2.set_ylabel("Current [A]")
        #self.ui.MplWidget.canvas.axes3.set_title("Temperature")
        self.ui.MplWidget.canvas.axes3.set_ylabel("Temperature [°C]")

        self.ui.MplWidget.canvas.axes1.plot(self.voltage_x, self.voltage_y[:, 0])
        self.ui.MplWidget.canvas.axes2.plot(self.voltage_x, self.voltage_y[:, -1])
        self.ui.MplWidget.canvas.axes3.plot(self.temp_x, self.temp_y)
        self.ui.MplWidget.canvas.axes3.plot(self.temp_x, self.tempmax)
        self.ui.MplWidget.canvas.draw()

    # START TIMER: READ ALL MESSAGES
    def start_reading_messages(self):
        # TIMER
        self.flow_timer = QTimer()
        self.flow_timer.setInterval(self.interval)
        self.flow_timer.timeout.connect(self.update_flowrate_suceth)
        self.flow_timer.start()

    # STOP TIMER: READ ALL MESSAGES
    def stop_reading_messages(self):
        pass

    # TIMER CALLBACK: READ ALL MESSAGES
    #def read_messages(self):
        # R

    # =====================================================================================================================================
    #  ____  _____ _____ _____ _____ _____    _____ _____ _____ _____ __    _____    _____ _____ _____ _____ _____ _____ _____ _____ _____ 
    # |    \|   __|  |  |     |     |   __|  |_   _|     |   __|   __|  |  |   __|  |   __|  |  |   | |     |_   _|     |     |   | |   __|
    # |  |  |   __|  |  |-   -|   --|   __|    | | |  |  |  |  |  |  |  |__|   __|  |   __|  |  | | | |   --| | | |-   -|  |  | | | |__   |
    # |____/|_____|\___/|_____|_____|_____|    |_| |_____|_____|_____|_____|_____|  |__|  |_____|_|___|_____| |_| |_____|_____|_|___|_____|
    # =====================================================================================================================================

    # BUTTON CALLBACK: PSU TOGGLE (ENABLE / DISABLE)
    def psu_button_toggle(self):
        if DEBUG: self.ui.display_system_log.append("BUTTON: TOGGLE PSU")

        if self.flag_connections[0]:
            # PSU IS SWITCHING OFF
            if self.flag_psu_on:
                sucess = send_PSU_disable(self.device_serials[0], 1)

                # CHECK IF DATA WAS SENT SUCESSFULLY
                if sucess:                                          # SENDING SUCESSFUL
                    self.ui.display_system_log.append("PSU: OFF")   # LOG TO GUI
                    self.flag_psu_on = False                        # SET FLAG FOR PSU STATE
                else:                                                                       # SENDING NOT POSSIBLE (5 tries)
                    self.ui.display_system_log.append("ERROR: Could not switch PSU OFF")    # LOG TO GUI
                    self.ui.button_toggle_psu_enable.setChecked(True)                       # SET THE BUTTON TO "ON" AGAIN

            # PSU IS SWITCHING ON
            else:
                sucess = send_PSU_enable(self.device_serials[0], 1)

                # CHECK IF DATA WAS SENT SUCESSFULLY
                if sucess:                                          # SENDING SUCESSFUL
                    self.ui.display_system_log.append("PSU: ON")    # LOG TO GUI
                    self.flag_psu_on = True                         # SET FLAG FOR PSU STATE
                else:                                                                       # SENDING NOT POSSIBLE (5 tries)
                    self.ui.display_system_log.append("ERROR: Could not switch PSU ON")     # LOG TO GUI
                    self.ui.button_toggle_psu_enable.setChecked(False)                      # SET THE BUTTON TO "OFF" AGAIN

        else:
            self.ui.display_system_log.append("PSU IS NOT CONNECTED! COULD NOT SWITCH IT ON")     # LOG TO GUI
            self.ui.button_toggle_psu_enable.setChecked(False)                      # SET THE BUTTON TO "OFF" AGAIN

    # BUTTON CALLBACK: PG TOGGLE (ENABLE / DISABLE)
    def pg_button_toggle(self):
        if DEBUG: self.ui.display_system_log.append("BUTTON: TOGGLE PG")

        if self.flag_connections[1]:
            if self.flag_pg_on:
                success = send_PG_disable(self.device_serials[1], 1)

                # CHECK IF DATA WAS SENT SUCESSFULLY
                if success:                                          # SENDING SUCESSFUL
                    self.ui.display_system_log.append("PG: OFF")    # LOG TO GUI
                    self.flag_pg_on = False                        # SET FLAG FOR PG STATE
                else:                                                                       # SENDING NOT POSSIBLE (5 tries)
                    self.ui.display_system_log.append("ERROR: Could not switch PG OFF")     # LOG TO GUI
                    self.ui.button_toggle_pg_enable.setChecked(True)                       # SET THE BUTTON TO "ON" AGAIN
            else:
                success = self.set_pulse_shape()
                if success:
                    self.ui.display_system_log.append("SET PULSE SHAPE SUCCESS")     # LOG TO GUI
                else:
                    self.ui.display_system_log.append("ERROR: COULD NOT SET PULSE SHAPE")     # LOG TO GUI
                
                self.zerodata = send_PG_enable(self.device_serials[1], 1)
                

                # CHECK IF DATA WAS SENT SUCESSFULLY
                if self.zerodata:                                          # SENDING SUCESSFUL
                    print("ZERO VOLTAGE: {}".format(self.zerodata[0]))      # JUST PRINT STUFF
                    print("ZERO CURRENT: {}".format(self.zerodata[1]))

                    self.maxval_pulse = 0   # RESET PLOT SCALE
                    self.minval_pulse = 0

                    self.ui.display_system_log.append("PG: ON")     # LOG TO GUI
                    self.flag_pg_on = True                          # SET FLAG FOR PG STATE
                else:                                                                       # SENDING NOT POSSIBLE (5 tries)
                    self.ui.display_system_log.append("ERROR: Could not switch PG ON")      # LOG TO GUI
                    self.ui.button_toggle_pg_enable.setChecked(False)                       # SET THE BUTTON TO "ON" AGAIN

        else:
            self.ui.display_system_log.append("PG IS NOT CONNECTED! COULD NOT SWITCH IT ON")     # LOG TO GUI
            self.ui.button_toggle_pg_enable.setChecked(False)                       # SET THE BUTTON TO "ON" AGAIN

    # HELPER FUNCTION: GET & CHECK ALL VALUES FROM GUI FOR PULSE SHAPE AND SEND "send_PG_pulsetimes" COMMAND TO PG
    def set_pulse_shape(self):
        # READ ALL VALUES FROM THE GUI
        repetition_rate_freq = self.ui.input_repetition_rate.text()
        pulse_length = self.ui.value_pulse_length.text()
        on_time = self.ui.value_on_time.text()

        # TEST THE VALUES FOR INPUT ERRORS: REPETITION RATE
        if repetition_rate_freq == "":                      # IF EMPTY
            repetition_rate_freq_int = 200                  # SET TO STANDARD VALUE
            self.ui.input_repetition_rate.setText("200")    # SET TO STANDARD VALUE
        else:
            try:
                repetition_rate_freq_int = int(repetition_rate_freq)        # READ INPUT VALUE & CONVERT

                if repetition_rate_freq_int < REPETITION_FREQUENCY_MIN :    # IF SMALLER THAN MIN VALUE
                    input_value_int_pos = REPETITION_FREQUENCY_MIN          # MAKE IT EQUAL TO MIN VALUE
                        
                if input_value_int_pos > REPETITION_FREQUENCY_MAX:          # IF GREATER THAN MAX VALUE
                    input_value_int_pos = REPETITION_FREQUENCY_MAX          # MAKE IT EQUAL TO MAX VALUE
                        
            except:                                         # NOT A VALID NUMBER (no integer conversion possible)
                repetition_rate_freq_int = 200
                self.ui.input_repetition_rate.setText("200")
                self.ui.display_system_log.append("NUMBER FORMAT ERROR. SET REP.RATE TO STANDARD")

        # TEST THE VALUES FOR INPUT ERRORS: PULSE LENGTH
        if pulse_length == "":                          # IF EMPTY
            pulse_length_int = 75                       # SET TO STANDARD VALUE
            self.ui.value_pulse_length.setText("75")    # SET TO STANDARD VALUE
        else:
            try:
                pulse_length_int = int(pulse_length)        # READ INPUT VALUE & CONVERT

                if pulse_length_int < PULSE_LENGTH_MIN :    # IF SMALLER THAN MIN VALUE
                    pulse_length_int = PULSE_LENGTH_MIN     # MAKE IT EQUAL TO MIN VALUE
                        
                if pulse_length_int > PULSE_LENGTH_MAX:     # IF GREATER THAN MAX VALUE
                    pulse_length_int = PULSE_LENGTH_MAX     # MAKE IT EQUAL TO MAX VALUE
                        
            except:                                         # NOT A VALID NUMBER (no integer conversion possible)
                pulse_length_int = 75
                self.ui.value_pulse_length.setText("75")
                self.ui.display_system_log.append("NUMBER FORMAT ERROR. SET PULSE LENGTH TO STANDARD")

        # TEST THE VALUES FOR INPUT ERRORS: ON-TIME
        if on_time == "":                          # IF EMPTY
            on_time_int = 248                       # SET TO STANDARD VALUE
            self.ui.value_on_time.setText("248")    # SET TO STANDARD VALUE
        else:
            try:
                on_time_int = int(on_time)        # READ INPUT VALUE & CONVERT

                if on_time_int < ON_TIME_MIN :    # IF SMALLER THAN MIN VALUE
                    on_time_int = ON_TIME_MIN     # MAKE IT EQUAL TO MIN VALUE
                        
                if on_time_int > ON_TIME_MAX:     # IF GREATER THAN MAX VALUE
                    on_time_int = ON_TIME_MAX     # MAKE IT EQUAL TO MAX VALUE
                        
            except:                                         # NOT A VALID NUMBER (no integer conversion possible)
                pulse_length_int = 248
                self.ui.value_on_time.setText("248")
                self.ui.display_system_log.append("NUMBER FORMAT ERROR. SET ON-TIME TO STANDARD")
            

        # SEND VALUES TO PG
        send_PG_pulsetimes(self.device_serials[1], 0, repetition_rate_freq_int, pulse_length_int, on_time_int, verbose=1)


    # =================================================================================================================================================
    #  _____ _____ _____      _    _____ _____    _____ _____ _____ _____ _____ _____ _____    _____ _____ _____ _____ _____ _____ _____ _____ _____ 
    # |  _  |   __|  |  |    / |  |  _  |   __|  |     |   __|   __|   __|  _  |   __|   __|  |   __|  |  |   | |     |_   _|     |     |   | |   __|
    # |   __|__   |  |  |   / /   |   __|  |  |  | | | |   __|__   |__   |     |  |  |   __|  |   __|  |  | | | |   --| | | |-   -|  |  | | | |__   |
    # |__|  |_____|_____|  |_/    |__|  |_____|  |_|_|_|_____|_____|_____|__|__|_____|_____|  |__|  |_____|_|___|_____| |_| |_____|_____|_|___|_____|
    # =================================================================================================================================================

    # BUTTON CALLBACK: PSU SET VOLTAGES (READ VALUES FROM GUI)
    def psu_set_voltage(self):
        if DEBUG: self.ui.display_system_log.append("BUTTON: SET VOLTAGE")

        if self.flag_connections[0]:
            # VOLTAGES ARE LINKED
            if self.ui.checkbox_link_voltages.isChecked():
                input_value_pos = self.ui.input_voltage_positive.text()

                if input_value_pos == "":   # IF EMPTY
                    input_value_int_pos = 0     # SET TO ZERO
                else:
                    try:
                        input_value_int_pos = int(input_value_pos)          # READ INPUT VALUE

                        if input_value_int_pos < 0 :                        # IF NEGATIVE
                            input_value_int_pos = abs(input_value_int_pos)  # MAKE POSITIVE
                        
                        if input_value_int_pos > VOLTAGE_PSU_MAX:           # IF GREATER THAN MAX VALUE
                            input_value_int_pos = VOLTAGE_PSU_MAX           # MAKE IT EQUAL TO MAX VALUE
                        
                    except:                                         # NOT A VALID NUMBER (no integer conversion possible)
                        self.ui.input_voltage_positive.setText("")
                        self.ui.display_system_log.append("NUMBER FORMAT ERROR")
                        return -1, "ERR"
                    
                voltage_setpoint_pos = input_value_int_pos
                voltage_setpoint_neg = voltage_setpoint_pos

            # VOLTAGES ARE NOT LINKED
            else:
                input_value_pos = self.ui.input_voltage_positive.text()
                input_value_neg = self.ui.input_voltage_negative.text()

                # TEST POSITIVE VALUE
                if input_value_pos == "":   # IF EMPTY
                    input_value_int_pos = 0     # SET TO ZERO
                else:
                    try:
                        input_value_int_pos = int(input_value_pos)          # READ INPUT VALUE

                        if input_value_int_pos < 0 :                        # IF NEGATIVE
                            input_value_int_pos = abs(input_value_int_pos)  # MAKE POSITIVE
                        
                        if input_value_int_pos > VOLTAGE_PSU_MAX:           # IF GREATER THAN MAX VALUE
                            input_value_int = VOLTAGE_PSU_MAX               # MAKE IT EQUAL TO MAX VALUE
                        
                    except:                                                 # NOT A VALID NUMBER (no integer conversion possible)
                        self.ui.input_voltage_positive.setText("")
                        self.ui.display_system_log.append("NUMBER FORMAT ERROR")
                        return -1, "ERR"
                    
                # TEST NEGATIVE VALUE
                if input_value_neg == "":   # IF EMPTY
                    input_value_int_neg = 0     # SET TO ZERO
                else:
                    try:
                        input_value_int_neg = int(input_value_neg)      # READ INPUT VALUE

                        if input_value_int_neg < 0 :                    # IF NEGATIVE
                            input_value_int_neg = abs(input_value_int_neg)  # MAKE POSITIVE
                        
                        if input_value_int_neg > VOLTAGE_PSU_MAX:       # IF GREATER THAN MAX VALUE
                            input_value_int_neg = VOLTAGE_PSU_MAX       # MAKE IT EQUAL TO MAX VALUE
                        
                    except:                                         # NOT A VALID NUMBER (no integer conversion possible)
                        self.ui.input_voltage_positive.setText("")
                        self.ui.display_system_log.append("NUMBER FORMAT ERROR")
                        return -1, "ERR"
                    
                voltage_setpoint_pos = input_value_int_pos
                voltage_setpoint_neg = input_value_int_neg

            # SET SETPOINTS VIA MESSAGE
            success = send_PSU_setpoints(self.device_serials[0], voltage_setpoint_pos, voltage_setpoint_neg, verbose=1)
            self.ui.display_system_log.append("SET VOLTAGE SUCCESS: {}".format(success))    # LOG TO GUI

        else:
            self.ui.display_system_log.append("PSU IS NOT CONNECTED! COULD NOT CHANGE VOLTAGES")     # LOG TO GUI
            self.ui.button_toggle_psu_enable.setChecked(False)                      # SET THE BUTTON TO "OFF" AGAIN

    # BUTTON CALLBACK: START LOGGING PULSES TO CSV
    def pg_logging_toggle(self):
        if DEBUG: self.ui.display_system_log.append("BUTTON: TOGGLE LOGGING")
        pass
        # CHECK IF LOGGING FLAG IS ON
        # START LOGGING OR STOP LOGGING (DEPENDING ON FLAG):
        # GATHER DATA TO PANDAS DF
        # SAVE TO CSV FILE(S)

    # BUTTON CALLBACK: START APPLYING PRESSURE UNTIL VALUE IS REACHED
    def apply_pressure(self):
        if DEBUG: self.ui.display_system_log.append("BUTTON: SET PRESSURE")
        pass

        if self.flag_connections[2]:
            # CLOSE VALVES (& UPDATE GUI BUTTON STATES)
            msg = f'wVS-110'    # TODO: CHECK VALVE STATES
            # Write the message
            self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
            msg = self.device_serials[2].readline()
            print("RESPONSE: " + msg.decode())

            # START MEASUREMENT

        # READ PRESSURE VALUE & TEST FOR ERRORS
        # READ CURRENT PRESSURE VALUE (3PAC)
        # CHECK FOR VALUE DIFFERENCE (OR GOAL ALREADY MET)
        # CLOSE VALVES (& UPDATE GUI BUTTON STATES)
        # START PUMP
        # START TIMER TO READ PRESSURE: check_applied_pressure()

    # HELPER FUNCTION: CHECK IF WANTED PRESSURE IS REACHED AND STOP PUMPS, IF THRESHHOLD IS REACHED
    def check_applied_pressure(self):
        pass
        # READ PRESSURE FROM SENSOR (3PAC)
        # CHECK IF THRESHHOLD IS REACHED
        # IF YES --> SWITCH OFF PUMP


    # =====================================================================================================================================
    #  _____ _____ __    _____ _____    _____ _____ _____ _____ _____ _____ __       _____ _____ _____ _____ _____ _____ _____ _____ _____ 
    # |  |  |  _  |  |  |  |  |   __|  |     |     |   | |_   _| __  |     |  |     |   __|  |  |   | |     |_   _|     |     |   | |   __|
    # |  |  |     |  |__|  |  |   __|  |   --|  |  | | | | | | |    -|  |  |  |__   |   __|  |  | | | |   --| | | |-   -|  |  | | | |__   |
    #  \___/|__|__|_____|\___/|_____|  |_____|_____|_|___| |_| |__|__|_____|_____|  |__|  |_____|_|___|_____| |_| |_____|_____|_|___|_____|
    # =====================================================================================================================================

    # TODO: MAKE A SINGLE FUNCTION OUT OF THE NEXT FOUR FUNCTIONS
    def change_valve_state_path(self, state):       # STATE 0..OFF; 1..SUCROSE; 2..ETHANOL; 3..CLEANING
        if self.flag_connections[2]:    # IF 3PAC CONNECTED
            if state == 0:  # OFF
                self.ui.display_system_log.append("VALVES: OFF")
                msg = f'wVS-111'
                # Write the message
                self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
                msg = self.device_serials[2].readline()
                print("RESPONSE: " + msg.decode())

                # EXACTLY INVERTED BUTTONS, SINCE VALVES ARE NORMALLY OPEN
                self.ui.button_toggle_valve1.setChecked(False)
                self.ui.button_toggle_valve2.setChecked(False)
                self.ui.button_toggle_valve3.setChecked(False)
            elif state == 1:    # SUCROSE
                self.ui.display_system_log.append("VALVES: SUCROSE")
                msg = f'wVS-010'
                # Write the message
                self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
                msg = self.device_serials[2].readline()
                print("RESPONSE: " + msg.decode())

                # EXACTLY INVERTED BUTTONS, SINCE VALVES ARE NORMALLY OPEN
                self.ui.button_toggle_valve1.setChecked(True)
                self.ui.button_toggle_valve2.setChecked(False)
                self.ui.button_toggle_valve3.setChecked(True)
            elif state == 2:    # ETHANOL
                self.ui.display_system_log.append("VALVES: ETHANOL")
                msg = f'wVS-001'
                # Write the message
                self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
                msg = self.device_serials[2].readline()
                print("RESPONSE: " + msg.decode())

                # EXACTLY INVERTED BUTTONS, SINCE VALVES ARE NORMALLY OPEN
                self.ui.button_toggle_valve1.setChecked(True)
                self.ui.button_toggle_valve2.setChecked(True)
                self.ui.button_toggle_valve3.setChecked(False)
            elif state == 3:    # CLEANING
                self.ui.display_system_log.append("VALVES: CLEANING")
                msg = f'wVS-100'
                # Write the message
                self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
                msg = self.device_serials[2].readline()
                print("RESPONSE: " + msg.decode())

                # EXACTLY INVERTED BUTTONS, SINCE VALVES ARE NORMALLY OPEN
                self.ui.button_toggle_valve1.setChecked(False)
                self.ui.button_toggle_valve2.setChecked(True)
                self.ui.button_toggle_valve3.setChecked(True)
            else:
                self.ui.display_system_log.append("VALVES: UNKNOWN STATE {}".format(state))
        else:
            self.ui.display_system_log.append("COULD NOT CHANGE VALVE STATE. 3PAC IS NOT CONNECTED")
            self.ui.button_valvestate_off.setChecked(True)

    # BUTTON CALLBACK: CHANGE VALVE STATE TO "SUCROSE"    (UNUSED)
    def change_valve_state_sucrose(self):
        if self.flag_connections[2]:
            self.ui.display_system_log.append("VALVES: SUCROSE")
            msg = f'wVS-010'
            # Write the message
            self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
            msg = self.device_serials[2].readline()
            print("RESPONSE: " + msg.decode())

            # EXACTLY INVERTED BUTTONS, SINCE VALVES ARE NORMALLY OPEN
            self.ui.button_toggle_valve1.setChecked(True)
            self.ui.button_toggle_valve2.setChecked(False)
            self.ui.button_toggle_valve3.setChecked(True)

        else:
            self.ui.display_system_log.append("COULD NOT CHANGE VALVE STATE. 3PAC IS NOT CONNECTED")
            self.ui.button_valvestate_off.setChecked(True)

    # BUTTON CALLBACK: CHANGE VALVE STATE TO "ETHANOL"    (UNUSED)
    def change_valve_state_ethanol(self):
        if self.flag_connections[2]:
            self.ui.display_system_log.append("VALVES: ETHANOL")
            msg = f'wVS-001'
            # Write the message
            self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
            msg = self.device_serials[2].readline()
            print("RESPONSE: " + msg.decode())

            # EXACTLY INVERTED BUTTONS, SINCE VALVES ARE NORMALLY OPEN
            self.ui.button_toggle_valve1.setChecked(True)
            self.ui.button_toggle_valve2.setChecked(True)
            self.ui.button_toggle_valve3.setChecked(False)

        else:
            self.ui.display_system_log.append("COULD NOT CHANGE VALVE STATE. 3PAC IS NOT CONNECTED")
            self.ui.button_valvestate_off.setChecked(True)

    # BUTTON CALLBACK: CHANGE VALVE STATE TO "CLEANING"    (UNUSED)
    def change_valve_state_cleaning(self):
        if self.flag_connections[2]:
            self.ui.display_system_log.append("VALVES: CLEANING")
            msg = f'wVS-100'
            # Write the message
            self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
            msg = self.device_serials[2].readline()
            print("RESPONSE: " + msg.decode())

            # EXACTLY INVERTED BUTTONS, SINCE VALVES ARE NORMALLY OPEN
            self.ui.button_toggle_valve1.setChecked(False)
            self.ui.button_toggle_valve2.setChecked(True)
            self.ui.button_toggle_valve3.setChecked(True)

        else:
            self.ui.display_system_log.append("COULD NOT CHANGE VALVE STATE. 3PAC IS NOT CONNECTED")
            self.ui.button_valvestate_off.setChecked(True)

    # BUTTON CALLBACK: CHANGE VALVE STATE TO "OFF"    (UNUSED)
    def change_valve_state_off(self):
        if self.flag_connections[2]:
            self.ui.display_system_log.append("VALVES: OFF")
            msg = f'wVS-111'
            # Write the message
            self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
            msg = self.device_serials[2].readline()
            print("RESPONSE: " + msg.decode())

            # EXACTLY INVERTED BUTTONS, SINCE VALVES ARE NORMALLY OPEN
            self.ui.button_toggle_valve1.setChecked(False)
            self.ui.button_toggle_valve2.setChecked(False)
            self.ui.button_toggle_valve3.setChecked(False)

        else:
            self.ui.display_system_log.append("COULD NOT CHANGE VALVE STATE. 3PAC IS NOT CONNECTED")

    # BUTTON CALLBACK: CHANGE A SINGLE VALVE (ON / OFF) TODO: ADD "LAMBDA" WHEN CONNECTING, INSTEAD OF CHECKING ALL VALVES
    def change_single_valve(self):

        if self.flag_connections[2]:

            # CHECK VALVE BUTTON STATES TO CRAFT MESSAGE FOR BUTTONS
            valvebutton_states = np.array([False, False, False])
            valvebutton_states[0] = self.ui.button_toggle_valve1.isChecked()
            valvebutton_states[1] = self.ui.button_toggle_valve2.isChecked()
            valvebutton_states[2] = self.ui.button_toggle_valve3.isChecked()


            # CONSTRUCT MESSAGE (INVERTING OF ARRAY NEEDED SINCE VALVES ARE NORMALLY OPEN)   
            binary_string = ''.join('1' if val else '0' for val in np.invert(valvebutton_states))
            decimal_value = int(binary_string, 2)
            msg = f"wVS-{decimal_value}"
            
            # Write the message
            self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
            msg = self.device_serials[2].readline()
            print("RESPONSE: " + msg.decode())

        else:
            self.ui.display_system_log.append("COULD NOT CHANGE VALVE STATE. 3PAC IS NOT CONNECTED")
    

    # ===============================================================================================================================
    #  _____ _____ __ __ __    _____    _____ _____ _____ _____ _____ _____    _____ _____ _____ _____ _____ _____ _____ _____ _____ 
    # |   __|_   _|  |  |  |  |   __|  |     |  |  |  _  |   | |   __|   __|  |   __|  |  |   | |     |_   _|     |     |   | |   __|
    # |__   | | | |_   _|  |__|   __|  |   --|     |     | | | |  |  |   __|  |   __|  |  | | | |   --| | | |-   -|  |  | | | |__   |
    # |_____| |_|   |_| |_____|_____|  |_____|__|__|__|__|_|___|_____|_____|  |__|  |_____|_|___|_____| |_| |_____|_____|_|___|_____|
    # ===============================================================================================================================

    # SET THE BACKGROUND COLOR OF A WIDGET. BUT WHY? NEVER CALLED ANYWAYS (YET)
    def set_background_color(self, widget, color):
        palette = widget.palette()
        palette.setColor(widget.backgroundRole(), color)
        widget.setPalette(palette)

    # SET STYLE FOR ALL CONNECTION-INDICATORS
    # TODO: ADD 2nd COLOUR POSSIBILITY (ORANGE) FOR WARNINGS
    def set_connection_indicators(self, connections):
        if connections[0]:
            self.ui.indicator_connection_psu.setStyleSheet("QFrame{background-color: #0796FF; border-radius: 10;}")
        else:
            self.ui.indicator_connection_psu.setStyleSheet("QFrame{background-color: #808080; border-radius: 10;}")

        if connections[1]:
            self.ui.indicator_connection_pg.setStyleSheet("QFrame{background-color: #0796FF; border-radius: 10;}")
        else:
            self.ui.indicator_connection_pg.setStyleSheet("QFrame{background-color: #808080; border-radius: 10;}")

        if connections[2]:
            self.ui.indicator_connection_3pac.setStyleSheet("QFrame{background-color: #0796FF; border-radius: 10;}")
        else:
            self.ui.indicator_connection_3pac.setStyleSheet("QFrame{background-color: #808080; border-radius: 10;}")

        if connections[3]:
            self.ui.indicator_connection_temp.setStyleSheet("QFrame{background-color: #0796FF; border-radius: 10;}")
        else:
            self.ui.indicator_connection_temp.setStyleSheet("QFrame{background-color: #808080; border-radius: 10;}")


    # ===============================================================================================================================
    #  _____ _____ ____  _____ _____ _____ _____    _____ _____ _____ _____    _____ _____ _____ _____ _____ _____ _____ _____ _____ 
    # |   __|     |    \|   __| __  |  _  | __  |  |     |   __|   | |  |  |  |   __|  |  |   | |     |_   _|     |     |   | |   __|
    # |__   |-   -|  |  |   __| __ -|     |    -|  | | | |   __| | | |  |  |  |   __|  |  | | | |   --| | | |-   -|  |  | | | |__   |
    # |_____|_____|____/|_____|_____|__|__|__|__|  |_|_|_|_____|_|___|_____|  |__|  |_____|_|___|_____| |_| |_____|_____|_|___|_____|
    # ===============================================================================================================================

    def menu_button_dashboard_click(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def menu_button_graphs_click(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def menu_button_control_click(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def menu_button_settings_click(self):
        self.ui.stackedWidget.setCurrentIndex(3)


    # ==========================================================================================================
    #  _____ _____ _____ _____ _____ _____ _____ _____    _____ _____ _____ _____ _____ _____ _____ _____ _____ 
    # |     |     |  |  |   __|     |   __|   | |_   _|  |   __|  |  |   | |     |_   _|     |     |   | |   __|
    # | | | |  |  |  |  |   __| | | |   __| | | | | |    |   __|  |  | | | |   --| | | |-   -|  |  | | | |__   |
    # |_|_|_|_____|\___/|_____|_|_|_|_____|_|___| |_|    |__|  |_____|_|___|_____| |_| |_____|_____|_|___|_____|
    # ==========================================================================================================

    # BUTTON CALLBACK: HOMING
    def movement_homing(self, motornumber=0):
        # motornumber = 0 --> ALL MOTORS
        if self.flag_connections[2]:
            writeMotorHoming(self.device_serials[2], motornumber)
            if motornumber == 0:
                print("HOMING STARTED FOR ALL MOTORS")
            else:
                print("HOMING STARTED FOR MOTOR {}".format(motornumber))

    # BUTTON CALLBACK (PRESS): JOGGING
    def movement_startjogging(self, motornumber, direction, fast):
        if self.flag_connections[2]:
            if direction < 0:
                direction = 2
            writeMotorJog(self.device_serials[2], motornumber, direction, fast)

            print("TRYING TO START JOGGING: motor: {}; direction: {}; fast: {}".format(motornumber, direction, fast))

    # BUTTON CALLBACK (RELEASE): JOGGING
    def movement_stopjogging(self, motornumber):
        if self.flag_connections[2]:
            writeMotorJog(self.device_serials[2], motornumber, 0, 0)

            print("TRYING TO STOP JOGGING: motor: {}".format(motornumber))

    # BUTTON CALLBACK: MOVE RELATIVE TO POSITION
    def movement_relative(self, motornumber, distance):
        if self.flag_connections[2]:
            if distance < 0:
                distance = -distance
                direction = 2
            elif distance > 0:
                direction = 1
            else:
                direction = 0
            writeMotorDistance(self.device_serials[2], motornumber, distance, direction)

            print("TRYING TO MOVE: motor: {}; distance: {}; direction: {}".format(motornumber, distance, direction))

    # BUTTON CALLBACK: MOVE ABSOLUTE POSITION
    def movement_absoluteposition(self, motornumber):
        if self.flag_connections[2]:    # IF 3PAC CONNECTED
            
            movement = True # FLAG

            if motornumber == 1:  # MOTOR 1 --> BLOOD
                position = self.ui.input_blood_position.text()
                
            elif motornumber == 2:  # MOTOR 2 --> CARTRIDGE
                position = self.ui.input_cartridge_position.text()

            elif motornumber == 3:  # MOTOR 3 --> FLASKS LEFT/RIGHT
                position = self.ui.line_flasks_pos_lr.text()

            elif motornumber == 4:  # MOTOR 4 --> FLASKS UP/DOWN
                position = self.ui.line_flasks_pos_ud.text()

            else:
                self.ui.display_system_log.append("MOTOR: UNKNOWN NUMBER {}".format(motornumber))
                movement = False

            if movement:
                try:
                    position_float = float(position)
                    writeMotorPosition(self.device_serials[2], motornumber, position_float)
                except:
                    print("POSITION VALUE IS NOT A NUMBER") 
                
        else:
            self.ui.display_system_log.append("COULD NOT MOVE MOTORS. 3PAC IS NOT CONNECTED")
            self.ui.button_valvestate_off.setChecked(True)

    # BUTTON CALLBACK: MOVE TO ABSOLUTE POSITION    (UNUSED)
    def movement_absoluteposition_blood(self):
        position = self.ui.input_blood_position.text()
        try:
            position_float = float(position)
            print(type(position_float))
            print(position_float)
            writeMotorPosition(self.device_serials[2], 1, position_float)

        except:
            print("VALUE IS NOT A NUMBER") 

    # BUTTON CALLBACK: MOVE TO ABSOLUTE POSITION    (UNUSED)
    def movement_absoluteposition_cartridge(self):
        position = self.ui.input_cartridge_position.text()
        try:
            position_float = float(position)
            print(type(position_float))
            print(position_float)
            writeMotorPosition(self.device_serials[2], 2, position_float)

        except:
            print("VALUE IS NOT A NUMBER")

    # BUTTON CALLBACK: MOVE TO ABSOLUTE POSITION    (UNUSED)
    def movement_absoluteposition_flasks_ud(self):
        position = self.ui.line_flasks_pos_ud.text()
        try:
            position_float = float(position)
            print(type(position_float))
            print(position_float)
            writeMotorPosition(self.device_serials[2], 4, position_float)

        except:
            print("VALUE IS NOT A NUMBER") 

    # BUTTON CALLBACK: MOVE TO ABSOLUTE POSITION    (UNUSED)
    def movement_absoluteposition_flasks_lr(self):
        position = self.ui.line_flasks_pos_lr.text()
        try:
            position_float = float(position)
            print(type(position_float))
            print(position_float)
            writeMotorPosition(self.device_serials[2], 3, position_float)

        except:
            print("VALUE IS NOT A NUMBER") 

    # BUTTON CALLBACK: MOVE TO ABSOLUTE POSITION    TODO: ALSO ADD THIS TO THE COMBINED FUNCTION
    def movement_flasknumber(self, flasknumber):
        if self.flag_connections[2]:
            writeFlaskPosition(self.device_serials[2], flasknumber)
            print("TRYING TO MOVE FLASK TO POSITION {}".format(flasknumber))
        
    
    # ===========================================================================================================================================
    #  _____ _____ __ __ _____ _____ _____ _____ _____    _____ _____ _____ _____ _____    _____ _____ _____ _____ _____ _____ _____ _____ _____ 
    # |  |  |   __|  |  |  _  | __  |   __|   __|   __|  |   __|  |  |   __|   | |_   _|  |   __|  |  |   | |     |_   _|     |     |   | |   __|
    # |    -|   __|_   _|   __|    -|   __|__   |__   |  |   __|  |  |   __| | | | | |    |   __|  |  | | | |   --| | | |-   -|  |  | | | |__   |
    # |__|__|_____| |_| |__|  |__|__|_____|_____|_____|  |_____|\___/|_____|_|___| |_|    |__|  |_____|_|___|_____| |_| |_____|_____|_|___|_____|
    # ===========================================================================================================================================

    def keyPressEvent(self, event):
        print("KEY EVENT FIRED: PRESSED")
        print(event.key())
        print(event.type())
        print("AUTO REPEAT: " + str(event.isAutoRepeat()))

        if event.key() == Qt.Key_W and not event.isAutoRepeat():  # AT "UP ARROW" KEY-EVENT
            self.movement_startjogging(1, -1, False)

        if event.key() == Qt.Key_S and not event.isAutoRepeat():  # AT "DOWN ARROW" KEY-EVENT
            self.movement_startjogging(1, 1, False)
    
    def keyReleaseEvent(self, event):
        print("KEY EVENT FIRED: RELEASED")
        print(event.key())
        print(event.type())
        print("AUTO REPEAT: " + str(event.isAutoRepeat()))

        if event.key() == Qt.Key_W and not event.isAutoRepeat():  # AT "UP ARROW" KEY-EVENT
            self.movement_stopjogging(1)

        if event.key() == Qt.Key_S and not event.isAutoRepeat():  # AT "DOWN ARROW" KEY-EVENT
            self.movement_stopjogging(1)




# =====================================================================================================
# ███    ███  █████  ██ ███    ██     ███████ ██    ██ ███    ██  ██████ ████████ ██  ██████  ███    ██
# ████  ████ ██   ██ ██ ████   ██     ██      ██    ██ ████   ██ ██         ██    ██ ██    ██ ████   ██
# ██ ████ ██ ███████ ██ ██ ██  ██     █████   ██    ██ ██ ██  ██ ██         ██    ██ ██    ██ ██ ██  ██
# ██  ██  ██ ██   ██ ██ ██  ██ ██     ██      ██    ██ ██  ██ ██ ██         ██    ██ ██    ██ ██  ██ ██
# ██      ██ ██   ██ ██ ██   ████     ██       ██████  ██   ████  ██████    ██    ██  ██████  ██   ████
# =====================================================================================================

if __name__ == "__main__":
    # OPEN THE WINDOW
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('GUI_ElectronicsTeam/style.qss').read_text())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
