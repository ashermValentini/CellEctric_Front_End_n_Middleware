import time
import sys
import os
import serial
import pandas as pd
from datetime import datetime  # This allows you to use datetime.now()

from scipy.signal import butter, filtfilt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Communication_Functions.communication_functions import *

from PyQt5 import QtWidgets, QtCore, QtGui 
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot, QMutex, QTimer, QDateTime
from PyQt5.QtWidgets import QProgressBar, QMessageBox

import application_style
import device_IDs
import pocii

from layout import Ui_MainWindow
from layout import PopupWindow
from layout import EndPopupWindow
from layout import SyringeSettingsPopupWindow

from data_saving_workers import DataSavingWorker

from serial_connections import SerialConnections
from serial_connections import TemperatureSensorSerial
from serial_connections import ESP32Serial
from serial_connections import SerialDeviceBySerialNumber

from serial_workers import TempWorker
from serial_workers import ESP32SerialWorker
from serial_workers import PulseGeneratorSerialWorker
from serial_workers import PeristalticDriverWorker

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import numpy as np

#================================================
# DIRECTIONS FOR MOTORS 
#================================================

DIR_M1_UP = 1
DIR_M1_DOWN = -1
DIR_M2_UP = -1
DIR_M2_DOWN = 1
DIR_M3_RIGHT = 1
DIR_M3_LEFT = 2
DIR_M4_UP = 2
DIR_M4_DOWN = 1

#================================================
# MOTOR NUMBERS 
#================================================

FLASK_MOTOR = 3
PIERCE_MOTOR = 4
BLOOD_SYRINGE = 1 
FLUIDICS_MOTOR = 2

#========================
# MAIN GUI THREAD
#========================

class Functionality(QtWidgets.QMainWindow):
    #========================================================
    # Signals 
    #========================================================
    #region: 
    stopTimer = pyqtSignal()  # Signal to request the timer to stop (needed when stopping timers running in a different thread)
    #endregion
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
        self.flag_connections = [False, False, False, False, False]# These flags should be changed to true if a serial device is succesfully created AND the port is opened 

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

        #flags to control system functionality if the motors have not been homed and to control the states of the homing buttons for the motors
        self.flask_vertical_gantry_is_home= False  
        self.all_motors_are_home= False 
        self.flask_horizontal_gantry_is_home= False 
        self.cartrige_gantry_is_home= False 

        #flag to control the lights button on the side bar
        self.lights_are_on= False 

        #flags for live data saving outside of a worklow
        self.live_data_saving_button_pressed = False

        self.flag_live_data_saving_applied = False
        self.live_data_is_logging = False
        self.live_tracking_temperature = False
        self.live_tracking_ethanol_flowrate = False 
        self.live_tracking_sucrose_flowrate = False
        self.live_tracking_pressure = False 
        self.live_tracking_current = False 
        self.live_tracking_voltage = False
        
        #flag to control the pulse generator button
        self.signal_is_enabled=False 

        #flags for live data saving outside of a worklow
        self.experiment_choice_is_locked_in = False

        self.flag_workflow_live_data_saving_applied = False
        self.workflow_live_data_is_logging = False
        self.workflow_live_tracking_temperature = False
        self.workflow_live_tracking_ethanol_flowrate = False 
        self.workflow_live_tracking_sucrose_flowrate = False
        self.workflow_live_tracking_pressure = False 
        self.workflow_live_tracking_current = False 
        self.workflow_live_tracking_voltage = False

        #flags for POCII WF
        self.POCII_is_running = False

        # turn this flag true if pressure tracking needed in the future
        self.pressure_data_needed = False

        # temperature controller
        self.temperature_control_is_running = False

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
        self.device_serials= [None, None,None, None, None]                                # device_serials = [PSU, PG, 3PAC, temperature_sensor]
        
        esp32_RTOS_serial = ESP32Serial()
        temperature_sensor_serial = TemperatureSensorSerial(device_IDs.TEMPERATURE_SENSOR_VENDOR_ID, device_IDs.TEMPERATURE_SENSOR_PRODUCT_ID) # Create Instance of TemperatureSensorSerial Class   
        pulse_generator_serial = SerialConnections(device_IDs.PG_PSU_VENDOR_ID, device_IDs.PG_PRODUCT_ID)
        psu_serial = SerialConnections(device_IDs.PG_PSU_VENDOR_ID, device_IDs.PSU_PRODUCT_ID)
        peristaltic_driver_serial = SerialDeviceBySerialNumber(device_IDs.PERISTALTIC_DRIVER_SERIAL_NUMBERS)
        
        self.device_serials[0] = psu_serial.establish_connection()
        self.device_serials[1] = pulse_generator_serial.establish_connection()
        self.device_serials[2] = esp32_RTOS_serial.establish_connection()        
        self.device_serials[3] = temperature_sensor_serial.establish_connection() 
        self.device_serials[4] = peristaltic_driver_serial.establish_connection(baud_rate = 115200)

        if self.device_serials[0] is not None and self.device_serials[0].isOpen():
            self.flag_connections[0] = True
        if self.device_serials[1] is not None and self.device_serials[1].isOpen():
            self.flag_connections[1] = True
        if self.device_serials[2] is not None and self.device_serials[2].isOpen():
            self.flag_connections[2] = True
        if self.device_serials[3] is not None:
            self.flag_connections[3] = True
        if self.device_serials[4] is not None and self.device_serials[4].isOpen():
            self.flag_connections[4] = True

        #endregion
        #==============================================================================================================================================================================================================================
        # Setup Data: Saving, Workers, and Threads
        #==============================================================================================================================================================================================================================
        #region:
        self.liveDataWorker = DataSavingWorker()
        self.liveDataThread = QThread()
        self.liveDataWorker.moveToThread(self.liveDataThread)
        self.liveDataThread.start()

        self.stopTimer.connect(self.liveDataWorker._stop_timer)

        #data saving initation for current and voltage which is different to non pg data since the bio team is using octave for the time being
        self.last_save_time = None
        self.save_interval = 10  
        self.pulse_number = 1 
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
            self.tempWorker.update_temp.connect(self.liveDataWorker.update_temp_data)

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
            self.esp32Worker.update_flowrate.connect(self.liveDataWorker.update_sucrose_flowrate_data)
            self.esp32Worker.update_flowrate.connect(self.liveDataWorker.update_ethanol_flowrate_data)
            
            if self.pressure_data_needed: 
                self.esp32Worker.update_pressure.connect(self.update_pressure_line_edit)
                self.esp32Worker.update_pressure.connect(self.liveDataWorker.update_pressure_data)

            self.esp32Thread.started.connect(self.esp32Worker.run)  
            self.esp32Thread.start() 
        #endregion
        #===========================================================================================================================================================================================================
        # Setup Peristaltic Driver Worker and Thread
        #===========================================================================================================================================================================================================
        #region:
        if self.flag_connections[4]: 
            self.peristalticDriverWorker = PeristalticDriverWorker(peristaltic_driver_serial)
            self.peristalticDriverThread = QThread()
            self.peristalticDriverWorker.moveToThread(self.peristalticDriverThread) 

            self.peristalticDriverWorker.stop_sucrose.connect(self.stop_sucrose_pump)
            self.peristalticDriverWorker.stop_ethanol.connect(self.stop_ethanol_pump)

            self.peristalticDriverThread.started.connect(self.peristalticDriverWorker.run)  
            self.peristalticDriverThread.start() 
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
            self.ui.button_motors_home.clicked.connect(lambda: self.movement_homing(0))     
            self.ui.button_motors_home.clicked.connect(self.enable_motor_buttons)
            #self.ui.button_lights.clicked.connect(self.skakel_ligte) #lights are telve volts not five so we must order new lights  

        self.ui.button_experiment_route.clicked.connect(self.go_to_route2)             
        self.ui.button_dashboard_route.clicked.connect(self.go_to_route1)             
        self.ui.button_dashboard_data_recording.clicked.connect(self.toggle_LDA_popup)
        #endregion
        #==============================================================================================================================================================================================================================
        # 1 Sucrose frame functionality 
        #==============================================================================================================================================================================================================================
        #region:
        if self.flag_connections[2] or self.flag_connections[4]: 
            self.ui.button_sucrose.pressed.connect(self.toggle_sucrose_button)
        #endregion
        #==============================================================================================================================================================================================================================
        # 2 Ethanol frame functionality 
        #==============================================================================================================================================================================================================================
        #region:
        if self.flag_connections[2] or self.flag_connections[4]: 
            self.ui.button_ethanol.pressed.connect(self.toggle_ethanol_pump)  
        #endregion
        #==============================================================================================================================================================================================================================
        # 1 Temperature frame 
        #==============================================================================================================================================================================================================================
        #region:
        self.coolingTimer = None
        self.threshold_temperature = 34 
        if self.flag_connections[3]:
            self.ui.temp_control_button.pressed.connect(self.toggle_cooling)
            #self.ui.temp_control_button.pressed.connect(lambda: self.warning_dialogue("Attention", "Cooling unavailable on your base station"))
        #endregion
        #==============================================================================================================================================================================================================================
        # 2 Pressure frame functionality 
        #==============================================================================================================================================================================================================================
        #region:
        #if self.flag_connections[2]: 
            #self.ui.pressure_check_button.pressed.connect(self.toggle_pressure_release_button)
            #self.ui.pressure_reset_button.pressed.connect(self.start_stop_increasing_system_pressure)
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
        
        self.ui.button_blood_down.setEnabled(False)
        self.ui.button_blood_up.setEnabled(False)
        self.ui.button_blood_play_pause.setEnabled(False)

        self.ui.blood_gear.clicked.connect(self.show_blood_pump_settings)
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
        
        self.ui.button_flask_up.setEnabled(False)
        self.ui.button_flask_down.setEnabled(False)
        self.ui.button_flask_right.setEnabled(False)
        self.ui.button_flask_left.setEnabled(False)
        #endregion
        #================================================================================================================================================================================================================================================================
        # 6 Fludic frame functionality
        #================================================================================================================================================================================================================================================================
        #region:
        if self.flag_connections[2]:
            self.ui.button_cartridge_bottom.clicked.connect(lambda: self.movement_homing(2))                           # connect the signal to the slot 
            self.ui.button_cartridge_up.pressed.connect(lambda: self.movement_startjogging(2, DIR_M2_UP, False))     # connect the signal to the slot    
            self.ui.button_cartridge_up.released.connect(lambda: self.movement_stopjogging(2))                      # connect the signal to the slot              
            self.ui.button_cartridge_down.pressed.connect(lambda: self.movement_startjogging(2, DIR_M2_DOWN, False)) # connect the signal to the slot
            self.ui.button_cartridge_down.released.connect(lambda: self.movement_stopjogging(2))                    # connect the signal to the slot
        
        self.ui.button_cartridge_up.setEnabled(False)
        self.ui.button_cartridge_down.setEnabled(False)
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
            self.ui.psu_button.pressed.connect(self.toggle_PSU_PG_signal_button)
        
        self.ui.line_edit_min_signal.setReadOnly(True)                                              #negative value should not be able to be edited
        self.ui.line_edit_max_signal.textChanged.connect(self.line_edit_min_signal_text_changed)    #updates to the positive signal value must be reflected in the negative line edit

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
        self.ui.user_info_lockin_button.pressed.connect(self.toggle_LDA_workflow_popup)
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
        #endregion
        #================================================================================================================================================================================================================================================================================================
        # Experiment page POCII Automation Functionality (im trying to use dictionaries for the first time with an easy application, so yes i could be using intergers here with no real advantage loss but i need to learn dictionaries)
        #================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
        #region:
        POCII_frame_names = [
            "frame_POCII_system_sterilaty",
            "frame_POCII_decontaminate_cartridge",
            "high_voltage_frame",
            "flush_out_frame",
            "zero_volt_frame",
            "safe_disconnect_frame"
        ]

        self.POCII_timers = {}
        self.POCII_time_intervals = { 

            "frame_POCII_system_sterilaty": 192,
            "frame_POCII_decontaminate_cartridge": 1046,
            "high_voltage_frame": 342,
            "flush_out_frame": 672,
            "zero_volt_frame": 344,
            "safe_disconnect_frame": 312,
        }
        self.POCII_counters = {frame_name: [0] for frame_name in POCII_frame_names}

        for POCII_frame_name in POCII_frame_names:
            POCII_timer = QtCore.QTimer(self)
            self.POCII_timers[POCII_frame_name] = POCII_timer
            POCII_timer.timeout.connect(
                lambda frame_name=POCII_frame_name: 
                    self.update_experiment_step_progress_bar(
                        self.POCII_counters[frame_name], 
                        self.POCII_timers[frame_name], 
                        self.POCII_progress_bar_dict[frame_name],
                        frame_name  
                    )
            )

        self.POCII_progress_bar_dict = {
            "frame_POCII_system_sterilaty": self.ui.frame_POCII_system_sterilaty.progress_bar,
            "frame_POCII_decontaminate_cartridge": self.ui.frame_POCII_decontaminate_cartridge.progress_bar,
            "high_voltage_frame": self.ui.high_voltage_frame.progress_bar,
            "flush_out_frame": self.ui.flush_out_frame.progress_bar,
            "zero_volt_frame": self.ui.zero_volt_frame.progress_bar,
            "safe_disconnect_frame": self.ui.safe_disconnect_frame.progress_bar
        }



        self.current_session_token = None

        self.ui.frame_POCII_system_sterilaty.start_stop_button.pressed.connect(self.toggle_system_sterilaty_start_stop_button)
        self.ui.frame_POCII_decontaminate_cartridge.start_stop_button.pressed.connect(self.toggle_decontamination_start_stop_button)
        self.ui.high_voltage_frame.start_stop_button.pressed.connect(self.toggle_WF_HV_start_stop_button)
        self.ui.flush_out_frame.start_stop_button.pressed.connect(self.toggle_flush_out_start_stop_button)
        self.ui.zero_volt_frame.start_stop_button.pressed.connect(self.toggle_WF_0V_start_stop_button)
        self.ui.safe_disconnect_frame.start_stop_button.pressed.connect(self.toggle_safe_disconnect_start_stop_button)
        
        self.ui.frame_POCII_system_sterilaty.reset_button.pressed.connect(lambda: self.reset_frame_progress_bar(self.ui.frame_POCII_system_sterilaty.progress_bar))
        self.ui.frame_POCII_decontaminate_cartridge.reset_button.pressed.connect(lambda: self.reset_frame_progress_bar(self.ui.frame_POCII_decontaminate_cartridge.progress_bar))
        self.ui.high_voltage_frame.reset_button.pressed.connect(lambda: self.reset_frame_progress_bar(self.ui.high_voltage_frame.progress_bar))
        self.ui.flush_out_frame.reset_button.pressed.connect(lambda: self.reset_frame_progress_bar(self.ui.flush_out_frame.progress_bar))
        self.ui.zero_volt_frame.reset_button.pressed.connect(lambda: self.reset_frame_progress_bar(self.ui.zero_volt_frame.progress_bar))
        self.ui.safe_disconnect_frame.reset_button.pressed.connect(lambda: self.reset_frame_progress_bar(self.ui.safe_disconnect_frame.progress_bar))

        #endregion
        #just for now so that i dont have to home the motors every single fucking time 
        #self.enable_motor_buttons()

