import time
import sys
import os
import serial
import pandas as pd
import datetime

from scipy.signal import butter, filtfilt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Communication_Functions.communication_functions import *

from PyQt5 import QtWidgets, QtCore, QtGui 
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot, QMutex, QTimer
from PyQt5.QtWidgets import QProgressBar, QMessageBox

from layout import Ui_MainWindow
from layout import PopupWindow
from layout import EndPopupWindow

from serial_connections import SerialConnections
from serial_connections import TemperatureSensorSerial
from serial_connections import ESP32Serial

from serial_workers import TempWorker
from serial_workers import ESP32SerialWorker
from serial_workers import PulseGeneratorSerialWorker

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import numpy as np

#========================
# DIRECTIONS FOR MOTORS 
#========================

DIR_M1_UP = 1
DIR_M1_DOWN = -1
DIR_M2_UP = -1
DIR_M2_DOWN = 1
DIR_M3_RIGHT = 1
DIR_M3_LEFT = -1
DIR_M4_UP = -1
DIR_M4_DOWN = 1

#==========================
# IDS FOR THE BSG2 DEVICES
#==========================
PG_PSU_VENDOR_ID = 0x6666     
PSU_PRODUCT_ID = 0x0100      
PG_PRODUCT_ID = 0x0200       
TEMPERATURE_SENSOR_VENDOR_ID = 0x0403  
TEMPERATURE_SENSOR_PRODUCT_ID = 0x6015

#========================
# MAIN GUI THREAD
#========================

