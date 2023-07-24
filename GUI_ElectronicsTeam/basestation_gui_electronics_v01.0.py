import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Communication_Functions.communication_functions import *


from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QLabel, QButtonGroup, QVBoxLayout
from PyQt5.QtCore import pyqtSlot, QFile, QTextStream, QTimer
from PyQt5.QtGui import QColor
from PyQt5.uic import loadUi
from pathlib import Path

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

import numpy as np

from Ui_GUI_Design_01 import Ui_MainWindow


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

        # SETUP BUTTON GROUPS
        self.ui.btngroup_valve_states.setExclusive(True)

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


        # =================
        # START SERIAL CONNECTION TO DEVICES
        # =================
        self.device_serials = serial_start_connections()
        handshake_3PAC(self.device_serials[2], print_handshake_message=True)
        self.ui.display_system_log.append("Connection to Devices established:")

        # CHECK PSU, PG, 3PAC CONNECTION
        if self.device_serials[0].isOpen(): # PSU
            self.ui.indicator_connection_psu.setStyleSheet("QFrame{background-color: #0796FF; border-radius: 10;}")
            self.ui.display_system_log.append("PSU OPEN @ PORT " + self.device_serials[0].name)
        else:
            self.ui.indicator_connection_psu.setStyleSheet("QFrame{background-color: #808080; border-radius: 10;}")
            self.ui.display_system_log.append("PSU NOT FOUND")


        if self.device_serials[1].isOpen(): # PG
            self.ui.indicator_connection_pg.setStyleSheet("QFrame{background-color: #0796FF; border-radius: 10;}")
            self.ui.display_system_log.append("PG OPEN @ PORT " + self.device_serials[1].name)
        else:
            self.ui.indicator_connection_pg.setStyleSheet("QFrame{background-color: #808080; border-radius: 10;}")
            self.ui.display_system_log.append("PG NOT FOUND")


        if self.device_serials[2].isOpen(): # 3PAC
            self.ui.indicator_connection_3pac.setStyleSheet("QFrame{background-color: #0796FF; border-radius: 10;}")
            self.ui.display_system_log.append("3PAC OPEN @ PORT " + self.device_serials[2].name)
        else:
            self.ui.indicator_connection_3pac.setStyleSheet("QFrame{background-color: #808080; border-radius: 10;}")
            self.ui.display_system_log.append("3PAC NOT FOUND")

        if self.device_serials[3] is not None:
            #self.ui.indicator_connection_3pac.setStyleSheet("QFrame{background-color: #0796FF; border-radius: 10;}")
            self.ui.display_system_log.append("TEMP SENS OPENED")
        else:
            #self.ui.indicator_connection_3pac.setStyleSheet("QFrame{background-color: #808080; border-radius: 10;}")
            self.ui.display_system_log.append("TEMP SENS NOT FOUND")


        

        # INITIALIZE SCALING VALUES
        self.zerodata = [2000, 2000]
        self.maxval_pulse = 10  
        self.minval_pulse = -10


        # INITIALIZE VALVE STATES (ALL CLOSED)
        # Construct the message
        msg = f'wVS-111'
        # Write the message
        self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
        msg = self.device_serials[2].readline()
        print("RESPONSE: " + msg.decode())
        time.sleep(2)

        # =================
        # START TEMPERATURE PLOT
        # =================
        self.start_plotting()

        # INITIALIZE PID STATES (ALL CLOSED)
        print("MESSAGE: PID On")
        msg = "wPS-22"
        self.device_serials[2].write(msg.encode())
        msg = self.device_serials[2].readline()
        print("RESPONSE: " + msg.decode())
        time.sleep(2)
        self.start_flowrate_suceth()
        


    # =================================================
    # FLOW RATES - UPDATES & TOGGLES
    # =================================================

    def start_flowrate_suceth(self):
        # TIMER
        self.flow_timer = QTimer()
        self.flow_timer.setInterval(self.interval)
        self.flow_timer.timeout.connect(self.update_flowrate_suceth)
        self.flow_timer.start()


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

                writePumpFlowRate(self.device_serials[2], input_value_float, 0)

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

                writePumpFlowRate(self.device_serials[2], 0, input_value_float)

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

    def start_plotting(self):

        #dynamic x axis 
        self.temp_x = np.linspace(0, 499, 500)  # This creates an array from 0 to 499 with 500 elements.
        self.tempmax = np.zeros(500)
        self.tempmax.fill(37)
        self.voltage_x = np.linspace(0, 499, 500)


        # Plotting variables
        self.interval = 500  # ms
        self.tempplotdata = np.zeros(500)   # initialize Temperature values with 0
        self.temp_y = self.tempplotdata
        self.voltageplotdata = np.zeros(500)   # initialize Temperature values with 0

        # TIMER
        self.plot_timer = QTimer()
        self.plot_timer.setInterval(self.interval)
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start()

    def update_plot(self):
        temperature = read_temperature(self.device_serials[3])

        if temperature is not None:
            self.tempplotdata = np.roll(self.tempplotdata, -1)
            self.tempplotdata[-1:] = temperature
            self.temp_y = self.tempplotdata
            
            self.temp_x = np.roll(self.temp_x, -1)
            self.temp_x[-1] = self.temp_x[-2] + 1  # This will keep increasing the count on the x-axis

        if self.device_serials[1].isOpen():
            self.voltage_y, _ = read_next_PG_pulse(self.device_serials[1])  # READ NEXT PULSE
        else:
            self.voltage_y = np.zeros((1500,2))

        # CUT THE LAST PART
        new_length = round(self.voltage_y.shape[0]/2)
        self.voltage_y = self.voltage_y[:new_length]

        self.voltage_y[:, 0] -= self.zerodata[0]    # ZERO THE VOLTAGE DATA
        self.voltage_y[:, 1] -= self.zerodata[1]    # ZERO THE CURRENT DATA

        self.voltage_y[:, 0] *= 0.15                # SCALE THE VOLTAGE DATA
        self.voltage_y[:, 1] *= 0.15                # SCALE THE CURRENT DATA



        maxval_pulse_new = self.voltage_y.max(axis=0)[0]    # GET MAX VALUE FROM VOLTAGE PULSE
        minval_pulse_new = self.voltage_y.min(axis=0)[0]    # GET MIN VALUE FROM VOLTAGE PULSE

        if maxval_pulse_new > self.maxval_pulse:        # CHECK MAX VALUE OVER TIME
            self.maxval_pulse = maxval_pulse_new
            
        if minval_pulse_new < self.minval_pulse:        # CHECK MIN VALUE OVER TIME
            self.minval_pulse = minval_pulse_new
        
        self.ui.value_voltage_max.setText("{:.2f}".format(maxval_pulse_new))    # SET GUI TEXT
        self.ui.value_voltage_min.setText("{:.2f}".format(minval_pulse_new))    # SET GUI TEXT



        #print("Data Length: {}".format(self.voltage_y.shape[0]))
        #print("MINVAL: {}".format(self.minval_pulse))
        #print("MAXVAL: {}".format(self.maxval_pulse))

        
        self.voltage_x = np.linspace(0, self.voltage_y.shape[0]-1, self.voltage_y.shape[0])
    



        #self.ui.MplWidget.canvas.axes.clear()
        #self.ui.MplWidget.canvas.axes.plot(self.xdata, self.ydata)
        #self.ui.MplWidget.canvas.draw()

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
    # DEVICE TOGGLES
    # =================================================

    def psu_button_toggle(self):
        if self.device_serials[0].isOpen():
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
        if self.device_serials[1].isOpen():
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
        self.ui.display_system_log.append("VALVES: SUCROSE")
        msg = f'wVS-010'
        # Write the message
        self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
        msg = self.device_serials[2].readline()
        print("RESPONSE: " + msg.decode())

        # EXACTLY INVERTED BUTTONS, SINCE VALVES ARE NORMALLY OPEN
        self.ui.button_toggle_valve1.setChecked(True)
        self.ui.button_toggle_valve1.setChecked(False)
        self.ui.button_toggle_valve1.setChecked(True)


    def change_valve_state_ethanol(self):
        self.ui.display_system_log.append("VALVES: ETHANOL")
        msg = f'wVS-001'
        # Write the message
        self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
        msg = self.device_serials[2].readline()
        print("RESPONSE: " + msg.decode())

        # EXACTLY INVERTED BUTTONS, SINCE VALVES ARE NORMALLY OPEN
        self.ui.button_toggle_valve1.setChecked(True)
        self.ui.button_toggle_valve1.setChecked(True)
        self.ui.button_toggle_valve1.setChecked(False)


    def change_valve_state_cleaning(self):
        self.ui.display_system_log.append("VALVES: CLEANING")
        msg = f'wVS-100'
        # Write the message
        self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
        msg = self.device_serials[2].readline()
        print("RESPONSE: " + msg.decode())

        # EXACTLY INVERTED BUTTONS, SINCE VALVES ARE NORMALLY OPEN
        self.ui.button_toggle_valve1.setChecked(False)
        self.ui.button_toggle_valve1.setChecked(True)
        self.ui.button_toggle_valve1.setChecked(True)


    def change_valve_state_off(self):
        self.ui.display_system_log.append("VALVES: OFF")
        msg = f'wVS-111'
        # Write the message
        self.device_serials[2].write(msg.encode())  # encode the string to bytes before sending
        msg = self.device_serials[2].readline()
        print("RESPONSE: " + msg.decode())

        # EXACTLY INVERTED BUTTONS, SINCE VALVES ARE NORMALLY OPEN
        self.ui.button_toggle_valve1.setChecked(False)
        self.ui.button_toggle_valve1.setChecked(False)
        self.ui.button_toggle_valve1.setChecked(False)


    def change_single_valve(self):

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

    
    # =================================================
    # STYLE CHANGE FUNCTIONS
    # =================================================

    def set_background_color(self, widget, color):
        # Helper function to set the background color of a widget
        palette = widget.palette()
        palette.setColor(widget.backgroundRole(), color)
        widget.setPalette(palette)


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