# region : TEMPERATURE  
    def update_temp_data(self, temp_data): 
        self.current_temp = temp_data

    def start_stop_temp_plotting(self):
        if not self.temp_is_plotting and not self.voltage_is_plotting and not self.current_is_plotting:  
            self.temp_is_plotting = True
            self.set_button_style(self.ui.temp_button)
        elif not self.temp_is_plotting and (self.voltage_is_plotting or self.current_is_plotting):
            self.voltage_is_plotting = False 
            self.current_is_plotting = False
            self.reset_button_style(self.ui.current_button)
            self.reset_button_style(self.ui.voltage_button)
            self.temp_is_plotting = True 
            self.set_button_style(self.ui.temp_button)
        else:  
            self.temp_is_plotting = False
            self.reset_button_style(self.ui.temp_button)

    @pyqtSlot(float)
    def update_temp_plot(self, temperature):
        shift = 1
        self.plotdata = np.roll(self.plotdata, -shift)
        self.plotdata[-shift:] = temperature
        self.ydata = self.plotdata[:]

        self.xdata = np.roll(self.xdata, -shift)
        self.xdata[-1] = self.xdata[-2] + 1  # This will keep increasing the count on the x-axis
        
        if self.temp_is_plotting:
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
            if(self.max_temp>30 and self.max_temp<35):
                self.ui.max_temp_data.setStyleSheet(application_style.medium_temperature_number_style)
            elif(self.max_temp>35): 
                self.ui.max_temp_data.setStyleSheet(application_style.high_temperature_number_style)

            self.ui.max_temp_data.setText(f"{self.max_temp}°")
    
        self.ui.current_temp_data.setText(f"{self.current_temp}°")

    def toggle_cooling(self): 
        if self.temperature_control_is_running: 
            self.stop_temperature_control()
            self.temperature_control_is_running = False
            self.reset_button_style(self.ui.temp_control_button)
        else: 
            self.start_temperature_control() 
            self.temperature_control_is_running = True
            self.set_button_style(self.ui.temp_control_button)
    
    def start_temperature_control(self): 
        self.coolingTimer = QTimer(self)
        self.coolingTimer.timeout.connect(self.check_and_control_temperature)
        self.coolingTimer.start(500)  # Check every 1000 milliseconds (1 second)

        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("cooling started", folder_name)
        
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("cooling started", folder_name)

    def stop_temperature_control(self): 
        if self.coolingTimer:
            self.coolingTimer.stop()
            self.coolingTimer.deleteLater()
            self.coolingTimer = None
            message = "wCS-0\n"
            self.esp32Worker.write_serial_message(message)

        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("cooling stopped", folder_name)
        
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("cooling stopped", folder_name)

    def check_and_control_temperature(self):
        if self.current_temp > self.threshold_temperature:
            message = "wCS-1\n"
        else:
            message = "wCS-0\n"

        self.esp32Worker.write_serial_message(message)

        
#endregion

# region : SUCROSE PUMP

    def toggle_sucrose_button(self): 
        if not self.ethanol_is_pumping: 
            if not self.sucrose_is_pumping: 
                self.start_sucrose_pump(self.ui.line_edit_sucrose.text(), self.ui.line_edit_sucrose_2.text() )
            else: 
                self.stop_sucrose_pump()

    def start_sucrose_pump(self, FR, V): 
        #self.close_pressure_release_valve()
        self.set_button_style(self.ui.button_sucrose)
        self.sucrose_is_pumping = True                      # GUI flag 
        self.liveDataWorker.set_sucrose_is_running(True)    # Data saving thread flag
        try:
            FR = float(FR)
            V = float(V)
        except ValueError:
            print("Invalid input in line_edit_sucrose")
            return 
        message3PAC = f'wFS-410-{FR:.2f}-{V:.1f}\n'
        messagePeristalticDriver = f'sB-{FR}-{V}-0.171\n'
        self.esp32Worker.write_serial_message(message3PAC)
        self.peristalticDriverWorker.write_serial_message(messagePeristalticDriver)

        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Sucrose pump started", folder_name)
        
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Sucrose pump started", folder_name)

    def stop_sucrose_pump(self): 
        self.reset_button_style(self.ui.button_sucrose)
        self.sucrose_is_pumping = False 
        self.liveDataWorker.set_sucrose_is_running(False) # Data saving thread flag
        message3PAC = f'wFO\n'
        messagePeristalticDriver = f'o\n'
        self.esp32Worker.write_serial_message(message3PAC)
        self.peristalticDriverWorker.write_serial_message(messagePeristalticDriver)
        self.updateSucroseProgressBar(0)

        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Sucrose pump stopped", folder_name)
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Sucrose pump stopped", folder_name)
        if self.POCII_is_running: 
            self.log_event("Sucrose pump stopped")

#endregion