class Functionality(QtWidgets.QMainWindow):
    def __init__(self):
        super(Functionality, self).__init__()
        #==============================================================================================================================================================================================================================
        # Initialize the applications widget structure creating an instance of the UI_MainWindow class that defined the application layout
        #==============================================================================================================================================================================================================================
        #region:
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #endregion
        #==============================================================================================================================================================================================================================
        # Initialize application flags 
        #==============================================================================================================================================================================================================================
        #region:
        self.flag_connections = [False, False, False, False]# These flags should be changed to true if a serial device is succesfully created AND the port is opened 

        self.temp_is_plotting = False
        self.voltage_is_plotting = False
        self.current_is_plotting = False 

        self.sucrose_is_pumping = False       
        self.ethanol_is_pumping = False 

        self.blood_is_homing= False         
        self.blood_is_jogging_down = False  
        self.blood_is_jogging_up = False    
        self.blood_is_pumping = False

        self.pressure_release_valve_open = True # the pressure release valve always at start up is open  
        self.resetting_pressure = False # in this context resetting pressure means increasing the systems pressure 

        self.flask_vertical_gantry_is_home= False  
        self.all_motors_are_home= False 
        self.flask_horizontal_gantry_is_home= False 
        self.cartrige_gantry_is_home= False 

        self.lights_are_on= False 

        self.starting_a_live_data_session = False
        self.live_data_is_logging = False
        self.live_tracking_temperature = False
        self.live_tracking_ethanol_flowrate = False 
        self.live_tracking_sucrose_flowrate = False
        self.live_tracking_pressure = False 
        self.live_tracking_current = False 
        self.live_tracking_voltage = False

        self.signal_is_enabled=False 

        self.experiment_choice_is_locked_in = False
        #endregion
        #==============================================================================================================================================================================================================================
        # Initialize display variables for line edits and plotting canvas 
        #==============================================================================================================================================================================================================================
        #region:
        self.xdata = np.linspace(0, 499, 500)   # Initialize the x data array for update_temp_plot() to update the FigureCanvas widget in the Plot Frame
        self.plotdata = np.zeros(500)           # Initialize the y data array for update_temp_plot() to update the FigureCanvas widget in the Plot Frame

        self.voltage_xdata = np.linspace(0, 499, 500)  
        self.plotdata = np.zeros(500)
        self.zerodata = [2000, 2000]
        
        self.maxval_pulse = 10  
        self.minval_pulse = -10

        self.max_temp = float('-inf')           # Initialize the max temp data for max temp QLabel in the Temperature Frame
        self.min_temp = float('inf')            # Initialize the min temp data for min temp QLabel in the Temperature Frame

        self.current_temp = 0
        
        #endregion
        #==============================================================================================================================================================================================================================
        # Start serial connections
        #==============================================================================================================================================================================================================================
        #region:
        self.device_serials= [None, None,None, None]                                # device_serials = [PSU, PG, 3PAC, temperature_sensor]
        
        esp32_RTOS_serial = ESP32Serial()
        temperature_sensor_serial = TemperatureSensorSerial(TEMPERATURE_SENSOR_VENDOR_ID, TEMPERATURE_SENSOR_PRODUCT_ID) # Create Instance of TemperatureSensorSerial Class   
        pulse_generator_serial = SerialConnections(PG_PSU_VENDOR_ID, PG_PRODUCT_ID)
        psu_serial = SerialConnections(PG_PSU_VENDOR_ID, PSU_PRODUCT_ID)
        
        self.device_serials[0] = psu_serial.establish_connection()
        self.device_serials[1] = pulse_generator_serial.establish_connection()
        self.device_serials[2] = esp32_RTOS_serial.establish_connection()        
        self.device_serials[3] = temperature_sensor_serial.establish_connection() # Create a temperature sensor serial device 

        if self.device_serials[0] is not None and self.device_serials[0].isOpen():
            self.flag_connections[0] = True
        if self.device_serials[1] is not None and self.device_serials[1].isOpen():
            self.flag_connections[1] = True
        if self.device_serials[2] is not None and self.device_serials[2].isOpen():
            self.flag_connections[2] = True
        if self.device_serials[3] is not None:
            self.flag_connections[3] = True

        #endregion
        # =====================================================================================================================================================================================================================================================================================================================================================================================================================================================================
        # Setup Temperature Sensor Worker and Thread 
        # =====================================================================================================================================================================================================================================================================================================================================================================================================================================
        #region: 
        if self.flag_connections[3]:

            self.tempWorker = TempWorker(temperature_sensor_serial) 
            self.tempThread = QThread()
            self.tempWorker.moveToThread(self.tempThread) 

            self.tempWorker.update_temp.connect(self.update_temp_data)
            self.tempWorker.update_temp.connect(self.update_temp_plot)
            self.tempWorker.update_temp.connect(self.update_temperature_labels)

            self.tempThread.started.connect(self.tempWorker.run)
            self.tempThread.start() 

        #endregion
        #===========================================================================================================================================================================================================
        # Setup ESP32 (3PAC) Worker and Thread
        #===========================================================================================================================================================================================================
        #region:
        if self.flag_connections[2]: 

            self.esp32Worker = ESP32SerialWorker(esp32_RTOS_serial)
            self.esp32Thread = QThread()
            self.esp32Worker.moveToThread(self.esp32Thread) 

            self.esp32Worker.update_flowrate.connect(self.updateEthanolProgressBar) 
            self.esp32Worker.update_flowrate.connect(self.updateSucroseProgressBar) 
            self.esp32Worker.update_pressure.connect(self.update_pressure_line_edit)
            self.esp32Worker.update_fluidic_play_pause_buttons.connect(self.update_play_pause_buttons) 

            self.esp32Thread.started.connect(self.esp32Worker.run)  
            self.esp32Thread.start() 
        #endregion
        #======================================================================================================================================================================================================================================================================================================
        # Setup Pulse Generator and Power Supply Unit Worker and Thread
        #======================================================================================================================================================================================================================================================================================================
        #region:
        if self.flag_connections[1]:

            send_PG_pulsetimes(self.device_serials[1], 0, 200, 75, 75, verbose = 0)

            self.pgWorker = PulseGeneratorSerialWorker(pulse_generator_serial)
            self.pgThread = QThread()
            self.pgWorker.moveToThread(self.pgThread)

            self.pgWorker.update_pulse.connect(self.process_pg_data)
            self.pgWorker.update_zerodata.connect(self.handleZeroDataUpdate)
            
            self.pgThread.started.connect(self.pgWorker.run)
            self.pgThread.start()  
        #endregion
        #================================================================================================================================================================================================================================
        # 0 Side bar functionality 
        #================================================================================================================================================================================================================================
        #region:        
        if self.flag_connections[2]:
            self.ui.button_lights.clicked.connect(self.skakel_ligte)
            self.ui.button_motors_home.clicked.connect(lambda: self.movement_homing(0))     
       
        self.ui.button_experiment_route.clicked.connect(self.go_to_route2)             
        self.ui.button_dashboard_route.clicked.connect(self.go_to_route1)             
        self.ui.button_dashboard_data_recording.clicked.connect(self.toggle_LDA_popup)
        #endregion
        #==============================================================================================================================================================================================================================
        # 1 Sucrose frame functionality 
        #==============================================================================================================================================================================================================================
        #region:
        if self.flag_connections[2]: 
            self.ui.button_sucrose.pressed.connect(self.start_stop_sucrose_pump)
        #endregion
        #==============================================================================================================================================================================================================================
        # 2 Ethanol frame functionality 
        #==============================================================================================================================================================================================================================
        #region:
        if self.flag_connections[2]: 
            self.ui.button_ethanol.pressed.connect(self.start_stop_ethanol_pump)  
        #endregion
        #==============================================================================================================================================================================================================================
        # 2 Pressure frame functionality 
        #==============================================================================================================================================================================================================================
        #region:
        if self.flag_connections[2]: 
            self.ui.pressure_check_button.pressed.connect(self.toggle_pressure_release_button)
            self.ui.pressure_reset_button.pressed.connect(self.start_stop_increasing_system_pressure)
        #endregion
        #===============================================================================================================================================================================================
        # 3 Blood frame functionality
        #================================================================================================================================================================================================
        #region:
        self.blood_pump_timer = None 
        if self.flag_connections[2]: 
            self.ui.button_blood_top.clicked.connect(lambda: self.movement_homing(1))                       # connect the signal to the slot 
            self.ui.button_blood_up.pressed.connect(lambda: self.movement_startjogging(1, DIR_M1_UP, False)) # connect the signal to the slot    
            self.ui.button_blood_up.released.connect(lambda: self.movement_stopjogging(1))                  # connect the signal to the slot              

            self.ui.button_blood_down.pressed.connect(lambda: self.movement_startjogging(1, DIR_M1_DOWN, False)) # connect the signal to the slot
            self.ui.button_blood_down.released.connect(lambda: self.movement_stopjogging(1))                    # connect the signal to the slot
            self.ui.button_blood_play_pause.pressed.connect(self.toggle_blood_pump)
        #endregion
        #================================================================================================================================================================================================================================
        # 11 Flask frame functionality
        #================================================================================================================================================================================================================================
        #region:   
        if self.flag_connections[2]: 
            self.ui.button_flask_bottom.clicked.connect(lambda: self.movement_homing(4))                        # connect the signal to the slot 
            self.ui.button_flask_up.pressed.connect(lambda: self.movement_startjogging(4, DIR_M4_UP, True))     # connect the signal to the slot    
            self.ui.button_flask_up.released.connect(lambda: self.movement_stopjogging(4))                      # connect the signal to the slot              
            self.ui.button_flask_down.pressed.connect(lambda: self.movement_startjogging(4, DIR_M4_DOWN, True)) # connect the signal to the slot
            self.ui.button_flask_down.released.connect(lambda: self.movement_stopjogging(4))                    # connect the signal to the slot   

        if self.flag_connections[2]:
            self.ui.button_flask_rightmost.clicked.connect(lambda: self.movement_homing(3))                           # connect the signal to the slot 
            self.ui.button_flask_right.pressed.connect(lambda: self.movement_startjogging(3, DIR_M3_RIGHT, True))     # connect the signal to the slot    
            self.ui.button_flask_right.released.connect(lambda: self.movement_stopjogging(3))                      # connect the signal to the slot              
            self.ui.button_flask_left.pressed.connect(lambda: self.movement_startjogging(3, DIR_M3_LEFT, True)) # connect the signal to the slot
            self.ui.button_flask_left.released.connect(lambda: self.movement_stopjogging(3))                    # connect the signal to the slot
        #endregion
        #================================================================================================================================================================================================================================================================
        # 6 Cartrige frame functionality
        #================================================================================================================================================================================================================================================================
        #region:
        if self.flag_connections[2]:
            self.ui.button_cartridge_bottom.clicked.connect(lambda: self.movement_homing(2))                           # connect the signal to the slot 
            self.ui.button_cartridge_up.pressed.connect(lambda: self.movement_startjogging(2, DIR_M2_UP, False))     # connect the signal to the slot    
            self.ui.button_cartridge_up.released.connect(lambda: self.movement_stopjogging(2))                      # connect the signal to the slot              
            self.ui.button_cartridge_down.pressed.connect(lambda: self.movement_startjogging(2, DIR_M2_DOWN, False)) # connect the signal to the slot
            self.ui.button_cartridge_down.released.connect(lambda: self.movement_stopjogging(2))                    # connect the signal to the slot
        #endregion
        #======================================================================================================================================================================================================================================================================================================
        # 4 Connections frame functionality
        #======================================================================================================================================================================================================================================================================
        #region:
        self.coms_timer = QtCore.QTimer()
        self.coms_timer.setInterval(10000)  # 10 seconds
        self.coms_timer.timeout.connect(self.check_coms)
        self.coms_timer.start()
        #endregion
        #======================================================================================================================================================================================================================================================================
        # 9 Signal frame functionality
        #======================================================================================================================================================================================================================================================================================================
        #region:
        if self.flag_connections[0] and self.flag_connections[1]:
            self.ui.psu_button.pressed.connect(self.start_psu_pg)
        #endregion
        #==============================================================================================================================================================================================================================
        # 5 Plotting Frame functionality (not the same as the plotting canvas)
        #==============================================================================================================================================================================================================================
        #region:     
        if self.flag_connections[0] and self.flag_connections[1]:
            self.ui.voltage_button.pressed.connect(self.start_voltage_plotting)
            self.ui.current_button.pressed.connect(self.start_current_plotting)
        if self.flag_connections[3]:            
            self.ui.temp_button.pressed.connect(self.start_stop_temp_plotting)
        #endregion
        #================================================================================================================================================================================================================================================
        # Experiment selection 
        #================================================================================================================================================================================================================================================================================================
        #region:
        self.ui.user_info_lockin_button.pressed.connect(self.lock_unlock_experiment_choice)
        #endregion
        #================================================================================================================================================================================================================================================================================================
        # Experiment page Demo Automation Functionality (im trying to use dictionaries for the first time with an easy application, so yes i could be using intergers here with no real advantage loss but i need to learn dictionaries)
        #================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
        #region:
        DEMO_frame_names = [
            "frame_DEMO_close_fluidic_circuit",
            "frame_DEMO_connect_waste_flask",
            "frame_DEMO_ethanol_flush",
            "frame_DEMO_connect_to_harvest_flask",
            "frame_DEMO_blood_sucrose_mix",
            "frame_DEMO_sample_retrieval",
            "save_experiment_data_frame"
        ]

        self.DEMO_timers = {}

        self.DEMO_counters = {frame_name: [0] for frame_name in DEMO_frame_names}

        for DEMO_frame_name in DEMO_frame_names:
            DEMO_timer = QtCore.QTimer(self)
            self.DEMO_timers[DEMO_frame_name] = DEMO_timer
            DEMO_timer.timeout.connect(
                lambda frame_name=DEMO_frame_name: 
                    self.update_experiment_step_progress_bar(
                        self.DEMO_counters[frame_name], 
                        self.DEMO_timers[frame_name], 
                        self.DEMO_progress_bar_dict[frame_name],
                        frame_name  
                    )
            )

        self.DEMO_progress_bar_dict = {
            "frame_DEMO_close_fluidic_circuit": self.ui.frame_DEMO_close_fluidic_circuit.progress_bar,
            "frame_DEMO_connect_waste_flask": self.ui.frame_DEMO_connect_waste_flask.progress_bar,
            "frame_DEMO_ethanol_flush": self.ui.frame_DEMO_ethanol_flush.progress_bar,
            "frame_DEMO_connect_to_harvest_flask": self.ui.frame_DEMO_connect_to_harvest_flask.progress_bar,
            "frame_DEMO_blood_sucrose_mix": self.ui.frame_DEMO_blood_sucrose_mix.progress_bar,
            "frame_DEMO_sample_retrieval": self.ui.frame_DEMO_sample_retrieval.progress_bar,
            "save_experiment_data_frame": self.ui.save_experiment_data_frame.progress_bar
        }

        self.DEMO_time_intervals = { 

            "frame_DEMO_close_fluidic_circuit": 5,
            "frame_DEMO_connect_waste_flask": 6,
            "frame_DEMO_ethanol_flush": 33,
            "frame_DEMO_connect_to_harvest_flask": 26,
            "frame_DEMO_blood_sucrose_mix": 67,
            "frame_DEMO_sample_retrieval": 14,
            "save_experiment_data_frame": 2
        }

        self.ui.frame_DEMO_close_fluidic_circuit.start_stop_button.pressed.connect(self.start_demo)
        self.ui.save_experiment_data_frame.reset_button.pressed.connect(self.reset_all_DEMO_progress_bars)
        #endregion
        #================================================================================================================================================================================================================================================================================================
        # Live data logging
        #================================================================================================================================================================================================================================================================================================
        #region : 
        self.last_save_time = None
        self.save_interval = 10  # seconds
        self.pulse_number = 1 
        #endregion

