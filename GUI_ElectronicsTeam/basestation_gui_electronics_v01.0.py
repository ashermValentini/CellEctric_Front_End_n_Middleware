import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Communication_Functions.communication_functions import *

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QLabel, QButtonGroup, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSlot, QFile, QTextStream, QTimer
from PyQt5.QtGui import QColor
from PyQt5.uic import loadUi
from pathlib import Path

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

import numpy as np

from Ui_GUI_Design_01 import Ui_MainWindow

# CONSTANTS
SUCROSE_FLOWRATE_MAX = 10
ETHANOL_FLOWRATE_MAX = 10
BLOOD_FLOWRATE_MAX = 5


# =================================================================
#   __  __   _   ___ _  _  __      _____ _  _ ___   _____      __
#  |  \/  | /_\ |_ _| \| | \ \    / /_ _| \| |   \ / _ \ \    / /
#  | |\/| |/ _ \ | || .` |  \ \/\/ / | || .` | |) | (_) \ \/\/ / 
#  |_|  |_/_/ \_\___|_|\_|   \_/\_/ |___|_|\_|___/ \___/ \_/\_/  
#
# =================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # VARIABLES

        # FLAGS TEST
        #                       [PSU  , PG   , 3PAC , TEMPSENS]
        self.flag_connections = [False, False, False, False]


        self.flag_psu_on = False
        self.flag_pg_on = False
        self.flag_3pac_on = False

        self.flag_suc_on = False
        self.flag_eth_on = False
        self.flag_suc_pid = False
        self.flag_eth_pid = False
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
                border-radius: 60px;
                background-color: qconicalgradient(cx:0.5, cy:0.5, angle:230, stop:0.9 rgba(7, 150, 255, 0), stop:1.0 rgba(7, 150, 255, 255));
                }"""
        self.ui.circularProgress_suc_eth.setStyleSheet(style_sheets)
        self.ui.circularProgress_blood.setStyleSheet(style_sheets)

        self.ui.value_flowrate_suc_eth.setText("OFF")
        self.ui.value_flowrate_blood.setText("OFF")

        # SET INDIVIDUAL VALVE BUTTONS DISABLED AT STARTUP
        self.ui.button_toggle_valve1.setEnabled(False)
        self.ui.button_toggle_valve2.setEnabled(False)
        self.ui.button_toggle_valve3.setEnabled(False)
        # SET VALVE BUTTON GROUP TO OFF
        self.ui.button_valvestate_off.setChecked(True)

        # SETUP BUTTON GROUPS
        self.ui.btngroup_valve_states.setExclusive(True)


        # MENU BUTTONS
        self.ui.menu_dashboard_button_1.clicked.connect(self.menu_button_dashboard_click)
        self.ui.menu_control_button_1.clicked.connect(self.menu_button_control_click)
        self.ui.menu_graphs_button_1.clicked.connect(self.menu_button_graphs_click)
        self.ui.menu_settings_button_1.clicked.connect(self.menu_button_settings_click)

        # BUTTON CLICKS
        self.ui.button_toggle_psu_enable.clicked.connect(self.psu_button_toggle)
        self.ui.button_toggle_pg_enable.clicked.connect(self.pg_button_toggle)

        self.ui.button_toggle_sucflow.clicked.connect(self.toggle_flow_suc)
        self.ui.button_toggle_ethflow.clicked.connect(self.toggle_flow_eth)
        self.ui.button_toggle_bloodflow.clicked.connect(self.toggle_flow_blood)

        self.ui.button_valvestate_sucrose.clicked.connect(self.change_valve_state_sucrose)
        self.ui.button_valvestate_ethanol.clicked.connect(self.change_valve_state_ethanol)
        self.ui.button_valvestate_cleaning.clicked.connect(self.change_valve_state_cleaning)
        self.ui.button_valvestate_off.clicked.connect(self.change_valve_state_off)

        self.ui.button_toggle_valve1.clicked.connect(self.change_single_valve)
        self.ui.button_toggle_valve2.clicked.connect(self.change_single_valve)
        self.ui.button_toggle_valve3.clicked.connect(self.change_single_valve)



        # MOVEMENT BUTTONS
        # JOGGING BLOOD
        self.ui.move_blood_upfast.pressed.connect(lambda: self.movement_startjogging(1, -1, True))     #(self, motornumber, direction, fast)
        self.ui.move_blood_upfast.released.connect(lambda: self.movement_stopjogging(1))               #(self, motornumber)

        self.ui.move_blood_upslow.pressed.connect(lambda: self.movement_startjogging(1, -1, False))
        self.ui.move_blood_upslow.released.connect(lambda: self.movement_stopjogging(1))

        self.ui.move_blood_downfast.pressed.connect(lambda: self.movement_startjogging(1, 1, True))
        self.ui.move_blood_downfast.released.connect(lambda: self.movement_stopjogging(1))

        self.ui.move_blood_downslow.pressed.connect(lambda: self.movement_startjogging(1, 1, False))
        self.ui.move_blood_downslow.released.connect(lambda: self.movement_stopjogging(1))

        # JOGGING CARTRIDGE
        self.ui.move_cartridge_upfast.pressed.connect(lambda: self.movement_startjogging(2, -1, True))     #(self, motornumber, direction, fast)
        self.ui.move_cartridge_upfast.released.connect(lambda: self.movement_stopjogging(2))               #(self, motornumber)

        self.ui.move_cartridge_upslow.pressed.connect(lambda: self.movement_startjogging(2, -1, False))
        self.ui.move_cartridge_upslow.released.connect(lambda: self.movement_stopjogging(2))

        self.ui.move_cartridge_downfast.pressed.connect(lambda: self.movement_startjogging(2, 1, True))
        self.ui.move_cartridge_downfast.released.connect(lambda: self.movement_stopjogging(2))

        self.ui.move_cartridge_downslow.pressed.connect(lambda: self.movement_startjogging(2, 1, False))
        self.ui.move_cartridge_downslow.released.connect(lambda: self.movement_stopjogging(2))

        # JOGGING FLASKS HORIZONTAL
        self.ui.move_flasks_leftfast.pressed.connect(lambda: self.movement_startjogging(3, -1, True))     #(self, motornumber, direction, fast)
        self.ui.move_flasks_leftfast.released.connect(lambda: self.movement_stopjogging(3))               #(self, motornumber)

        self.ui.move_flasks_leftslow.pressed.connect(lambda: self.movement_startjogging(3, -1, False))
        self.ui.move_flasks_leftslow.released.connect(lambda: self.movement_stopjogging(3))

        self.ui.move_flasks_rightfast.pressed.connect(lambda: self.movement_startjogging(3, 1, True))
        self.ui.move_flasks_rightfast.released.connect(lambda: self.movement_stopjogging(3))

        self.ui.move_flasks_rightslow.pressed.connect(lambda: self.movement_startjogging(3, 1, False))
        self.ui.move_flasks_rightslow.released.connect(lambda: self.movement_stopjogging(3))

        # JOGGING FLASKS VERTICAL
        self.ui.move_flasks_upfast.pressed.connect(lambda: self.movement_startjogging(4, -1, True))     #(self, motornumber, direction, fast)
        self.ui.move_flasks_upfast.released.connect(lambda: self.movement_stopjogging(4))               #(self, motornumber)

        self.ui.move_flasks_upslow.pressed.connect(lambda: self.movement_startjogging(4, -1, False))
        self.ui.move_flasks_upslow.released.connect(lambda: self.movement_stopjogging(4))

        self.ui.move_flasks_downfast.pressed.connect(lambda: self.movement_startjogging(4, 1, True))
        self.ui.move_flasks_downfast.released.connect(lambda: self.movement_stopjogging(4))

        self.ui.move_flasks_downslow.pressed.connect(lambda: self.movement_startjogging(4, 1, False))
        self.ui.move_flasks_downslow.released.connect(lambda: self.movement_stopjogging(4))

        # TRAVEL BLOOD
        self.ui.move_blood_up_10.clicked.connect(lambda: self.movement_relative(1, -10))                 #(self, motornumber, distance)
        self.ui.move_blood_up_1.clicked.connect(lambda: self.movement_relative(1, -1))
        self.ui.move_blood_up_01.clicked.connect(lambda: self.movement_relative(1, -0.1))
        self.ui.move_blood_down_10.clicked.connect(lambda: self.movement_relative(1, 10))
        self.ui.move_blood_down_1.clicked.connect(lambda: self.movement_relative(1, 1))
        self.ui.move_blood_down_01.clicked.connect(lambda: self.movement_relative(1, 0.1))

        self.ui.move_blood_bottom.clicked.connect(lambda: self.movement_relative(1, 200))           # JUST MOVE VERY FAR (1m) AND REACH THE END
        self.ui.move_blood_top.clicked.connect(lambda: self.movement_relative(1, -200))

        # TRAVEL CARTRIDGE
        self.ui.move_cartridge_up_10.clicked.connect(lambda: self.movement_relative(2, -10))                 #(self, motornumber, distance)
        self.ui.move_cartridge_up_1.clicked.connect(lambda: self.movement_relative(2, -1))
        self.ui.move_cartridge_up_01.clicked.connect(lambda: self.movement_relative(2, -0.1))
        self.ui.move_cartridge_down_10.clicked.connect(lambda: self.movement_relative(2, 10))
        self.ui.move_cartridge_down_1.clicked.connect(lambda: self.movement_relative(2, 1))
        self.ui.move_cartridge_down_01.clicked.connect(lambda: self.movement_relative(2, 0.1))

        self.ui.move_cartridge_bottom.clicked.connect(lambda: self.movement_relative(2, 200))           # JUST MOVE VERY FAR (1m) AND REACH THE END
        self.ui.move_cartridge_top.clicked.connect(lambda: self.movement_relative(2, -200))

        # TRAVEL FLASKS HORIZONTAL
        self.ui.move_flasks_left_10.clicked.connect(lambda: self.movement_relative(3, -10))                 #(self, motornumber, distance)
        self.ui.move_flasks_left_1.clicked.connect(lambda: self.movement_relative(3, -1))
        self.ui.move_flasks_left_01.clicked.connect(lambda: self.movement_relative(3, -0.1))
        self.ui.move_flasks_right_10.clicked.connect(lambda: self.movement_relative(3, 10))
        self.ui.move_flasks_right_1.clicked.connect(lambda: self.movement_relative(3, 1))
        self.ui.move_flasks_right_01.clicked.connect(lambda: self.movement_relative(3, 0.1))

        self.ui.move_flasks_rightmost.clicked.connect(lambda: self.movement_relative(3, 200))           # JUST MOVE VERY FAR (1m) AND REACH THE END
        self.ui.move_flasks_leftmost.clicked.connect(lambda: self.movement_relative(3, -200))

        # TRAVEL FLASKS VERTICAL
        self.ui.move_flasks_up_10.clicked.connect(lambda: self.movement_relative(3, -10))                 #(self, motornumber, distance)
        self.ui.move_flasks_up_1.clicked.connect(lambda: self.movement_relative(3, -1))
        self.ui.move_flasks_up_01.clicked.connect(lambda: self.movement_relative(3, -0.1))
        self.ui.move_flasks_down_10.clicked.connect(lambda: self.movement_relative(3, 10))
        self.ui.move_flasks_down_1.clicked.connect(lambda: self.movement_relative(3, 1))
        self.ui.move_flasks_down_01.clicked.connect(lambda: self.movement_relative(3, 0.1))

        self.ui.move_flasks_bottom.clicked.connect(lambda: self.movement_relative(3, 200))           # JUST MOVE VERY FAR (1m) AND REACH THE END
        self.ui.move_flasks_top.clicked.connect(lambda: self.movement_relative(3, -200))


        # TRAVEL TO POSITION
        self.ui.button_blood_setpos.clicked.connect(self.movement_absoluteposition_blood)
        self.ui.button_cartridge_setpos.clicked.connect(self.movement_absoluteposition_cartridge)
        self.ui.button_set_flasks_pos_ud.clicked.connect(self.movement_absoluteposition_flasks_ud)
        self.ui.button_set_flasks_pos_lr.clicked.connect(self.movement_absoluteposition_flasks_lr)





        # =================
        # START SERIAL CONNECTION TO DEVICES
        # =================
        self.device_serials = serial_start_connections()

        self.ui.display_system_log.append("Connection to Devices established:")

        # CHECK CONNECTION STATUS
        if self.device_serials[0].isOpen():
            self.ui.display_system_log.append("PSU OPEN @ PORT " + self.device_serials[0].name)
            self.flag_connections[0] = True
        print("FLAG PSU: {}".format(self.flag_connections[0]))
        if self.device_serials[1].isOpen():
            self.ui.display_system_log.append("PG OPEN @ PORT " + self.device_serials[1].name)
            self.flag_connections[1] = True
        print("FLAG PG: {}".format(self.flag_connections[1]))
        if self.device_serials[2].isOpen():
            self.ui.display_system_log.append("3PAC OPEN @ PORT " + self.device_serials[2].name)
            self.flag_connections[2] = True
        print("FLAG 3PAC: {}".format(self.flag_connections[2]))
        if self.device_serials[3] is not None:
            self.ui.display_system_log.append("TEMP SENS OPENED")
            self.flag_connections[3] = True
        print("FLAG TEMPSENS: {}".format(self.flag_connections[3]))

        # HANDSHAKES WITH DEVICES
        if self.flag_connections[2]:
            handshake_3PAC(self.device_serials[2], print_handshake_message=True)

        self.set_connection_indicators(self.flag_connections)


        # INITIALIZE SCALING VALUES FOR PLOTS
        self.zerodata = [2000, 2000]
        self.maxval_pulse = 10  
        self.minval_pulse = -10


        #==============================================================
        # INIT STATES
        #==============================================================

        self.start_plotting()

        # INIT 3PAC
        if self.flag_connections[2]:
            # INITIALIZE VALVE STATES (ALL CLOSED)
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

        # =================
        # START PLOT
        # =================
        

        
        


    # =================================================
    # FLOW RATES - UPDATES & TOGGLES
    # =================================================

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


    def toggle_flow_suc(self):

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


    def toggle_flow_eth(self):
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
    # PLOTTING 
    # =================================================

    # START FLOWRATE UPDATE TIMER
    def start_flowrate_suceth_update(self):
        # TIMER
        self.flow_timer = QTimer()
        self.flow_timer.setInterval(self.interval)
        self.flow_timer.timeout.connect(self.update_flowrate_suceth)
        self.flow_timer.start()

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



    # =================================================
    # DEVICE TOGGLES (ENABLE / DISABLE)
    # =================================================

    def psu_button_toggle(self):
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
                    self.ui.button_toggle_psu_enable.setChecked(False)                      # SET THE BUTTON TO "ON" AGAIN

        else:
            self.ui.display_system_log.append("PSU IS NOT CONNECTED! COULD NOT SWITCH IT ON")     # LOG TO GUI
            self.ui.button_toggle_psu_enable.setChecked(False)                      # SET THE BUTTON TO "ON" AGAIN

    def pg_button_toggle(self):
        if self.flag_connections[1]:
            if self.flag_pg_on:
                sucess = send_PG_disable(self.device_serials[1], 1)

                # CHECK IF DATA WAS SENT SUCESSFULLY
                if sucess:                                          # SENDING SUCESSFUL
                    self.ui.display_system_log.append("PG: OFF")    # LOG TO GUI
                    self.flag_pg_on = False                        # SET FLAG FOR PG STATE
                else:                                                                       # SENDING NOT POSSIBLE (5 tries)
                    self.ui.display_system_log.append("ERROR: Could not switch PG OFF")     # LOG TO GUI
                    self.ui.button_toggle_pg_enable.setChecked(True)                       # SET THE BUTTON TO "ON" AGAIN
            else:
                send_PG_pulsetimes(self.device_serials[1])
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


    # =================================================
    # VALVE CONTROL
    # =================================================

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
    
    # =================================================
    # STYLE CHANGE FUNCTIONS
    # =================================================

    def set_background_color(self, widget, color):
        # Helper function to set the background color of a widget
        palette = widget.palette()
        palette.setColor(widget.backgroundRole(), color)
        widget.setPalette(palette)

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


    # =================================================
    # MENU CHANGE FUNCTIONS
    # =================================================
    def menu_button_dashboard_click(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def menu_button_graphs_click(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def menu_button_control_click(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def menu_button_settings_click(self):
        self.ui.stackedWidget.setCurrentIndex(3)





    # =================================================
    # MOVEMENT FUNCTIONS
    # =================================================
    def movement_startjogging(self, motornumber, direction, fast):
        if self.flag_connections[2]:
            if direction < 0:
                direction = 2
            writeMotorJog(self.device_serials[2], motornumber, direction, fast)

            print("TRYING TO START JOGGING: motor: {}; direction: {}; fast: {}".format(motornumber, direction, fast))


    def movement_stopjogging(self, motornumber):
        if self.flag_connections[2]:
            writeMotorJog(self.device_serials[2], motornumber, 0, 0)

        print("TRYING TO STOP JOGGING: motor: {}".format(motornumber))

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

    def movement_absoluteposition_blood(self):
        position = self.ui.input_blood_position.text()
        try:
            position_float = float(position)
            print(type(position_float))
            print(position_float)
            writeMotorPosition(self.device_serials[2], 1, position_float)

        except:
            print("VALUE IS NOT A NUMBER") 

    def movement_absoluteposition_cartridge(self):
        position = self.ui.input_blood_position.text()
        try:
            position_float = float(position)
            print(type(position_float))
            print(position_float)
            writeMotorPosition(self.device_serials[2], 2, position_float)

        except:
            print("VALUE IS NOT A NUMBER") 

    def movement_absoluteposition_flasks_ud(self):
        position = self.ui.input_blood_position.text()
        try:
            position_float = float(position)
            print(type(position_float))
            print(position_float)
            writeMotorPosition(self.device_serials[2], 3, position_float)

        except:
            print("VALUE IS NOT A NUMBER") 

    def movement_absoluteposition_flasks_lr(self):
        position = self.ui.input_blood_position.text()
        try:
            position_float = float(position)
            print(type(position_float))
            print(position_float)
            writeMotorPosition(self.device_serials[2], 4, position_float)

        except:
            print("VALUE IS NOT A NUMBER") 
    
    

    # =================================================
    # KEYPRESS EVENTS FUNCTIONS
    # =================================================
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