# region : ETHANOL PUMP
    
    def toggle_ethanol_pump(self): 
        if not self.sucrose_is_pumping:
            if not self.ethanol_is_pumping: 
                self.start_ethanol_pump(self.ui.line_edit_ethanol.text(), self.ui.line_edit_ethanol_2.text())
            else: 
                self.stop_ethanol_pump()
    
    def start_ethanol_pump(self, FR, V): 
        #self.close_pressure_release_valve()
        self.ethanol_is_pumping = True  # GUI flag 
        self.liveDataWorker.set_ethanol_is_running(True) # Live data saving flag
        self.set_button_style(self.ui.button_ethanol)
        try:
            FR = float(FR)
            V = float(V)
        except ValueError:
            print("Invalid input in line_edit_sucrose")
            return 
        #message3PAC = f'wFE-175-{FR:.2f}-{V:.1f}\n'  
        message3PAC = f'wFE-400-{FR:.2f}-{V:.1f}\n'  
        messagePeristalticDriver = f'sE-{FR}-{V}-0.169\n'  
        self.esp32Worker.write_serial_message(message3PAC)
        self.peristalticDriverWorker.write_serial_message(messagePeristalticDriver)

        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Ethanol pump started", folder_name)
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Ethanol pump started", folder_name)
  
    def stop_ethanol_pump(self): 
        self.reset_button_style(self.ui.button_ethanol)
        self.ethanol_is_pumping = False 
        self.liveDataWorker.set_ethanol_is_running(False) # Live data saving flag
        message3PAC = f'wFO\n'
        messagePeristalticDriver = f'o\n'
        self.esp32Worker.write_serial_message(message3PAC)
        self.peristalticDriverWorker.write_serial_message(messagePeristalticDriver)
        self.updateEthanolProgressBar(0)
        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Ethanol pump stopped", folder_name)
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Ethanol pump stopped", folder_name)
        if self.POCII_is_running: 
            self.log_event("Ethanol pump stopped")

#endregion

# region : BLOOD PUMP 

    def toggle_blood_pump(self):
        if self.check_inputs(self.ui.line_edit_blood, self.ui.line_edit_blood_2):
            if not self.blood_is_pumping:
                self.start_blood_pump(self.ui.line_edit_blood.text(), self.ui.line_edit_blood_2.text())
            else:
                self.stop_blood_pump()
        else: 
            self.warning_dialogue("Warning", "Either volume or flowrate is not an acceptable input")
    
    def start_blood_pump(self, FR, V):  
        self.blood_is_pumping = True  
        self.set_button_style(self.ui.button_blood_play_pause)
        
        blood_volume = float(V)
        blood_speed = float(FR)
        syringe_diameter = float(self.ui.syringeSettingsPopup.combobox_options.currentText())

        message = f'wMB-{blood_volume}-{blood_speed}-{syringe_diameter}\n'
        self.esp32Worker.write_serial_message(message)
        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Blood pump started", folder_name)
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Blood pump started", folder_name)

        blood_pump_time = int((blood_volume / blood_speed) * 60 * 1000)

        self.blood_pump_timer = QTimer()
        self.blood_pump_timer.timeout.connect(self.stop_blood_pump)
        self.blood_pump_timer.start(blood_pump_time)  
            
    def stop_blood_pump(self):
        self.reset_button_style(self.ui.button_blood_play_pause)
        if self.blood_pump_timer: 
            self.blood_pump_timer.stop()  
        blood_volume = float(0) 
        blood_speed = float(0)
        volume_str = f"0{blood_volume:02.1f}"  
        speed_str = f"{blood_speed:.2f}"
        message = f'wMB-{volume_str}-{speed_str}\n'
        print(message)
        self.esp32Worker.write_serial_message(message)
        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Blood pump stopped", folder_name)
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Blood pump stopped", folder_name)
        self.blood_is_pumping = False
        if self.POCII_is_running: 
            self.log_event("Blood syringe pump stopped")

    def check_inputs(self, input_1, input_2):
        return input_1.hasAcceptableInput() and input_2.hasAcceptableInput()
        #return self.line_edit_blood.hasAcceptableInput() and self.line_edit_blood_2.hasAcceptableInput()

#endregion

# region : PULSE GENENRATOR AND POWER SUPPLY 
    def line_edit_min_signal_text_changed(self, text):
        neg_text = "-" + text
        self.ui.line_edit_min_signal.setText(neg_text)

    def handleZeroDataUpdate(self, zerodata):
        self.zerodata = zerodata

    def start_voltage_plotting(self):
        if not self.voltage_is_plotting and not self.temp_is_plotting and not self.current_is_plotting:   
            self.voltage_is_plotting = True  
            self.set_button_style(self.ui.voltage_button)       
        elif not self.voltage_is_plotting and (self.temp_is_plotting or self.current_is_plotting):
            self.temp_is_plotting = False 
            self.current_is_plotting = False
            self.reset_button_style(self.ui.current_button)
            self.reset_button_style(self.ui.temp_button)
            self.voltage_is_plotting = True 
            self.set_button_style(self.ui.voltage_button)
        else: 
            self.voltage_is_plotting = False  
            self.reset_button_style(self.ui.voltage_button)   

    def start_current_plotting(self): 
        if not self.current_is_plotting and not self.temp_is_plotting and not self.voltage_is_plotting:  
            self.current_is_plotting = True 
            self.set_button_style(self.ui.current_button)
        elif not self.current_is_plotting and (self.temp_is_plotting or self.voltage_is_plotting):
            self.temp_is_plotting = False 
            self.voltage_is_plotting = False
            self.reset_button_style(self.ui.voltage_button)
            self.reset_button_style(self.ui.temp_button)
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
        self.voltage_y[:, 0] *= 0.15        # Nico original guess for voltage scaling 
        self.voltage_y[:, 1] *= 0.034       # Hans value fo current scaling as calculated by Nico

        # before we chop up the data to display on the UI we will save the data to csv as the Octave script potentially requires the full data set to be analyzed
        current_time = time.time()
        # saving data for live data sessions 
        if self.live_data_is_logging and (self.last_save_time is None or current_time - self.last_save_time >= self.save_interval) and self.signal_is_enabled:
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_pg_data_to_csv(self.voltage_y, self.ui.line_edit_max_signal.text(), self.ui.line_edit_min_signal.text(), self.current_temp, self.pulse_number, folder_name)
            self.last_save_time = current_time
        
        if self.workflow_live_data_is_logging and (self.last_save_time is None or current_time - self.last_save_time >= self.save_interval) and self.signal_is_enabled:
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_pg_data_to_csv(self.voltage_y, self.ui.line_edit_max_signal.text(), self.ui.line_edit_min_signal.text(), self.current_temp, self.pulse_number, folder_name)
            self.last_save_time = current_time

        length_of_data = self.voltage_y.shape[0] 
        self.voltage_xdata = np.linspace(1, 300, length_of_data)

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

    def toggle_PSU_PG_signal_button(self): 

        if not self.signal_is_enabled: 
            if not self.live_data_is_logging:
                if not self.warning_dialogue("Warning", "You are not saving data. Click okay to proceed. Click Cancel to abort."):
                    return  # Exit the method if the user clicks Cancel
            self.start_psu_pg()
        else: 
            self.stop_psu_pg()

    def start_psu_pg(self):

        pos_setpoint_text = self.ui.line_edit_max_signal.text().strip()
        neg_setpoint_text = self.ui.line_edit_min_signal.text().strip()

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
        message = "Enabled PSU"
        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log(message, folder_name)
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log(message, folder_name)
  
        time.sleep(.1)

        send_PSU_setpoints(self.device_serials[0], 20, 20, 0)
        time.sleep(.1)

        send_PSU_setpoints(self.device_serials[0], pos_setpoint, neg_setpoint, 0)
        message = "Sent PSU setpoints"
        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log(message, folder_name)
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log(message, folder_name)

        self.pgWorker.start_pg()
        message = "Started PG"
        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log(message, folder_name)
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log(message, folder_name)

    def stop_psu_pg(self):
        self.reset_button_style(self.ui.psu_button)
        self.signal_is_enabled = False         
        
        send_PSU_disable(self.device_serials[0], 1)
        message = "Disabled PSU"
        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log(message, folder_name)
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log(message, folder_name)

        self.pgWorker.stop_pg()
        message = "Stopped PG"
        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log(message, folder_name)
        if self.workflow_live_data_is_logging: 
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log(message, folder_name)
#endregion