# region: TEMPERATURE  
    def update_temp_data(self, temp_data): 
        self.current_temp = temp_data

    def start_stop_temp_plotting(self):
        if not self.temp_is_plotting and not self.voltage_is_plotting and not self.current_is_plotting:  
            self.temp_is_plotting = True
            self.set_button_style(self.ui.temp_button)

        else:  
            self.temp_is_plotting = False
            self.reset_button_style(self.ui.temp_button)

    @pyqtSlot(float)
    def update_temp_plot(self, temperature):

        if self.temp_is_plotting:
            shift = 1
            self.plotdata = np.roll(self.plotdata, -shift)
            self.plotdata[-shift:] = temperature
            self.ydata = self.plotdata[:]

            self.xdata = np.roll(self.xdata, -shift)
            self.xdata[-1] = self.xdata[-2] + 1  # This will keep increasing the count on the x-axis

            self.ui.axes_voltage.clear()
            self.ui.axes_voltage.plot(self.xdata, self.ydata, color='#FFFFFF')
            self.ui.axes_voltage.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
            self.ui.axes_voltage.set_ylim(min(self.ydata) - 1, max(self.ydata) + 10)  # dynamically update y range

            self.set_plot_canvas('Temperature (°C)', 'Electrode Temperature')
            self.ui.canvas_voltage.draw()
    
    @pyqtSlot(float)
    def update_temperature_labels(self, temp_data):
        if temp_data > self.max_temp:
            self.max_temp = temp_data
            self.ui.max_temp_data.setText(f"{self.max_temp}°")
            
        if temp_data < self.min_temp:
            self.min_temp = temp_data
            self.ui.min_temp_data.setText(f"{self.min_temp}°")
#endregion