# region : CONNECTION CIRCLE FUNCTION     
      
    def check_coms(self):

        if self.flag_connections[3]:
            self.ui.circles["Temperature Sensor"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else:
            self.ui.circles["Temperature Sensor"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")
            
        if self.flag_connections[2]:
            self.ui.circles["Flow Rate Sensor"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
            self.ui.circles["Motors"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else: 
            self.ui.circles["Flow Rate Sensor"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")
            self.ui.circles["Motors"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")
        
        if self.flag_connections[0]:
            self.ui.circles["Pulse Generator"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else: 
            self.ui.circles["Pulse Generator"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")
        
        if self.flag_connections[1]:
            self.ui.circles["PSU"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else: 
            self.ui.circles["PSU"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")
        
        if self.flag_connections[4]:
            self.ui.circles["Pumps"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else: 
            self.ui.circles["Pumps"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")

#endregion 

# region : MOTOR (MOVEMENT FUNCTIONS DO NOT INCLUDE BLOOD MOTOR) NOTE: use the esp worker to send motor commands not the comminication file
    def enable_motor_buttons(self): 
        self.ui.button_blood_down.setEnabled(True)
        self.ui.button_blood_up.setEnabled(True)
        self.ui.button_blood_play_pause.setEnabled(True)
        self.ui.button_flask_up.setEnabled(True)
        self.ui.button_flask_down.setEnabled(True)
        self.ui.button_flask_right.setEnabled(True)
        self.ui.button_flask_left.setEnabled(True)
        self.ui.button_cartridge_up.setEnabled(True)
        self.ui.button_cartridge_down.setEnabled(True)
        self.reset_button_style(self.ui.button_blood_up)
        self.reset_button_style(self.ui.button_blood_down)
        self.reset_button_style(self.ui.button_blood_play_pause)
        self.reset_button_style(self.ui.button_flask_down)
        self.reset_button_style(self.ui.button_flask_up)
        self.reset_button_style(self.ui.button_flask_left)
        self.reset_button_style(self.ui.button_flask_right)
        self.reset_button_style(self.ui.button_cartridge_down)
        self.reset_button_style(self.ui.button_cartridge_up)
    
    def movement_homing(self, motornumber=0):
        # motornumber = 0 --> ALL MOTORS
        if self.flag_connections[2]:
            writeMotorHoming(self.device_serials[2], motornumber)
            message = f'wMH-{motornumber}\n'
            if self.live_data_is_logging: 
                folder_name = self.popup.line_edit_LDA_folder_name.text()
                self.liveDataWorker.save_activity_log(message, folder_name)

            if motornumber == 0:
                print("HOMING STARTED FOR ALL MOTORS")
            else:
                print("HOMING STARTED FOR MOTOR {}".format(motornumber))      

    def movement_startjogging(self, motornumber, direction, fast):
        if self.flag_connections[2]:
            if direction < 0:
                direction = 2
            if fast:
                speed = 1
            else:
                speed = 0
            
            writeMotorJog(self.device_serials[2], motornumber, direction, fast)
            message = f'wMJ-{motornumber}-{direction}-{speed}\n'   
            if self.live_data_is_logging: 
                folder_name = self.popup.line_edit_LDA_folder_name.text()
                self.liveDataWorker.save_activity_log(message, folder_name)

            print("TRYING TO START JOGGING: motor: {}; direction: {}; fast: {}".format(motornumber, direction, fast))

    def movement_stopjogging(self, motornumber):
        if self.flag_connections[2]:
            writeMotorJog(self.device_serials[2], motornumber, 0, 0)
            message = f'wMJ-{motornumber}-{0}-{0}\n'   
            if self.live_data_is_logging: 
                folder_name = self.popup.line_edit_LDA_folder_name.text()
                self.liveDataWorker.save_activity_log(message, folder_name)
            print("TRYING TO STOP JOGGING: motor: {}".format(motornumber))  
#endregion

# region : LIGHTS 
    def skakel_ligte(self): 
        if not self.lights_are_on: 
            self.lights_are_on = True  
            self.set_button_style(self.ui.button_lights)

            writeLedStatus(self.device_serials[2], 1, 1, 1)

        else: #Else if surcrose_is_pumping is true then it means the button was pressed during a state of pumping sucrose and the user would like to stop pumping which means we need to:
            self.lights_are_on = False 
            self.reset_button_style(self.ui.button_lights)
            writeLedStatus(self.device_serials[2], 0, 0, 0)
#endregion

# region : LIVE DATA AQUISITION OUTSIDE OF AUTOMATED WORKFLOW 
    def toggle_LDA_popup(self):
        if self.workflow_live_data_is_logging: 
            self.warning_dialogue("Attention", "You are currently in a worfklow. Please end worfklow before starting live data saving session")
        else: 
            if not self.live_data_saving_button_pressed:
                self.show_LDA_popup()
            else:
                self.show_end_LDA_popup()

    def show_LDA_popup(self):
        self.popup = PopupWindow(title="Live Data Aquisition", description="Live data aquisition will allow you to save work done outside of traditional workflows. Please populate the fields below and save your changes before going live.")
        self.popup.button_LDA_go_live.clicked.connect(self.go_live)
        self.popup.button_LDA_apply.clicked.connect(self.toggle_LDA_apply)
        self.popup.button_LDA_go_live.clicked.connect(self.popup.close)
        self.popup.button_LDA_temperature.clicked.connect(self.toggle_LDA_temperature_button)
        self.popup.button_LDA_pressure.clicked.connect(self.toggle_LDA_pressure_button)
        self.popup.button_LDA_Sucrose.clicked.connect(self.toggle_LDA_sucrose_button)
        self.popup.button_LDA_Ethanol.clicked.connect(self.toggle_LDA_ethanol_button)
        self.popup.button_LDA_current.clicked.connect(self.toggle_LDA_current_button)
        self.popup.button_LDA_voltage.clicked.connect(self.toggle_LDA_voltage_button)
        
        self.popup.exec_()

    def show_end_LDA_popup(self):
        self.endpopup = EndPopupWindow()
        self.endpopup.button_end_LDA.clicked.connect(self.end_go_live)
        self.endpopup.button_end_LDA.clicked.connect(self.endpopup.close)
        self.endpopup.exec_()

    def toggle_LDA_temperature_button(self): 
        if not self.live_tracking_temperature:
            self.live_tracking_temperature = True   # GUI thread flag
            self.liveDataWorker.set_save_temp(True) # Data saving thread flag
            self.set_button_style(self.popup.button_LDA_temperature)
        else: 
            self.live_tracking_temperature = False  # GUI thread flag 
            self.liveDataWorker.set_save_temp(False) # Data saving thread flag
            self.reset_button_style(self.popup.button_LDA_temperature)

    def toggle_LDA_current_button(self): 
        if not self.live_tracking_current:
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
            self.liveDataWorker.set_save_pressure(True)
            self.set_button_style(self.popup.button_LDA_pressure)
        else: 
            self.live_tracking_pressure = False 
            self.liveDataWorker.set_save_pressure(False)
            self.reset_button_style(self.popup.button_LDA_pressure)

    def toggle_LDA_ethanol_button(self): 
        if not self.live_tracking_ethanol_flowrate: 
            self.live_tracking_ethanol_flowrate = True 
            self.liveDataWorker.set_save_ethanol_flowrate(True)
            self.set_button_style(self.popup.button_LDA_Ethanol)
        else: 
            self.live_tracking_ethanol_flowrate = False
            self.liveDataWorker.set_save_ethanol_flowrate(False)
            self.reset_button_style(self.popup.button_LDA_Ethanol)

    def toggle_LDA_sucrose_button(self): 
        if not self.live_tracking_sucrose_flowrate: 
            self.live_tracking_sucrose_flowrate = True 
            self.liveDataWorker.set_save_sucrose_flowrate(True)
            self.set_button_style(self.popup.button_LDA_Sucrose)
        else: 
            self.live_tracking_sucrose_flowrate = False
            self.liveDataWorker.set_save_sucrose_flowrate(False)
            self.reset_button_style(self.popup.button_LDA_Sucrose)

    def go_live(self):
        self.live_data_is_logging = True                            # GUI thread flag once go live has been pressed
        self.live_data_saving_button_pressed = True                 # GUI thread flag for the side bar button being pressed
        self.liveDataWorker.start_saving_live_non_pg_data(True)     # Live data saving thread flag
        border_style = "#centralwidget { border: 7px solid green; }"
        self.ui.centralwidget.setStyleSheet(border_style)
        print("Going live and starting data saving...")
        folder_name = self.popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_activity_log("Live data saving session started", folder_name)

    def end_go_live(self):
        border_style = "#centralwidget { border: 0px solid green; }"
        self.ui.centralwidget.setStyleSheet(border_style)

        header_values = {
            "Name": self.popup.combobox_LDA_user_name.currentText(),
            "Email": self.popup.combobox_LDA_user_email.currentText(),
            "Purpose": self.popup.line_edit_LDA_experiment_purpose.text(), 
            "ID": self.popup.line_edit_LDA_experiment_number.text(),  
            "Strain Name": self.popup.combobox_LDA_strain.currentText(),
            "Fresh Sucrose": self.popup.combobox_LDA_fresh_sucrose.currentText()
        }

        folder_name = self.popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_header_info_to_csv(header_values, folder_name)
        self.liveDataWorker.save_non_pg_data_to_csv(folder_name)

        self.live_data_is_logging = False
        self.liveDataWorker.start_saving_live_non_pg_data(False)
        self.live_data_saving_button_pressed = False
        self.live_tracking_temperature = False
        self.live_tracking_ethanol_flowrate = False 
        self.live_tracking_sucrose_flowrate = False
        self.live_tracking_pressure = False 
        self.live_tracking_current = False 
        self.live_tracking_voltage = False
        self.pulse_number = 1
        self.flag_live_data_saving_applied = False

        print("Ending live data saving...")
        self.liveDataWorker.save_activity_log("Live data saving session stopped", folder_name)
    
    def toggle_LDA_apply(self): 
        if not self.flag_live_data_saving_applied:
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            folder_created = self.liveDataWorker.create_live_data_folder(folder_name)
            if folder_created:    
                self.flag_live_data_saving_applied = True
                self.set_button_style(self.popup.button_LDA_apply, 23)
                self.popup.button_LDA_go_live.setEnabled(True)
                self.reset_button_style(self.popup.button_LDA_go_live, 23)
            else: 
                self.flag_live_data_saving_applied = False
                self.reset_button_style(self.popup.button_LDA_apply, 23)
                self.grey_out_button(self.popup.button_LDA_go_live, 23)
                self.popup.button_LDA_go_live.setEnabled(False)
                self.showFolderExistsDialog()
        else: 
            self.flag_live_data_saving_applied = False
            self.reset_button_style(self.popup.button_LDA_apply, 23)
            self.popup.button_LDA_go_live.setEnabled(False)
            self.grey_out_button(self.popup.button_LDA_go_live, 23)
    
    def showFolderExistsDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("The folder already exists. Please try a different name.")
        msgBox.setWindowTitle("Folder Exists")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()
#endregion 
            
# region : LIVE DATA AQUISITION INSIDE OF AN AUTOMATED WORKFLOW    
    def toggle_LDA_workflow_popup(self): 
        if self.live_data_is_logging: 
            self.warning_dialogue("Attention", "You are currently tracking data outside of a workflow. Please end your live data aquisition session before starting your workflow session")
        else: 
            if not self.experiment_choice_is_locked_in: 
                self.show_LDA_workflow_popup()
            else: 
                self.experiment_choice_is_locked_in = False
                self.show_end_LDA_workflow_popup()

    def lock_experiment_choice(self): 
        self.set_button_style(self.ui.user_info_lockin_button)
        self.ui.application_combobox.setEnabled(False)

        if self.ui.application_combobox.currentText() == "POCII":
            self.create_POCII_experiment_page()
            self.show_activity_logger()
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

    def unlock_experiment_choice(self): 
        self.reset_button_style(self.ui.user_info_lockin_button)
        self.ui.application_combobox.setEnabled(True)

        if self.ui.application_combobox.currentText() == "POCII":
            self.destroy_POCII_experiment_page()
            self.hide_activity_logger()
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
 
    def show_LDA_workflow_popup(self):
        self.workflow_LDA_popup = PopupWindow(title="Workflow Live Data Aquisition", description="Workflow Live data aquisition will allow you to save work done inside of traditional workflows. Please populate the fields below and save your changes before going live.")
        self.workflow_LDA_popup.button_LDA_go_live.clicked.connect(self.workflow_go_live)
        self.workflow_LDA_popup.button_LDA_apply.clicked.connect(self.toggle_LDA_workflow_apply)
        self.workflow_LDA_popup.button_LDA_go_live.clicked.connect(self.workflow_LDA_popup.close)
        self.workflow_LDA_popup.button_LDA_temperature.clicked.connect(self.toggle_LDA_workflow_temperature_button)
        self.workflow_LDA_popup.button_LDA_pressure.clicked.connect(self.toggle_LDA_workflow_pressure_button)
        self.workflow_LDA_popup.button_LDA_Sucrose.clicked.connect(self.toggle_LDA_workflow_sucrose_button)
        self.workflow_LDA_popup.button_LDA_Ethanol.clicked.connect(self.toggle_LDA_workflow_ethanol_button)
        self.workflow_LDA_popup.button_LDA_current.clicked.connect(self.toggle_LDA_workflow_current_button)
        self.workflow_LDA_popup.button_LDA_voltage.clicked.connect(self.toggle_LDA_workflow_voltage_button)
        
        self.workflow_LDA_popup.exec_()

    def show_end_LDA_workflow_popup(self):
        self.workflow_endpopup = EndPopupWindow()
        self.workflow_endpopup.button_end_LDA.clicked.connect(self.workflow_end_go_live)
        self.workflow_endpopup.button_end_LDA.clicked.connect(self.workflow_endpopup.close)
        self.workflow_endpopup.exec_()
    
    def toggle_LDA_workflow_temperature_button(self): 
        if not self.workflow_live_tracking_temperature:
            self.workflow_live_tracking_temperature = True   # GUI thread flag
            self.liveDataWorker.set_save_temp(True) # Data saving thread flag commneting this out here and only activating it when the HV is applied
            self.set_button_style(self.workflow_LDA_popup.button_LDA_temperature)
        else: 
            self.workflow_live_tracking_temperature = False  # GUI thread flag 
            self.liveDataWorker.set_save_temp(False) # Data saving thread flag
            self.reset_button_style(self.workflow_LDA_popup.button_LDA_temperature)

    def toggle_LDA_workflow_current_button(self): 
        if not self.workflow_live_tracking_current:
            self.workflow_live_tracking_current = True
            self.set_button_style(self.workflow_LDA_popup.button_LDA_current)
        else: 
            self.workflow_live_tracking_current = False
            self.reset_button_style(self.workflow_LDA_popup.button_LDA_current)
    
    def toggle_LDA_workflow_voltage_button(self): 
        if not self.workflow_live_tracking_voltage: 
            self.workflow_live_tracking_voltage = True 
            self.set_button_style(self.workflow_LDA_popup.button_LDA_voltage)
        else: 
            self.workflow_live_tracking_voltage = False 
            self.reset_button_style(self.workflow_LDA_popup.button_LDA_voltage)
    
    def toggle_LDA_workflow_pressure_button(self): 
        if not self.workflow_live_tracking_pressure: 
            self.workflow_live_tracking_pressure = True 
            self.liveDataWorker.set_save_pressure(True)
            self.set_button_style(self.workflow_LDA_popup.button_LDA_pressure)
        else: 
            self.workflow_live_tracking_pressure = False 
            self.liveDataWorker.set_save_pressure(False)
            self.reset_button_style(self.workflow_LDA_popup.button_LDA_pressure)

    def toggle_LDA_workflow_ethanol_button(self): 
        if not self.workflow_live_tracking_ethanol_flowrate: 
            self.workflow_live_tracking_ethanol_flowrate = True 
            self.liveDataWorker.set_save_ethanol_flowrate(True)
            self.set_button_style(self.workflow_LDA_popup.button_LDA_Ethanol)
        else: 
            self.workflow_live_tracking_ethanol_flowrate = False
            self.liveDataWorker.set_save_ethanol_flowrate(False)
            self.reset_button_style(self.workflow_LDA_popup.button_LDA_Ethanol)

    def toggle_LDA_workflow_sucrose_button(self): 
        if not self.workflow_live_tracking_sucrose_flowrate: 
            self.workflow_live_tracking_sucrose_flowrate = True 
            self.liveDataWorker.set_save_sucrose_flowrate(True)
            self.set_button_style(self.workflow_LDA_popup.button_LDA_Sucrose)
        else: 
            self.workflow_live_tracking_sucrose_flowrate = False
            self.liveDataWorker.set_save_sucrose_flowrate(False)
            self.reset_button_style(self.workflow_LDA_popup.button_LDA_Sucrose)
    
    def workflow_go_live(self):
        self.workflow_live_data_is_logging = True                            # GUI thread flag once go live has been pressed
        self.experiment_choice_is_locked_in = True                   # GUI thread flag for the side bar button being pressed
        border_style = "#centralwidget { border: 7px solid blue; }"
        self.ui.centralwidget.setStyleSheet(border_style)
        self.lock_experiment_choice()
        print("Going live and starting data saving...")
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_activity_log("POCII workflows started", folder_name)

    def workflow_end_go_live(self):
        border_style = "#centralwidget { border: 0px solid green; }"
        self.ui.centralwidget.setStyleSheet(border_style)
        self.unlock_experiment_choice()

        header_values = {
            "Name": self.workflow_LDA_popup.combobox_LDA_user_name.currentText(),
            "Email": self.workflow_LDA_popup.combobox_LDA_user_email.currentText(),
            "Purpose": self.workflow_LDA_popup.line_edit_LDA_experiment_purpose.text(), 
            "ID": self.workflow_LDA_popup.line_edit_LDA_experiment_number.text(),  
            "Strain Name": self.workflow_LDA_popup.combobox_LDA_strain.currentText(),
            "Fresh Sucrose": self.workflow_LDA_popup.combobox_LDA_fresh_sucrose.currentText()
        }

        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_header_info_to_csv(header_values, folder_name)
        self.liveDataWorker.save_non_pg_data_to_csv(folder_name)

        self.workflow_live_data_is_logging = False
        self.liveDataWorker.start_saving_live_non_pg_data(False)
        self.live_data_saving_button_pressed = False
        self.workflow_live_tracking_temperature = False
        self.workflow_live_tracking_ethanol_flowrate = False 
        self.workflow_live_tracking_sucrose_flowrate = False
        self.workflow_live_tracking_pressure = False 
        self.workflow_live_tracking_current = False 
        self.workflow_live_tracking_voltage = False
        self.pulse_number = 1
        self.flag_workflow_live_data_saving_applied = False
        print("Ending live data saving...")

        self.liveDataWorker.save_activity_log("POCII workflows stopped", folder_name)
        self.clear_log()

    def toggle_LDA_workflow_apply(self): 
        if not self.flag_workflow_live_data_saving_applied:
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            folder_created = self.liveDataWorker.create_live_data_folder(folder_name)
            if folder_created: 
                    self.flag_workflow_live_data_saving_applied = True
                    self.set_button_style(self.workflow_LDA_popup.button_LDA_apply, 23)
                    self.reset_button_style(self.workflow_LDA_popup.button_LDA_go_live, 23)
                    self.workflow_LDA_popup.button_LDA_go_live.setEnabled(True)
            else: 
                self.flag_workflow_live_data_saving_applied = False
                self.reset_button_style(self.workflow_LDA_popup.button_LDA_apply, 23)
                self.grey_out_button(self.workflow_LDA_popup.button_LDA_go_live, 23)
                self.workflow_LDA_popup.button_LDA_go_live.setEnabled(False)
                self.showFolderExistsDialog()
        else: 
            self.flag_workflow_live_data_saving_applied = False
            self.reset_button_style(self.workflow_LDA_popup.button_LDA_apply, 23)
            self.grey_out_button(self.workflow_LDA_popup.button_LDA_go_live, 23)
            self.workflow_LDA_popup.button_LDA_go_live.setEnabled(False)

# endregion

# region : BLOOD PUMP SETTINGS 
    def show_blood_pump_settings(self):
        self.ui.syringeSettingsPopup.show()
#endregion

# region : UI ELEMENT UPDATES 
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

    def grey_out_button(self, button, font_size =30): 
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

    def reset_all_DEMO_progress_bars(self):
        for progress_bar in self.DEMO_progress_bar_dict.values():
            progress_bar.setValue(0)   
 
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

    def warning_dialogue(self, title="Default Title", description="Default Description"):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(description)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result = msgBox.exec_()  # This will show the dialog and wait for the user to press a button.
        return result == QMessageBox.Ok
#endregion

# region : CHANGING PAGES 

    def go_to_route1(self):
        self.ui.stack.setCurrentIndex(0)

    def go_to_route2(self):
        self.ui.stack.setCurrentIndex(1)
        
#endregion 

# region : POCII
    # region : SYSTEM STERILATY 
    def toggle_system_sterilaty_start_stop_button(self): 
        if self.POCII_is_running: 
            self.stop_interrupt_WF_system_sterilaty()
            self.POCII_is_running = False
        else: 
            self.WF_start_system_sterility()
            self.set_button_style(self.ui.frame_POCII_system_sterilaty.start_stop_button)
            self.POCII_is_running = True

    def WF_start_system_sterility(self): 
        #session token 
        self.generate_new_token()
        current_token = self.current_session_token
        #save and display activity
        self.log_event("SYSTEM STERILATY SUB EVENT STARTED")
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_activity_log("System sterilaty sub event started", folder_name)
        #session time
        FR_ethanol_1 = 10   # [ml/min]
        V_ethanol_1 = 5     # [ml]
        delay_1 = (V_ethanol_1/FR_ethanol_1) * 60 * 1000
        delay_1_int = int(round(delay_1)) + 2000
        FR_sucrose_1 = 10   # [ml/min]   
        V_sucrose_1 = 9     # [ml]
        delay_2 = (V_sucrose_1/FR_sucrose_1) * 60 * 1000
        delay_2_int = int(round(delay_2)) + 2000
        FR_sucrose_2 = 10   # [ml/min]              
        V_sucrose_2 = 5     # [ml]
        instruction_delay_1 = 10000
        delay_3 = (V_sucrose_2/FR_sucrose_2) * 60 * 1000
        delay_3_int = int(round(delay_3)) + 2000
        instruction_delay_2 = 10000
        FR_ethanol_2 = 10   # [ml/min]  
        V_ethanol_2 = 8     # [ml]
        delay_4 = (V_ethanol_2/FR_ethanol_2) * 60 * 1000
        delay_4_int = int(round(delay_4)) + 2000
        #operations 
        QTimer.singleShot(1, lambda: self.WF_start_ethanol_pump(FR_ethanol_1, V_ethanol_1, current_token))
        QTimer.singleShot(delay_1_int, lambda: self.WF_start_sucrose_pump(FR_sucrose_1, V_sucrose_1, current_token))
        QTimer.singleShot(delay_1_int+delay_2_int, lambda: self.WF_announcement("INSTRUCTION: MANUAL SWITCH TO STERILATY FALCON", current_token))
        QTimer.singleShot(delay_1_int+delay_2_int+instruction_delay_1, lambda: self.WF_start_sucrose_pump(FR_sucrose_2, V_sucrose_2, current_token))
        QTimer.singleShot(delay_1_int+delay_2_int+instruction_delay_1+delay_3_int, lambda: self.WF_announcement("INSTRUCTION: MANUAL SWITCH TO WASTE FALCON", current_token))
        QTimer.singleShot(delay_1_int+delay_2_int+instruction_delay_1+delay_3_int+instruction_delay_2, lambda: self.WF_start_ethanol_pump(FR_ethanol_2, V_ethanol_2, current_token))
        QTimer.singleShot(delay_1_int+delay_2_int+instruction_delay_1+delay_3_int+instruction_delay_2 + delay_4_int + 2000, lambda: self.stop_timed_WF_system_sterilaty(current_token))
        #progress bar 
        frame_name = "frame_POCII_system_sterilaty"
        self.POCII_counters[frame_name][0] = 0
        self.POCII_timers[frame_name].start(1000)  

    def stop_interrupt_WF_system_sterilaty(self): 
        #null the session
        self.current_session_token = None  
        #shut down operations 
        self.reset_button_style(self.ui.frame_POCII_system_sterilaty.start_stop_button)
        self.stop_sucrose_pump()
        self.stop_ethanol_pump()
        self.stop_motors(0, 0)
        #log events 
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.log_event("SYSTEM STERILATY SUB EVENT STOPPED MANUALLY")
        self.liveDataWorker.save_activity_log("System sterilaty sub event stopped manually", folder_name)
        #pause progress bar 
        frame_name = "frame_POCII_system_sterilaty"
        self.POCII_counters[frame_name][0] = 0
        self.POCII_timers[frame_name].stop()

    def stop_timed_WF_system_sterilaty(self, token): 
        if self.POCII_is_running and token == self.current_session_token: 
            self.reset_button_style(self.ui.frame_POCII_system_sterilaty.start_stop_button)
            self.POCII_is_running = False
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.log_event("SYSTEM STERILATY SUB EVENT COMPLETED")
            self.liveDataWorker.save_activity_log("System sterilaty sub event completed", folder_name)
        else:
            pass
#endregion

    # region : DECONTAMINATION
    def toggle_decontamination_start_stop_button(self): 
        if self.POCII_is_running: 
            self.stop_interrupt_WF_decontamination()
            self.POCII_is_running = False
        else: 
            self.WF_start_decontamination()
            self.POCII_is_running = True
            self.set_button_style(self.ui.frame_POCII_decontaminate_cartridge.start_stop_button)

    def stop_interrupt_WF_decontamination(self): 
        #null the session
        self.current_session_token = None  
        #shut down operations 
        self.reset_button_style(self.ui.frame_POCII_decontaminate_cartridge.start_stop_button)
        self.stop_sucrose_pump()
        self.stop_ethanol_pump()
        self.stop_motors(0, 0)
        #log events 
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.log_event("DECONTAMINATION SUB EVENT STOPPED MANUALLY")
        self.liveDataWorker.save_activity_log("Decontamination sub event stopped manually", folder_name)
        #pause progress bar 
        frame_name = "frame_POCII_decontaminate_cartridge"
        self.POCII_counters[frame_name][0] = 0
        self.POCII_timers[frame_name].stop()

    def WF_start_decontamination(self): 
        #session token 
        self.generate_new_token()
        current_token = self.current_session_token
        #save and display activity
        self.log_event("DECONTAMINATION SUB EVENT STARTED")
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_activity_log("Decontamination sub event started", folder_name)
        #session times
        fluid_delay_1 = (pocii.V[1]/pocii.FR[1]) * 60 * 1000 
        fluid_delay_1_int = int(round(fluid_delay_1)) + 2000 
        fluid_delay_2 = (pocii.V[0]/pocii.FR[1]) * 60 * 1000
        fluid_delay_2_int = int(round(fluid_delay_2)) + 2000
        fluid_delay_3 = (pocii.V[1]/pocii.FR[1]) * 60 * 1000
        fluid_delay_3_int = int(round(fluid_delay_3)) + 2000
        fluid_delay_4 = (pocii.V[0]/pocii.FR[1]) * 60 * 1000
        fluid_delay_4_int = int(round(fluid_delay_4)) + 2000
        #operations:
        QTimer.singleShot(1, lambda: self.WF_move_motor(3, pocii.WASTE_FLASK, current_token)) # move to waste flask 
        QTimer.singleShot(24000, lambda: self.WF_move_motor(4, pocii.PIERCE, current_token)) # pierce waste flask
        QTimer.singleShot(24000 + pocii.PIERCE_T, lambda: self.WF_start_ethanol_pump(pocii.FR[1], pocii.V[1], current_token)) #req 96 : ethanol-2.5ml/mn-10ml (10ml = total volume in tubing and cartridge)
        QTimer.singleShot(24000 + pocii.PIERCE_T + fluid_delay_1_int, lambda: self.WF_announcement("Five minute ethanol soak", current_token)) #req 99 : 5 minute soak in ethanol 
        QTimer.singleShot(24000 + pocii.PIERCE_T + pocii.SOAK_T + fluid_delay_1_int, lambda: self.WF_start_ethanol_pump(pocii.FR[1], pocii.V[0], current_token)) #req 100: ethanol-2.5ml/mn-5ml 
        QTimer.singleShot(24000 + pocii.PIERCE_T + pocii.SOAK_T + fluid_delay_1_int + fluid_delay_2_int, lambda: self.WF_start_sucrose_pump(pocii.FR[1], pocii.V[1], current_token)) #req 101 : sucrose-2.5ml/mn-10ml (10ml = total volume in tubing cartridge) 
        QTimer.singleShot(24000 + pocii.PIERCE_T + pocii.SOAK_T + fluid_delay_1_int + fluid_delay_2_int + fluid_delay_3_int + pocii.DRIP_T, lambda: self.WF_move_motor(4, pocii.DEPIERCE, current_token)) # depierce 
        QTimer.singleShot(24000 + pocii.PIERCE_T + pocii.SOAK_T + fluid_delay_1_int + fluid_delay_2_int + fluid_delay_3_int + pocii.DRIP_T + pocii.PIERCE_T, lambda: self.WF_move_motor(3, pocii.DECONTAMINATION_CONTROL, current_token)) # move to decontamination control  
        QTimer.singleShot(24000 + pocii.PIERCE_T + pocii.SOAK_T + fluid_delay_1_int + fluid_delay_2_int + fluid_delay_3_int + pocii.DRIP_T + pocii.PIERCE_T + 10000, lambda: self.WF_move_motor(4, pocii.PIERCE, current_token)) # pierce 
        QTimer.singleShot(24000 + pocii.PIERCE_T + pocii.SOAK_T + fluid_delay_1_int + fluid_delay_2_int + fluid_delay_3_int + pocii.DRIP_T + pocii.PIERCE_T + 10000 + pocii.PIERCE_T, lambda: self.WF_start_sucrose_pump(pocii.FR[1], pocii.V[0], current_token)) #req 102 : sucrose-2.5ml/min-5ml          
        QTimer.singleShot(24000 + pocii.PIERCE_T + pocii.SOAK_T + fluid_delay_1_int + fluid_delay_2_int + fluid_delay_3_int + pocii.DRIP_T + pocii.PIERCE_T + 10000 + pocii.PIERCE_T + fluid_delay_4_int + pocii.DRIP_T, lambda: self.WF_move_motor(4, pocii.DEPIERCE, current_token)) # depierce 
        QTimer.singleShot(24000 + pocii.PIERCE_T + pocii.SOAK_T + fluid_delay_1_int + fluid_delay_2_int + fluid_delay_3_int + pocii.DRIP_T + pocii.PIERCE_T + 10000 + pocii.PIERCE_T + fluid_delay_4_int + pocii.DRIP_T + pocii.PIERCE_T + 2000, lambda: self.stop_timed_WF_decontamination(current_token)) #end
        #progress bar 
        frame_name = "frame_POCII_decontaminate_cartridge"
        self.POCII_counters[frame_name][0] = 0
        self.POCII_timers[frame_name].start(1000)  
    
    def stop_timed_WF_decontamination(self, token): 
        if self.POCII_is_running and token == self.current_session_token : 
            self.reset_button_style(self.ui.frame_POCII_decontaminate_cartridge)
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.log_event("DECONTAMINATION SUB EVENT COMPLETED")
            self.liveDataWorker.save_activity_log("Decontamination sub event completed", folder_name)
            self.POCII_is_running = False
        else: 
            pass
#endregion

    # region : HIGH V
    def toggle_WF_HV_start_stop_button(self): 
        if self.POCII_is_running: 
            self.stop_interrupt_WF_HV()
            self.POCII_is_running = False
        else: 
            self.start_WF_HV()
            self.POCII_is_running = True
            self.set_button_style(self.ui.high_voltage_frame.start_stop_button)

    def start_WF_HV(self): 
        #session token
        self.generate_new_token()
        current_token = self.current_session_token
        #save and display activity
        self.liveDataWorker.start_saving_live_non_pg_data(True)     # Live data saving thread flag
        self.log_event("HIGH VOLTAGE SUB EVENT STARTED")
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_activity_log("High volt sub event started", folder_name)
        #session time
        total_HV_WF_time = (pocii.V[2]/pocii.FR[0]) * 60 * 1000
        total_HV_WF_time_int = int(round(total_HV_WF_time)) 
        #operation
        QTimer.singleShot(1, lambda: self.WF_move_motor(3, pocii.HV_FLASK, current_token))
        QTimer.singleShot(1 + 10000, lambda: self.WF_move_motor(4, pocii.PIERCE, current_token))
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T, lambda: self.WF_start_sucrose_pump(pocii.FR[0], pocii.V[2], current_token))
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + 5000, lambda: self.WF_start_psu_pg(current_token))
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + 20000, lambda: self.WF_start_blood_pump(current_token))
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + total_HV_WF_time_int-5000, lambda: self.WF_stop_psu_pg(current_token))
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + total_HV_WF_time_int + 30000, lambda: self.WF_move_motor(4, pocii.DEPIERCE, current_token))
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + total_HV_WF_time_int+ 30000 + pocii.PIERCE_T + 2000, lambda: self.stop_timed_WF_HV(current_token))
        #progress bar
        frame_name = "high_voltage_frame"
        self.POCII_counters[frame_name][0] = 0
        self.POCII_timers[frame_name].start(1000)  
    
    def stop_interrupt_WF_HV(self): 
        #null the session
        self.current_session_token = None  
        #save and display acitivity 
        self.liveDataWorker.start_saving_live_non_pg_data(False)     # Live data saving thread flag
        self.log_event("HIGH VOLTAGE SUB EVENT STOPPED MANUALLY")
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_activity_log("High volt sub event manually stopped", folder_name)
        #shut down operations 
        self.reset_button_style(self.ui.high_voltage_frame.start_stop_button)
        self.stop_sucrose_pump()
        self.stop_psu_pg()
        self.stop_blood_pump()
        self.stop_motors(0, 0)
        #pause the progress bar
        frame_name = "high_voltage_frame"
        self.POCII_counters[frame_name][0] = 0
        self.POCII_timers[frame_name].stop()
    
    def stop_timed_WF_HV(self, token): 
        if self.POCII_is_running and token == self.current_session_token : 
            self.liveDataWorker.start_saving_live_non_pg_data(False)     # Live data saving thread flag
            self.reset_button_style(self.ui.high_voltage_frame.start_stop_button)
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.log_event("HIGH VOLTAGE SUB EVENT COMPLETED")
            self.liveDataWorker.save_activity_log("High volt sub event completed", folder_name)
            self.POCII_is_running = False
        else:
            pass
#endregion

    # region : FLUSH OUT
    def toggle_flush_out_start_stop_button(self): 
        if self.POCII_is_running: 
            self.stop_interrupt_WF_flush_out()
            self.POCII_is_running = False
        else: 
            self.WF_start_flush_out()
            self.POCII_is_running = True
            self.set_button_style(self.ui.flush_out_frame.start_stop_button)

    def stop_interrupt_WF_flush_out(self): 
        #null the session
        self.current_session_token = None  
        #save and display acitivity 
        self.log_event("FLUSH OUT SUB EVENT STOPPED MANUALLY")
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_activity_log("flush out sub event manually stopped", folder_name)
        #shut down operations 
        self.reset_button_style(self.ui.flush_out_frame.start_stop_button)
        self.stop_sucrose_pump()
        self.stop_ethanol_pump()
        self.stop_motors(0, 0)
        #pause the progress bar
        frame_name = "flush_out_frame"
        self.POCII_counters[frame_name][0] = 0
        self.POCII_timers[frame_name].stop()
    
    def WF_start_flush_out(self): 
        #session token
        self.generate_new_token()
        current_token = self.current_session_token
        #save and display activity
        self.log_event("FLUSH OUT SUB EVENT STARTED")
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_activity_log("Flush out sub event started", folder_name)
        #session time
        fluid_out_delay_1 = (pocii.V[0]/pocii.FR[1]) * 60 * 1000
        fluid_out_delay_1_int = int(round(fluid_out_delay_1)) 
        fluid_out_delay_2_int = fluid_out_delay_1_int
        #operation
        QTimer.singleShot(1, lambda: self.WF_move_motor(3, pocii.FLUSH_OUT_FLASK_1, current_token)) # move to flush out flask 1
        QTimer.singleShot(1 + 10000, lambda: self.WF_move_motor(4, pocii.PIERCE, current_token)) # pierce flush out flask 1
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T , lambda: self.WF_start_sucrose_pump(pocii.FR[1], pocii.V[0], current_token)) # req 111 : sucrose - 2.5 ml/min - 5mls
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + fluid_out_delay_1_int + pocii.DRIP_T, lambda: self.WF_move_motor(4, pocii.DEPIERCE, current_token)) # Depierce flush out flask 1
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + fluid_out_delay_1_int + pocii.DRIP_T + pocii.PIERCE_T, lambda: self.WF_move_motor(3, pocii.FLUSH_OUT_FLASK_2, current_token)) # move to flush out flask 2
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + fluid_out_delay_1_int + pocii.DRIP_T + pocii.PIERCE_T + 10000, lambda: self.WF_move_motor(4, pocii.PIERCE, current_token)) # pierce flush out flask 2
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + fluid_out_delay_1_int + pocii.DRIP_T + pocii.PIERCE_T + 10000 + pocii.PIERCE_T, lambda: self.WF_start_sucrose_pump(pocii.FR[1], pocii.V[0], current_token)) # repeat req 111 
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + fluid_out_delay_1_int + pocii.DRIP_T + pocii.PIERCE_T + 10000 + pocii.PIERCE_T + fluid_out_delay_2_int + pocii.DRIP_T, lambda: self.WF_move_motor(4, pocii.DEPIERCE, current_token)) # depierce 
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + fluid_out_delay_1_int + pocii.DRIP_T + pocii.PIERCE_T + 10000 + pocii.PIERCE_T + fluid_out_delay_2_int + pocii.DRIP_T + 2000, lambda: self.stop_timed_WF_flush_out(current_token)) # complete
        #progress bar
        frame_name = "flush_out_frame"
        self.POCII_counters[frame_name][0] = 0
        self.POCII_timers[frame_name].start(1000)  
    
    def stop_timed_WF_flush_out(self, token): 
        if self.POCII_is_running and token == self.current_session_token : 
            self.reset_button_style(self.ui.flush_out_frame.start_stop_button)
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.log_event("FLUSH OUT SUB EVENT COMPLETED")
            self.liveDataWorker.save_activity_log("Flush out sub event completed", folder_name)
            self.POCII_is_running = False
        else:
            pass