# region : PUMPS
    def start_stop_sucrose_pump(self):
        if not self.ethanol_is_pumping:
            if not self.sucrose_is_pumping:   
                self.close_pressure_release_valve()
                self.set_button_style(self.ui.button_sucrose)
                self.sucrose_is_pumping = True 
                try:
                    FR = float(self.ui.line_edit_sucrose.text())
                    V = float(self.ui.line_edit_sucrose_2.text())
                except ValueError:
                    print("Invalid input in line_edit_sucrose")
                    return 
                message = f'wFS-300-{FR:.2f}-{V:.1f}\n'
                print(message)  
                self.esp32Worker.write_serial_message(message)

            else: 
                self.reset_button_style(self.ui.button_sucrose)
                self.sucrose_is_pumping = False 
                message = f'wFO\n'
                self.esp32Worker.write_serial_message(message)
                self.updateSucroseProgressBar(0)
    
    def updateSucroseProgressBar(self, value):
        if self.sucrose_is_pumping:
            if value:
                value = float(value)
                # Check if the value is below zero
                if value < 0:
                    self.ui.progress_bar_sucrose.setValue(0)
                # Check if the value is greater than the maximum allowed value
                elif value > self.ui.progress_bar_sucrose.max:
                    self.ui.progress_bar_sucrose.setValue(self.ui.progress_bar_sucrose.max)
                else:
                    self.ui.progress_bar_sucrose.setValue(value)
            else:
                self.ui.progress_bar_sucrose.setValue(0)
        else: 
            self.ui.progress_bar_sucrose.setValue(0)
         
    def start_stop_ethanol_pump(self):
        if not self.sucrose_is_pumping:
            if not self.ethanol_is_pumping: 
                self.close_pressure_release_valve()
                self.ethanol_is_pumping = True  
                self.set_button_style(self.ui.button_ethanol)
                try:
                    FR = float(self.ui.line_edit_ethanol.text())
                    V = float(self.ui.line_edit_ethanol_2.text())
                except ValueError:
                    print("Invalid input in line_edit_sucrose")
                    return 
                message = f'wFE-160-{FR:.2f}-{V:.1f}\n'  
                print(message)
                self.esp32Worker.write_serial_message(message)

            else: 
                self.reset_button_style(self.ui.button_ethanol)
                self.ethanol_is_pumping = False 
                message = f'wFO\n'
                self.esp32Worker.write_serial_message(message)
                self.updateEthanolProgressBar(0)

    def updateEthanolProgressBar(self, value):
        if self.ethanol_is_pumping:
            if value:
                value = float(value)
                # Check if the value is below zero
                if value < 0:
                    self.ui.progress_bar_ethanol.setValue(0)
                # Check if the value is greater than the maximum allowed value
                elif value > self.ui.progress_bar_ethanol.max:
                    self.ui.progress_bar_ethanol.setValue(self.ui.progress_bar_ethanol.max)
                else:
                    self.ui.progress_bar_ethanol.setValue(value)
            else:
                self.ui.progress_bar_ethanol.setValue(0)
        else: self.ui.progress_bar_ethanol.setValue(0)  

    def toggle_pressure_release_button(self): 
        if self.pressure_release_valve_open: 
            self.close_pressure_release_valve()
        else: 
            self.open_pressure_release_valve()

    def open_pressure_release_valve(self):
        self.pressure_release_valve_open = True  
        self.reset_button_style(self.ui.pressure_check_button, 25)
        self.ui.pressure_check_button.setText("OPEN")
        message = f'wRL\n' 
        self.esp32Worker.write_serial_message(message)

    def close_pressure_release_valve(self):
        self.pressure_release_valve_open = False  
        self.set_button_style(self.ui.pressure_check_button, 25)
        self.ui.pressure_check_button.setText("CLOSED")
        message = f'wRH\n'
        self.esp32Worker.write_serial_message(message)

    def update_pressure_line_edit(self, value):
        if value is not None:
            self.ui.pressure_data.setText(f"{value} Bar")
    
    def start_stop_increasing_system_pressure(self):
        if not self.resetting_pressure:
            self.close_pressure_release_valve()
            self.resetting_pressure = True 
            self.set_button_style(self.ui.pressure_reset_button)
            self.ui.pressure_progress_bar.setValue(0)
            
            # Setup timer to update progress bar every second
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_pressure_progress_bar)
            self.timer.start(1000)  # 1000 milliseconds == 1 second
            self.counter = 0
            message = f'wRS\n'
            print(message)
            self.esp32Worker.write_serial_message(message)

        else: 
            self.reset_button_style(self.ui.pressure_reset_button)
            self.resetting_pressure = False
            self.timer.stop()
            self.counter = 0
            self.ui.pressure_progress_bar.setValue(0) 
            message = f'wRO\n'
            print(message)
            self.esp32Worker.write_serial_message(message)
        
    def update_pressure_progress_bar(self):
        self.counter += 1
        if self.counter <= 20 and self.resetting_pressure:
            self.ui.pressure_progress_bar.setValue(int((self.counter / 20) * 100))
        else:
            self.start_stop_increasing_system_pressure()

    def update_play_pause_buttons(self): 
        if self.ethanol_is_pumping: 
            self.start_stop_ethanol_pump()
        elif self.sucrose_is_pumping: 
            self.start_stop_sucrose_pump()
#endregion

# region : PULSE GENENRATOR AND POWER SUP 

    def handleZeroDataUpdate(self, zerodata):
        self.zerodata = zerodata

    def start_voltage_plotting(self):
        if not self.voltage_is_plotting and not self.temp_is_plotting and not self.current_is_plotting:   
            self.voltage_is_plotting = True  
            self.set_button_style(self.ui.voltage_button)       
        
        else: 
            self.voltage_is_plotting = False  
            self.reset_button_style(self.ui.voltage_button)   

    def start_current_plotting(self): 
        if not self.current_is_plotting and not self.temp_is_plotting and not self.voltage_is_plotting:  
            self.current_is_plotting = True 
            self.set_button_style(self.ui.current_button)
        else: 
            self.current_is_plotting = False 
            self.reset_button_style(self.ui.current_button)
    
    def butter_lowpass_filter(self, data, cutoff, fs, order):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, data)
        return y
    
    def moving_average(self, data, window_size):
        return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

    def process_pg_data(self, voltage_y):

        self.voltage_y = voltage_y

        self.voltage_y[:, 0] -= self.zerodata[0]           # voltage data
        self.voltage_y[:, 1] -= self.zerodata[1]           # current data  

        self.voltage_y[:, 0] *= 0.15       # Nico original guess for voltage caling 
        self.voltage_y[:, 1] *= 0.15       # Nico original guess for current scaling
        #self.voltage_y[:, 0] *= 0.456812    # Hans value for voltage scaling as calculated by Nico  
        #self.voltage_y[:, 1] *= 0.034  # Hans value fo current scaling as calculated by Nico

        # before we chop up the data to display on the UI we will save the data to csv as the Octave script potentially requires the full data set to be analyzed
        current_time = time.time()
        if self.live_data_is_logging and (self.last_save_time is None or current_time - self.last_save_time >= self.save_interval) and self.signal_is_enabled:
            self.save_data_to_csv(self.voltage_y, self.current_temp)
            self.last_save_time = current_time

        length_of_data = self.voltage_y.shape[0] 
        self.voltage_xdata = np.linspace(1, 300, length_of_data)

        # Sample rate and desired cutoff frequency of the filter
        fs = 1000.0  # Sample rate, adjust to your data
        cutoff = 40  # Desired cutoff frequency, adjust based on your data

        #self.voltage_y[:, 1] = self.butter_lowpass_filter(self.voltage_y[:, 1], cutoff, fs, order=5)

        # Apply the filter to the current data
        window_size = 10  # Adjust this based on your data
        #self.voltage_y[:, 1] = self.moving_average(self.voltage_y[:, 1], window_size)

        if self.voltage_is_plotting: 
            self.update_voltage_plot()
        
        if self.current_is_plotting: 
            self.update_current_plot() 

    def update_current_plot(self): 
        self.ui.axes_voltage.clear()
        self.ui.axes_voltage.plot(self.voltage_xdata, self.voltage_y[:, -1], color='#FFFFFF')
        self.ui.axes_voltage.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
        self.ui.axes_voltage.set_ylim(-90, 90) #+-90 are the PG voltage limits
        
        self.set_plot_canvas('Current (A)', 'Current Signal')

        self.ui.canvas_voltage.draw()

    def update_voltage_plot(self):
        
        self.ui.axes_voltage.clear()
        self.ui.axes_voltage.plot(self.voltage_xdata, self.voltage_y[:, 0], color='#FFFFFF')
        self.ui.axes_voltage.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
        self.ui.axes_voltage.set_ylim(-90, 90) #+-90 are the PG voltage limits
        
        self.set_plot_canvas('Voltage (V)', 'Voltage Signal')

        self.ui.canvas_voltage.draw()
   
    def start_psu_pg(self): 
        if not self.signal_is_enabled:  
            
            pos_setpoint_text = self.ui.line_edit_max_signal.text().strip()
            neg_setpoint_text = self.ui.line_edit_min_signal.text().strip()

            #self.ui.line_edit_max_signal.setEnabled(False)
            #self.ui.line_edit_min_signal.setEnabled(False)

            # Validate positive setpoint
            if not pos_setpoint_text:
                QMessageBox.warning(self, "Input Error", "The positive setpoint cannot be blank. Please enter a value.")
                self.ui.line_edit_max_signal.clear()
                return

            try:
                pos_setpoint = int(pos_setpoint_text)
                if not (20 <= pos_setpoint <= 90):
                    raise ValueError("Positive setpoint out of range.")
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Invalid positive setpoint. Please enter an integer between 20 and 90.")
                self.ui.line_edit_max_signal.clear()
                return

            # Validate negative setpoint
            if not neg_setpoint_text:
                QMessageBox.warning(self, "Input Error", "The negative setpoint cannot be blank. Please enter a value.")
                self.ui.line_edit_min_signal.clear()
                return

            try:
                neg_setpoint = int(neg_setpoint_text)
                if not (-90 <= neg_setpoint <= -20):
                    raise ValueError("Negative setpoint out of range.")
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Invalid negative setpoint. Please enter an integer between -90 and -20.")
                self.ui.line_edit_min_signal.clear()
                return

            print("Setpoints are valid.")

            self.set_button_style(self.ui.psu_button)
            
            self.signal_is_enabled = True

            neg_setpoint = abs(neg_setpoint)
            
            print(pos_setpoint)
            print(neg_setpoint)
            send_PSU_enable(self.device_serials[0], 1)
            time.sleep(.1)

            send_PSU_setpoints(self.device_serials[0], 20, 20, 0)
            time.sleep(.1)

            send_PSU_setpoints(self.device_serials[0], pos_setpoint, neg_setpoint, 0)


            self.pgWorker.start_pg()

        else: 
            
            self.reset_button_style(self.ui.psu_button)
            self.signal_is_enabled = False         
            
            #self.ui.line_edit_max_signal.setEnabled(True)
            #self.ui.line_edit_min_signal.setEnabled(True)

            send_PSU_disable(self.device_serials[0], 1)
            self.pgWorker.stop_pg()

#endregion

# region : BLOOD PUMP (MOTOR)

    def toggle_blood_pump(self):
        if not self.blood_is_pumping:
            self.start_blood_pump()
        else:
            self.stop_blood_pump()

    def start_blood_pump(self):  
        self.blood_is_pumping = True  
        self.set_button_style(self.ui.button_blood_play_pause)
        
        blood_volume = float(self.ui.line_edit_blood_2.text())
        blood_speed = float(self.ui.line_edit_blood.text())
       
        volume_str = f"0{blood_volume:.1f}" if blood_volume < 10 else f"{blood_volume:.1f}"
        speed_str = f"{blood_speed:.3f}"

        if speed_str[0] == "0":
            speed_str = speed_str[1:]

        message = f'wMB-{volume_str}-{speed_str}\n'
        #print(message)   
        #self.esp32Worker.write_serial_message(message)

        writeBloodSyringe(self.device_serials[2], blood_volume, blood_speed)
        
        #if self.blood_pump_timer is None:
            #self.blood_pump_timer = QTimer()
            #self.blood_pump_timer.timeout.connect(self.stop_blood_pump)
        #self.blood_pump_timer.start(blood_pump_time)  # Start the timer
            
    def stop_blood_pump(self):
        self.reset_button_style(self.ui.button_blood_play_pause)
        #if self.blood_pump_timer is not None:
            #self.blood_pump_timer.stop()  # Stop the timer
        blood_volume = float(0) 
        blood_speed = float(0)
        volume_str = f"0{blood_volume:02.1f}"  
        speed_str = f"{blood_speed:.2f}"
        message = f'wMB-{volume_str}-{speed_str}\n'
        print(message)
        self.esp32Worker.write_serial_message(message)
        self.blood_is_pumping = False

#endregion