#endregion

    # region : 0V
    def toggle_WF_0V_start_stop_button(self): 
        if self.POCII_is_running: 
            self.stop_interrupt_WF_0V()
            self.POCII_is_running = False
        else: 
            self.start_WF_0V()
            self.set_button_style(self.ui.zero_volt_frame.start_stop_button)
            self.POCII_is_running = True
    
    def start_WF_0V(self): 
        #session token
        self.generate_new_token()
        current_token = self.current_session_token
        #save and display acitivity
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.log_event("ZERO VOLT SUB EVENT STARTED")
        self.liveDataWorker.save_activity_log("Zero volt sub event started", folder_name)
        #session time
        total_0V_WF_time = (pocii.V[2]/pocii.FR[0]) * 60 * 1000
        total_0V_WF_time_int = int(round(total_0V_WF_time)) + 2000
        #operations 
        QTimer.singleShot(1, lambda: self.WF_move_motor(3, pocii.ZERO_V_FLASK, current_token))
        QTimer.singleShot(1 + 10000, lambda: self.WF_move_motor(4, pocii.PIERCE, current_token))
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T, lambda: self.WF_start_sucrose_pump(pocii.FR[0], pocii.V[2], current_token))
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + 20000, lambda: self.WF_start_blood_pump(current_token))
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + total_0V_WF_time_int + 30000, lambda: self.WF_move_motor(4, pocii.DEPIERCE, current_token))
        QTimer.singleShot(1 + 10000 + pocii.PIERCE_T + total_0V_WF_time_int+ 30000 + pocii.PIERCE_T + 2000, lambda: self.stop_timed_WF_0V(current_token))
        #progress bar
        frame_name = "zero_volt_frame"
        self.POCII_counters[frame_name][0] = 0
        self.POCII_timers[frame_name].start(1000)  
    
    def stop_interrupt_WF_0V(self): 
        #null the session
        self.current_session_token = None  
        #save and display activity
        self.log_event("ZERO VOLT SUB EVENT STOPPED MANUALLY")
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_activity_log("Zero volt sub event stopped manually", folder_name)
        #shut down operations 
        self.reset_button_style(self.ui.zero_volt_frame.start_stop_button)
        self.stop_sucrose_pump()
        self.stop_blood_pump()
        self.stop_motors(0, 0)
        #pause the progress bar token
        frame_name = "zero_volt_frame"
        self.POCII_counters[frame_name][0] = 0
        self.POCII_timers[frame_name].stop()
   
    def stop_timed_WF_0V(self, token): 
        if self.POCII_is_running and token == self.current_session_token : 
            self.reset_button_style(self.ui.zero_volt_frame.start_stop_button)
            self.POCII_is_running = False
            self.log_event("ZERO VOLT SUB EVENT COMPLETE")
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Zero volt sub event completed", folder_name)
        else:
            pass