# region : CONNECTION CIRCLE FUNCTION     
      
    def check_coms(self):

        if self.flag_connections[3]:
            self.ui.circles["Temperature Sensor"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else:
            self.ui.circles["Temperature Sensor"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")
            
        if self.flag_connections[2]:
            self.ui.circles["3PAC"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else: 
            self.ui.circles["3PAC"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")
        
        if self.flag_connections[0]:
            self.ui.circles["Pulse Generator"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else: 
            self.ui.circles["Pulse Generator"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")
        
        if self.flag_connections[1]:
            self.ui.circles["PSU"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else: 
            self.ui.circles["PSU"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")

#endregion 

# region : CHANGING PAGES 

    def go_to_route1(self):
        # This is the slot that gets called when the button is clicked
        self.ui.stack.setCurrentIndex(0)

    def go_to_route2(self):
        # This is the slot that gets called when the button is clicked
        self.ui.stack.setCurrentIndex(1)
        
#endregion 

# region : MOTOR MOVEMENTS (NOT INCLUDING BLOOD MOTOR)
    def movement_homing(self, motornumber=0):
        # motornumber = 0 --> ALL MOTORS
        if self.flag_connections[2]:
            writeMotorHoming(self.device_serials[2], motornumber)
            if motornumber == 0:
                print("HOMING STARTED FOR ALL MOTORS")
            else:
                print("HOMING STARTED FOR MOTOR {}".format(motornumber))      

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
#endregion

# region : LEDS 

    def skakel_ligte(self): 
        if not self.lights_are_on: 
            self.lights_are_on = True  
            self.set_button_style(self.ui.button_lights)

            writeLedStatus(self.device_serials[2], 1, 1, 1)
            writeLogoStatus(self.device_serials[2], 1)

        else: #Else if surcrose_is_pumping is true then it means the button was pressed during a state of pumping sucrose and the user would like to stop pumping which means we need to:
            self.lights_are_on = False 
            self.reset_button_style(self.ui.button_lights)
            writeLogoStatus(self.device_serials[2], 0)
            writeLedStatus(self.device_serials[2], 0, 0, 0)
   
#endregion

# region : DEMO

    def start_demo(self):
        self.step_two()                                             # start the automation sequence (AS)

    def step_two(self):
        if self.flag_connections[2]: 
            writeMotorDistance(self.device_serials[2], 2, 31, 2)    # connect fluidics to cartridge (move motor two down a distance 31mm)
            writeLedStatus(self.device_serials[2], 0, 1, 0)         # syringe region LED on

        frame_name = "frame_DEMO_close_fluidic_circuit"
        self.DEMO_counters[frame_name][0] = 0
        self.DEMO_timers[frame_name].start(1000)  

        QTimer.singleShot(5000, self.step_three)


    def step_three(self):
        if self.flag_connections[2]: 
            writeMotorDistance(self.device_serials[2], 4, 37, 1)    # connect waste flask to cartridge (move motor 4 up a distance 38mm)
        
        frame_name = "frame_DEMO_connect_waste_flask"
        self.DEMO_counters[frame_name][0] = 0
        self.DEMO_timers[frame_name].start(1000)    

        QTimer.singleShot(6500, self.step_four)                     # give the motor 6.5 seconds to reach its posistion before executing the next step in the AS


    def step_four(self):
        if self.flag_connections[2]: 
            self.start_ethanol_pump()                               # flush ethanol
            writeLedStatus(self.device_serials[2], 0, 0, 2)         # blink the resevoir region LED  

        frame_name = "frame_DEMO_ethanol_flush"
        self.DEMO_counters[frame_name][0] = 0
        self.DEMO_timers[frame_name].start(1000)    

        QTimer.singleShot(30000, self.step_four_part_two)           # let ethanol flush for 30 seconds 


    def step_four_part_two(self):
        if self.flag_connections[2]: 
            self.start_ethanol_pump()                               # stop ethanol 
            writeLedStatus(self.device_serials[2], 0, 0, 0)         # turn of all LEDs
        QTimer.singleShot(3000, self.step_five)                     # wait 3 seconds before proceeding to next step (can reduce this time) 

    def step_five(self):
        if self.flag_connections[2]: 
            writeMotorDistance(self.device_serials[2], 4, 37, 2)    # disconnect waste flask (move motor 4 down a distance of 37mm)
            writeLedStatus(self.device_serials[2], 1, 0, 0)         # flask region led on 

        frame_name = "frame_DEMO_connect_to_harvest_flask"
        self.DEMO_counters[frame_name][0] = 0
        self.DEMO_timers[frame_name].start(1000)    

        QTimer.singleShot(6500, self.step_five_part_two)            # give motor 4 6.5 seconds to get to its position before proceeding to the next step in the AS
    
    def step_five_part_two(self):
        if self.flag_connections[2]: 
            writeMotorDistance(self.device_serials[2], 3, 60, 1)    # connect mixing flask to cartridge (move motor three left a distance of 60mm)
        QTimer.singleShot(10000, self.step_five_part_three)         # give motor 3 10 seconds to get to its position before proceeding to the next step in the AS
    
    def step_five_part_three(self): 
        if self.flag_connections[2]: 
            writeMotorDistance(self.device_serials[2], 4, 37 , 1)   # connect mixing flask to cartridge (move motor 3 up a distance of 38mm)
        QTimer.singleShot(7000, self.step_six)                      # give motor 4 7 seconds to get to its position before proceeding to the next step in the AS
    
    def step_six(self): 
        if self.flag_connections[2]: 
            writeBloodSyringe(self.device_serials[2], 0.115, 0.125) # flush blood 
            writeLedStatus(self.device_serials[2], 0, 2, 0)         # blink syring region LED 

        frame_name = "frame_DEMO_blood_sucrose_mix"
        self.DEMO_counters[frame_name][0] = 0
        self.DEMO_timers[frame_name].start(1000)    

        QTimer.singleShot(50, self.step_six_part_two)               # wait 50ms before proceeding to the next step in the AS to allow the serial coms to complete
    
    def step_six_part_two(self): 
        if self.flag_connections[2]: 
            self.start_sucrose_pump()                               # flush sucrose (with blood running)
        QTimer.singleShot(60000, self.step_six_part_three)          # let sucrose flush with blood for 60 seconds

    def step_six_part_three(self): 
        if self.flag_connections[2]: 
            self.start_sucrose_pump()                               # stop sucrose
            writeLedStatus(self.device_serials[2], 0, 0, 0)         # turn off all LEDs
        QTimer.singleShot(7000, self.step_seven)                

    def step_seven(self): 
        if self.flag_connections[2]: 
            writeMotorDistance(self.device_serials[2], 4, 37, 2)    # disconnect mixing flask (move motor 4 down a distnace of 38 mm)
            writeLedStatus(self.device_serials[2], 1, 0, 0)         # flask region led on 

        frame_name = "frame_DEMO_sample_retrieval"
        self.DEMO_counters[frame_name][0] = 0
        self.DEMO_timers[frame_name].start(1000)   
        
        QTimer.singleShot(7000, self.step_seven_part_two)           # give motor 4 7 seconds to get to its position before proceeding to the next step in the AS

    def step_seven_part_two(self): 
        if self.flag_connections[2]: 
            writeMotorDistance(self.device_serials[2], 3, 62, 1)    # retrieve mixing flask (move motor three a distance of 62 mm left)
        QTimer.singleShot(7000, self.end_demo)                      # give motor 3 7 seconds to get to its posistion before proceeding to the next step
    
    def end_demo(self): 
        if self.flag_connections[2]: 
            writeLedStatus(self.device_serials[2], 2, 2, 2)         # blink lights to take the flask
        QTimer.singleShot(10000, self.end_demo_part_two)            # let the lights blink for 10 seconds
    
    def end_demo_part_two(self):
        if self.flag_connections[2]: 
            writeLedStatus(self.device_serials[2], 1, 0, 0)         # turn light back on 
            
#endregion

# region : LIVE DATA AQUISITION 
    def toggle_LDA_popup(self):
        if not self.starting_a_live_data_session:
            self.showLDAPopup()
        else:
            self.showEndLDAPopup()

    def showLDAPopup(self):
        self.popup = PopupWindow()
        self.popup.button_LDA_go_live.clicked.connect(self.go_live)

        self.popup.button_LDA_temperature.clicked.connect(self.toggle_LDA_temperature_button)
        self.popup.button_LDA_pressure.clicked.connect(self.toggle_LDA_pressure_button)
        self.popup.button_LDA_Sucrose.clicked.connect(self.toggle_LDA_sucrose_button)
        self.popup.button_LDA_Ethanol.clicked.connect(self.toggle_LDA_ethanol_button)
        self.popup.button_LDA_current.clicked.connect(self.toggle_LDA_current_button)
        self.popup.button_LDA_voltage.clicked.connect(self.toggle_LDA_voltage_button)
        
        self.popup.exec_()

    def showEndLDAPopup(self):
        self.endpopup = EndPopupWindow()
        self.endpopup.button_end_LDA.clicked.connect(self.end_go_live)
        self.endpopup.exec_()

    def toggle_LDA_temperature_button(self): 
        if not self.live_tracking_temperature:
            self.live_tracking_temperature = True
            self.set_button_style(self.popup.button_LDA_temperature)
        else: 
            self.live_tracking_temperature = False
            self.reset_button_style(self.popup.button_LDA_temperature)

    def toggle_LDA_current_button(self): 
        if not self.live_tracking_temperature:
            self.live_tracking_current = True
            self.set_button_style(self.popup.button_LDA_current)
        else: 
            self.live_tracking_current = False
            self.reset_button_style(self.popup.button_LDA_current)
    
    def toggle_LDA_voltage_button(self): 
        if not self.live_tracking_voltage: 
            self.live_tracking_voltage = True 
            self.set_button_style(self.popup.button_LDA_voltage)
        else: 
            self.live_tracking_voltage = False 
            self.reset_button_style(self.popup.button_LDA_voltage)
    
    def toggle_LDA_pressure_button(self): 
        if not self.live_tracking_pressure: 
            self.live_tracking_pressure = True 
            self.set_button_style(self.popup.button_LDA_pressure)
        else: 
            self.live_tracking_pressure = False 
            self.reset_button_style(self.popup.button_LDA_pressure)

    def toggle_LDA_ethanol_button(self): 
        if not self.live_tracking_ethanol_flowrate: 
            self.live_tracking_ethanol_flowrate = True 
            self.set_button_style(self.popup.button_LDA_Ethanol)
        else: 
            self.live_tracking_ethanol_flowrate = False
            self.reset_button_style(self.popup.button_LDA_Ethanol)

    def toggle_LDA_sucrose_button(self): 
        if not self.live_tracking_sucrose_flowrate: 
            self.live_tracking_sucrose_flowrate = True 
            self.set_button_style(self.popup.button_LDA_Sucrose)
        else: 
            self.live_tracking_sucrose_flowrate = False
            self.reset_button_style(self.popup.button_LDA_Sucrose)

    def go_live(self):
        border_style = "#centralwidget { border: 7px solid green; }"
        self.live_data_is_logging = True
        self.ui.centralwidget.setStyleSheet(border_style)
        self.starting_a_live_data_session = True
        print("Going live and starting data saving...")
    
    def end_go_live(self):
        border_style = "#centralwidget { border: 0px solid green; }"
        self.live_data_is_logging = False
        self.ui.centralwidget.setStyleSheet(border_style)
        self.starting_a_live_data_session = False
        self.starting_a_live_data_session = False
        self.live_data_is_logging = False
        self.live_tracking_temperature = False
        self.live_tracking_ethanol_flowrate = False 
        self.live_tracking_sucrose_flowrate = False
        self.live_tracking_pressure = False 
        self.live_tracking_current = False 
        self.live_tracking_voltage = False
        self.pulse_number = 1
        print("Ending live data saving...")

    def save_data_to_csv(self, y_data, temp_data):
        # Construct the file name based on the current date and time
        current_time = datetime.datetime.now()
        filename = current_time.strftime("%Y%m%d_%H%M%S") + "_experiment_data.csv"

        # Define the directory where the file will be saved
        save_directory = r"C:\Users\BSG2_UI\OneDrive\Desktop\Experiments"  # Use raw string for Windows paths
        full_path = os.path.join(save_directory, filename)
        
        # Create a DataFrame for the header information
        header_info = [
                f"Date: {current_time.strftime("%Y-%m-%d %H:%M:%S")}",
                f"#Pulse Number: {self.pulse_number}",
                f"#Voltage Pos: {self.ui.line_edit_max_signal.text()}",
                f"#Voltage Neg: {self.ui.line_edit_min_signal.text()}",
                f"Temperature: {temp_data}",
                "#Pulse Length: 75,00",
                "#Transistor on time: 75",
                "#Rate: 200"
            ]
        

        # Calculate the pulse number (assuming the method is called every 10 seconds)
        self.pulse_number = self.pulse_number + 1

        header_df = pd.DataFrame({'Column1': header_info,'Column2': ['']*len(header_info)})

        # Create a DataFrame for the data
        voltage_data_df = pd.DataFrame({'Column1': y_data[:, 0]})
        current_data_df = pd.DataFrame({'Column2': y_data[:, 1] })

        combined_pg_data_df = pd.concat([voltage_data_df, current_data_df], axis=1)
        combined_output_df = pd.concat([header_df, combined_pg_data_df], ignore_index=True)


        # Save to CSV
        combined_output_df.to_csv(full_path, index=False, header=False)
        print(f"Saving experiment data to {filename}...")

#endregion 

# region : GENERIC UI ELEMENT UPDATES 
    
    def set_plot_canvas(self, x_title: str, y_title: str):
        # Get the Axes object from the Figure for voltage plot
        self.ui.axes_voltage.grid(True, color='#808080', linestyle='--')
        self.ui.axes_voltage.set_facecolor('#222222')
        self.ui.axes_voltage.spines['bottom'].set_color('#FFFFFF')
        self.ui.axes_voltage.spines['top'].set_color('#FFFFFF')
        self.ui.axes_voltage.spines['right'].set_color('#FFFFFF')
        self.ui.axes_voltage.spines['left'].set_color('#FFFFFF')
        self.ui.axes_voltage.tick_params(colors='#FFFFFF')
        
        # Increase the font size of the x-axis and y-axis labels
        self.ui.axes_voltage.tick_params(axis='x', labelsize=14)  # You can adjust the font size (e.g., 12)
        self.ui.axes_voltage.tick_params(axis='y', labelsize=14)  # You can adjust the font size (e.g., 12)
        
        # Move the y-axis ticks and labels to the right
        self.ui.axes_voltage.yaxis.tick_right()
        
        # Adjust the position of the x-axis label
        self.ui.axes_voltage.xaxis.set_label_coords(0.5, -0.1)  # Move the x-axis label downwards

        # Adjust the position of the y-axis label to the left
        self.ui.axes_voltage.yaxis.set_label_coords(-0.05, 0.5)  # Move the y-axis label to the left

        # Set static labels
        self.ui.axes_voltage.set_xlabel('Time (us)', color='#FFFFFF',  fontsize=15)
        self.ui.axes_voltage.set_ylabel(x_title, color='#FFFFFF',  fontsize=15)
        self.ui.axes_voltage.set_title(y_title, color='#FFFFFF',fontsize=20, fontweight='bold', y=1.05)
        
    def set_button_style(self, button, font_size=30):
        button.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid white;
                border-radius: 10px;
                background-color: #0796FF;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: {font_size}px;
            }}

            QPushButton:hover {{
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }}
        """)

    def reset_button_style(self, button, font_size=30):
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
    
    def update_experiment_step_progress_bar(self, counter, timer, progress_bar, frame_name):
        interval = self.DEMO_time_intervals[frame_name]
        
        counter[0] += 1
        if counter[0] <= interval:
            progress_bar.setValue(int((counter[0] / interval) * 100))
        else:
            timer.stop()
            counter[0] = 0

    def reset_all_DEMO_progress_bars(self):
        for progress_bar in self.DEMO_progress_bar_dict.values():
            progress_bar.setValue(0)   

    def lock_unlock_experiment_choice(self): 
        if not self.experiment_choice_is_locked_in: 
            self.experiment_choice_is_locked_in=True
            self.set_button_style(self.ui.user_info_lockin_button)
            self.ui.application_combobox.setEnabled(False)

            if self.ui.application_combobox.currentText() == "POCII":
                self.create_POCII_experiment_page()
                pass
            elif self.ui.application_combobox.currentText() == "Ethanol to Sucrose Flush":
                # Do something for Ethanol to Sucrose Flush
                pass
            elif self.ui.application_combobox.currentText() == "CG2 QC":
                # Do something for CG2 QC
                pass
            elif self.ui.application_combobox.currentText() == "Autotune":
                # Do something for Autotune
                pass
            elif self.ui.application_combobox.currentText() == "Demonstration":
                self.create_DEMO_experiment_page()
                pass

        else: 
            self.experiment_choice_is_locked_in = False
            self.reset_button_style(self.ui.user_info_lockin_button)
            self.ui.application_combobox.setEnabled(True)

            if self.ui.application_combobox.currentText() == "POCII":
                self.destroy_POCII_experiment_page()
                pass
            elif self.ui.application_combobox.currentText() == "Ethanol to Sucrose Flush":
                # Do something for Ethanol to Sucrose Flush
                pass
            elif self.ui.application_combobox.currentText() == "CG2 QC":
                # Do something for CG2 QC
                pass
            elif self.ui.application_combobox.currentText() == "Autotune":
                # Do something for Autotune
                pass
            elif self.ui.application_combobox.currentText() == "Demonstration":
                self.destroy_DEMO_experiment_page()
                pass

    def create_POCII_experiment_page(self):
        self.ui.frame_POCII_system_sterilaty.show()
        self.ui.frame_POCII_decontaminate_cartridge.show()
        self.ui.high_voltage_frame.show()
        self.ui.flush_out_frame.show()
        self.ui.zero_volt_frame.show()
        self.ui.safe_disconnect_frame.show()
        self.ui.save_experiment_data_frame.show()

        self.ui.spacing_placeholder1.show()
        self.ui.spacing_placeholder2.show()
        self.ui.spacing_placeholder3.show()
        self.ui.spacing_placeholder4.show()
        self.ui.spacing_placeholder5.show()
        self.ui.spacing_placeholder6.show()
    
    def destroy_POCII_experiment_page(self): 

        self.ui.frame_POCII_system_sterilaty.hide()
        self.ui.frame_POCII_decontaminate_cartridge.hide()
        self.ui.high_voltage_frame.hide()
        self.ui.flush_out_frame.hide()
        self.ui.zero_volt_frame.hide()
        self.ui.safe_disconnect_frame.hide()
        self.ui.save_experiment_data_frame.hide()

        self.ui.spacing_placeholder1.hide()
        self.ui.spacing_placeholder2.hide()
        self.ui.spacing_placeholder3.hide()
        self.ui.spacing_placeholder4.hide()
        self.ui.spacing_placeholder5.hide()
        self.ui.spacing_placeholder6.hide()
   
    def create_DEMO_experiment_page(self):

        self.ui.frame_DEMO_close_fluidic_circuit.show()
        self.ui.frame_DEMO_connect_waste_flask.show()
        self.ui.frame_DEMO_ethanol_flush.show()
        self.ui.frame_DEMO_connect_to_harvest_flask.show()
        self.ui.frame_DEMO_blood_sucrose_mix.show()
        self.ui.frame_DEMO_sample_retrieval.show()
        self.ui.save_experiment_data_frame.show()


        self.ui.spacing_placeholder7.show()
        self.ui.spacing_placeholder8.show()
        self.ui.spacing_placeholder9.show()
        self.ui.spacing_placeholder10.show()
        self.ui.spacing_placeholder11.show()
        self.ui.spacing_placeholder12.show()
    
    def destroy_DEMO_experiment_page(self): 

        self.ui.frame_DEMO_close_fluidic_circuit.hide()
        self.ui.frame_DEMO_connect_waste_flask.hide()
        self.ui.frame_DEMO_ethanol_flush.hide()
        self.ui.frame_DEMO_connect_to_harvest_flask.hide()
        self.ui.frame_DEMO_blood_sucrose_mix.hide()
        self.ui.frame_DEMO_sample_retrieval.hide()
        self.ui.save_experiment_data_frame.hide()

        self.ui.spacing_placeholder7.hide()
        self.ui.spacing_placeholder8.hide()
        self.ui.spacing_placeholder9.hide()
        self.ui.spacing_placeholder10.hide()
        self.ui.spacing_placeholder11.hide()
        self.ui.spacing_placeholder12.hide()

#endregion