#endregion

    # region : SAFE DISCONNECT
    def toggle_safe_disconnect_start_stop_button(self): 
        if self.POCII_is_running: 
            self.stop_interrupt_WF_safe_disconnect()
            self.POCII_is_running = False
        else: 
            self.WF_start_safe_disconnect()
            self.POCII_is_running = True
            self.set_button_style(self.ui.safe_disconnect_frame.start_stop_button)

    def stop_interrupt_WF_safe_disconnect(self): 
        #null the session
        self.current_session_token = None  
        #save and display activity
        self.log_event("SAFE DISCONNECT STOPPED MANUALLY")
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_activity_log("Safe disconnect sub event manually stopped", folder_name)
        #shut down operations 
        self.reset_button_style(self.ui.safe_disconnect_frame.start_stop_button)
        self.stop_sucrose_pump()
        self.stop_blood_pump()
        self.stop_motors(0, 0)
        #pause the progress bar token
        frame_name = "safe_disconnect_frame"
        self.POCII_counters[frame_name][0] = 0
        self.POCII_timers[frame_name].stop()
    
    def WF_start_safe_disconnect(self): 
        #session token
        self.generate_new_token()
        current_token = self.current_session_token
        #save and display activity
        self.log_event("SAFE DISCONNECT SUB EVENT STARTED")
        folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
        self.liveDataWorker.save_activity_log("Safe disconnect sub event started", folder_name)
        #session time
        fluid_safe_disconnect_delay_1 = (pocii.V[1]/pocii.FR[1]) * 60 * 1000
        fluid_out_delay_1_int = int(round(fluid_safe_disconnect_delay_1)) 
        #operation
        QTimer.singleShot(1, lambda: self.WF_move_motor(3, pocii.WASTE_FLASK, current_token)) # move to flush out flask 1
        QTimer.singleShot(1 + 30000, lambda: self.WF_move_motor(4, pocii.PIERCE, current_token)) # pierce flush out flask 1
        QTimer.singleShot(1 + 30000 + pocii.PIERCE_T , lambda: self.WF_start_ethanol_pump(pocii.FR[1], pocii.V[1], current_token)) # fluid 1
        QTimer.singleShot(1 + 30000 + pocii.PIERCE_T + fluid_out_delay_1_int + 30000, lambda: self.WF_move_motor(4, pocii.DEPIERCE, current_token)) # Depierce flush out flask 1
        QTimer.singleShot(1 + 30000 + pocii.PIERCE_T + fluid_out_delay_1_int + 30000 + 2000, lambda: self.stop_timed_WF_safe_disconnect(current_token)) # stop sub event
        #progress bar
        frame_name = "safe_disconnect_frame"
        self.POCII_counters[frame_name][0] = 0
        self.POCII_timers[frame_name].start(1000)  
    
    def stop_timed_WF_safe_disconnect(self, token): 
        if self.POCII_is_running and token == self.current_session_token : 
            self.reset_button_style(self.ui.safe_disconnect_frame.start_stop_button)
            self.POCII_is_running = False
            self.log_event("Safe disconnect sub event completed")
            folder_name = self.workflow_LDA_popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log("Safe disconnect sub event completed", folder_name)
        else:
            pass

#endregion

    # region : UI METHODS
    def create_POCII_experiment_page(self):
        self.ui.frame_POCII_system_sterilaty.show()
        self.ui.frame_POCII_decontaminate_cartridge.show()
        self.ui.high_voltage_frame.show()
        self.ui.flush_out_frame.show()
        self.ui.zero_volt_frame.show()
        self.ui.safe_disconnect_frame.show()

        self.ui.spacing_placeholder1.show()
        self.ui.spacing_placeholder2.show()
        self.ui.spacing_placeholder3.show()
        self.ui.spacing_placeholder4.show()
        self.ui.spacing_placeholder5.show()
 
    def destroy_POCII_experiment_page(self): 

        self.ui.frame_POCII_system_sterilaty.hide()
        self.ui.frame_POCII_decontaminate_cartridge.hide()
        self.ui.high_voltage_frame.hide()
        self.ui.flush_out_frame.hide()
        self.ui.zero_volt_frame.hide()
        self.ui.safe_disconnect_frame.hide()

        self.reset_frame_progress_bar(self.ui.frame_POCII_system_sterilaty.progress_bar)
        self.reset_frame_progress_bar(self.ui.frame_POCII_decontaminate_cartridge.progress_bar)
        self.reset_frame_progress_bar(self.ui.high_voltage_frame.progress_bar)
        self.reset_frame_progress_bar(self.ui.flush_out_frame.progress_bar)
        self.reset_frame_progress_bar(self.ui.zero_volt_frame.progress_bar)
        self.reset_frame_progress_bar(self.ui.safe_disconnect_frame.progress_bar)

        self.ui.frame_POCII_system_sterilaty.hide()
        self.ui.frame_POCII_decontaminate_cartridge.hide()
        self.ui.high_voltage_frame.hide()
        self.ui.flush_out_frame.hide()
        self.ui.zero_volt_frame.hide()
        self.ui.safe_disconnect_frame.hide()

        self.ui.spacing_placeholder1.hide()
        self.ui.spacing_placeholder2.hide()
        self.ui.spacing_placeholder3.hide()
        self.ui.spacing_placeholder4.hide()
        self.ui.spacing_placeholder5.hide()
    
    def update_experiment_step_progress_bar(self, counter, timer, progress_bar, frame_name):
        
        interval = self.POCII_time_intervals[frame_name]
        counter[0] += 1
        if counter[0] <= interval:
            progress_bar.setValue(int((counter[0] / interval) * 100))
        else:
            timer.stop()
            counter[0] = 0

    def reset_frame_progress_bar(self, progress_bar):
        progress_bar.setValue(0)
        self.clear_log() 

#endregion

    # region : WORKFLOW OPERATIONAL METHODS 
    def generate_new_token(self):
        import time
        self.current_session_token = time.time() 

    def WF_start_blood_pump(self, token):
        if self.POCII_is_running and token == self.current_session_token: 
            self.start_blood_pump(self.ui.line_edit_blood.text(), self.ui.line_edit_blood_2.text())
            self.log_event(f"Blood syringe pump started with FR = {self.ui.line_edit_blood.text()} ml/min and V = {self.ui.line_edit_blood_2.text()} ml")
        else: 
            pass

    def WF_start_psu_pg(self, token): 
        if self.POCII_is_running and token == self.current_session_token: 
            self.start_psu_pg()
            self.log_event("High voltage signal started with Vp = 75 V and Vn = -75 V")
        else: 
            pass 

    def WF_stop_psu_pg(self, token): 
        if self.POCII_is_running and token == self.current_session_token: 
            self.stop_psu_pg()
            self.log_event("High voltage signal stopped")
        else: 
            pass 

    def WF_start_sucrose_pump(self, FR, V, token): 
        if self.POCII_is_running and token == self.current_session_token: 
            self.start_sucrose_pump(FR, V)
            self.ui.line_edit_sucrose.setText(f"{FR}")
            self.ui.line_edit_sucrose_2.setText(f"{V}")
            self.log_event(f"Sucrose pump started with FR = {FR} ml/min and V = {V} ml")
        else: 
            pass

    def WF_start_ethanol_pump(self, FR, V, token): 
        if self.POCII_is_running and token == self.current_session_token: 
            self.ui.line_edit_ethanol.setText(f"{FR}")
            self.ui.line_edit_ethanol_2.setText(f"{V}")
            self.start_ethanol_pump(FR, V)
            self.log_event(f"Ethanol pump started with FR = {FR} ml/min and V = {V} ml")
        else: 
            pass

    def WF_move_motor(self, motor_nr, position, token): 
        if self.POCII_is_running and token == self.current_session_token    : 
            msg = f'wMP-{motor_nr}-{position:06.2f}\n' 
            self.esp32Worker.write_serial_message(msg)           
            self.log_event("Motor moving to position")
        else: 
            pass

    def WF_announcement(self, message, token): 
        if self.POCII_is_running and token == self.current_session_token    : 
            self.log_event(message)
        else: 
            pass

    def stop_motors(self, distance_in_mm, direction): 
        msg1 = f'wMD-2-{distance_in_mm:06.2f}-{direction}\n'
        msg2 = f'wMD-2-{distance_in_mm:06.2f}-{direction}\n'
        msg3 = f'wMD-2-{distance_in_mm:06.2f}-{direction}\n'
        self.esp32Worker.write_serial_message(msg1)
        self.esp32Worker.write_serial_message(msg2)
        self.esp32Worker.write_serial_message(msg3)         
        self.log_event("Motors stopping manually")

    def move_motor_to(self, motor_nr, position):
        msg = f'wMP-{motor_nr}-{position:06.2f}\n' 
        self.esp32Worker.write_serial_message(msg)           
        
#endregion

    # region : WORKFLOW LOG 

    def log_event(self, message):
        # Get the current date and time
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        # Define the style (this should match your desired CSS from the style sheet)
        style = "color: #FFFFFF; font-family: Archivo; font-size: 25px;"
        # Create HTML string with styling
        html_message = f"<span style='{style}'>{message} #{current_time}</span><br>"
        # Append formatted message to the log
        self.ui.WF_activity_log.append(html_message)

    def clear_log(self):
        self.ui.WF_activity_log.clear()
    
    def show_activity_logger(self):
        self.ui.frame_activity_logger.show()
    
    def hide_activity_logger(self):
        self.ui.frame_activity_logger.hide()
#endregion
#endregion

# region : CLOSE EVENT 
    
    def closeEvent(self, event):

        # Properly handle worker threads and close them if necessary
        if hasattr(self, 'liveDataThread') and self.liveDataThread.isRunning():
            self.stopTimer.emit()  # Emit signal to stop the timer in the correct thread
            QThread.msleep(50)  # delay in milliseconds
            self.liveDataThread.quit()
            self.liveDataThread.wait()

        if hasattr(self, 'tempThread') and self.tempThread.isRunning():
            self.tempWorker.stop()  # Assuming you have a stop method to cleanly stop the worker
            self.tempThread.quit()
            self.tempThread.wait()

        if hasattr(self, 'esp32Thread') and self.esp32Thread.isRunning():
            self.esp32Worker.stop()  # Assuming you have a stop method to cleanly stop the worker
            self.esp32Thread.quit()
            self.esp32Thread.wait()

        if hasattr(self, 'peristalticDriverThread') and self.peristalticDriverThread.isRunning():
            self.peristalticDriverWorker.stop()  # Assuming you have a stop method to cleanly stop the worker
            self.peristalticDriverThread.quit()
            self.peristalticDriverThread.wait()

        if hasattr(self, 'pgThread') and self.pgThread.isRunning():
            self.pgWorker.stop()  # Assuming you have a stop method to cleanly stop the worker
            self.pgThread.quit()
            self.pgThread.wait()
            
        # Iterate over each serial device stored in device_serials
        for serial_device in self.device_serials:
            # Check if the serial_device is an instance of serial.Serial and it's open
            if isinstance(serial_device, serial.Serial) and serial_device.is_open:
                serial_device.close()  # Use the close method directly from pyserial
        
        # Handling other threads similarly...
        print('application stopped successfully')
        event.accept()  # Accept the close event to close the application

#endregion

#CODE THAT MAY GO OUT OF PRODUCTION BUT STILL MIGHT BE NEEDS TO BE PHASED OUT 
# region : PRESSURE
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
        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log(message, folder_name)

    def close_pressure_release_valve(self):
        self.pressure_release_valve_open = False  
        self.set_button_style(self.ui.pressure_check_button, 25)
        self.ui.pressure_check_button.setText("CLOSED")
        message = f'wRH\n'
        self.esp32Worker.write_serial_message(message)
        if self.live_data_is_logging: 
            folder_name = self.popup.line_edit_LDA_folder_name.text()
            self.liveDataWorker.save_activity_log(message, folder_name)

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
            if self.live_data_is_logging: 
                folder_name = self.popup.line_edit_LDA_folder_name.text()
                self.liveDataWorker.save_activity_log(message, folder_name)

        else: 
            self.reset_button_style(self.ui.pressure_reset_button)
            self.resetting_pressure = False
            self.timer.stop()
            self.counter = 0
            self.ui.pressure_progress_bar.setValue(0) 
            message = f'wRO\n'
            print(message)
            self.esp32Worker.write_serial_message(message)
            if self.live_data_is_logging: 
                folder_name = self.popup.line_edit_LDA_folder_name.text()
                self.liveDataWorker.save_activity_log(message, folder_name)
        
    def update_pressure_progress_bar(self):
        self.counter += 1
        if self.counter <= 20 and self.resetting_pressure:
            self.ui.pressure_progress_bar.setValue(int((self.counter / 20) * 100))
        else:
            self.start_stop_increasing_system_pressure()
#endregion