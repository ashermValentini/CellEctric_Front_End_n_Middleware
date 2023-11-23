import time
import sys
import os
import serial

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Communication_Functions.communication_functions import *

from PyQt5 import QtWidgets, QtCore, QtGui 
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot, QMutex, QTimer
from PyQt5.QtWidgets import QProgressBar, QMessageBox
from layout import Ui_MainWindow
from layout import PopupWindow
from layout import EndPopupWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import numpy as np

#==============================
#SERIAL MESSAGES FOR 3PAC
#==============================

VALVE1_OFF = "wVS-001\n"
VALVE1_ON = "wVS-000\n"
PELTIER_ON = "wCS-1\n"
PELTIER_OFF = "wCS-0\n"
PUMPS_OFF ="wFO\n"

#========================
# DIRECTIONS FOR MOTORS 
#========================

DIR_M1_UP = -1
DIR_M1_DOWN = 1
DIR_M2_UP = 1
DIR_M2_DOWN = -1
DIR_M3_RIGHT = -1
DIR_M3_LEFT = 1
DIR_M4_UP = 1
DIR_M4_DOWN = -1

#========================
# THREAD WORKERS 
#========================

#region : The matrix begins here -Thread Worker Classes 

class TempWorker(QObject):
    update_temp = pyqtSignal(float)
    interval = 250
    
    def __init__(self, device_serials):
        super(TempWorker, self).__init__()
        self.device_serials = device_serials[3]
        self._is_running = False
        self._lock = QMutex()

    @pyqtSlot()
    def run(self):
        self._is_running = True
        while True:
            self._lock.lock()
            if not self._is_running:
                self._lock.unlock()
                break
            self._lock.unlock()
            
            temperature = read_temperature(self.device_serials)
            if temperature is not None:
                self.update_temp.emit(temperature)
            QThread.msleep(self.interval)

    @pyqtSlot()
    def stop(self):
        self._lock.lock()
        self._is_running = False
        self._lock.unlock()

class ReadSerialWorker(QObject):
    update_data = pyqtSignal(float)
    interval = 500  

    def __init__(self, device_serials):
        super(ReadSerialWorker, self).__init__()
        self.device_serials = device_serials[2]
        self._is_running = False
        self._lock = QMutex()

    @pyqtSlot()
    def run(self):
        self._is_running = True
        while True:
            self._lock.lock()
            if not self._is_running:
                self._lock.unlock()
                break
            self._lock.unlock()
            data = read_flowrate(self.device_serials)
            if data is not None:
                self.update_data.emit(data)
            QThread.msleep(self.interval)

    @pyqtSlot()
    def stop(self):
        self._lock.lock()
        self._is_running = False
        self._lock.unlock()

class PulseGeneratorSerialWorker(QObject):
    update_pulse = pyqtSignal(np.ndarray)
    update_zerodata = pyqtSignal(object)  
    interval = 500   

    def __init__(self, device_serials):
        super(PulseGeneratorSerialWorker, self).__init__()
        self.device_serials = device_serials[1]
        self._is_running = False
        self._lock = QMutex()

    @pyqtSlot()
    def run(self):
        self._is_running = True
        while True:
            self._lock.lock()
            if not self._is_running:
                self._lock.unlock()
                break
            self._lock.unlock()
            voltage_y, _ = read_next_PG_pulse(self.device_serials)
            if voltage_y is not None:
                self.update_pulse.emit(voltage_y)
            QThread.msleep(self.interval)
    
    @pyqtSlot()
    def start_pg(self): 
        self._lock.lock()
        try:
            zerodata = send_PG_enable(self.device_serials, 0)
            self.update_zerodata.emit(zerodata)         

        finally:
            self._lock.unlock()  # Ensure the lock is always released

    @pyqtSlot()
    def stop_pg(self): 
        self._lock.lock()
        try:
            send_PG_disable(self.device_serials, 0)
        finally:
            self._lock.unlock()  # Ensure the lock is always released

    @pyqtSlot()
    def stop(self):
        self._lock.lock()
        self._is_running = False
        self._lock.unlock()

#endregion 

#========================
# MAIN GUI THREAD
#========================

# region : Main functionality

class Functionality(QtWidgets.QMainWindow):
    def __init__(self):
        super(Functionality, self).__init__()

        #==============================================================================================================================================================================================================================
        # Initialize the main UI windows
        #==============================================================================================================================================================================================================================
        #region:
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #endregion
        # =====================================================================================================================================================================================================================================================================================================================================================================================================================================================================
        # START SERIAL CONNECTION TO DEVICES
        # =====================================================================================================================================================================================================================================================================================================================================================================================================================================
        #region: 
        self.flag_connections = [False, False, False, False]
        self.device_serials = serial_start_connections() 
        
        if self.device_serials[0].isOpen():
            self.flag_connections[0] = True
        if self.device_serials[1].isOpen():
            self.flag_connections[1] = True
        if self.device_serials[2].isOpen():
            self.flag_connections[2] = True
        if self.device_serials[3] is not None:
            self.flag_connections[3] = True

        if self.flag_connections[2]:
            handshake_3PAC(self.device_serials[2], print_handshake_message=True)

        if self.flag_connections[1]: 
            send_PG_pulsetimes(self.device_serials[1], 0)
        #endregion
        #================================================================================================================================================================================================================================
        # Side bar functionality 
        #================================================================================================================================================================================================================================
        #region:
        self.all_motors_are_home= False # sucrose pumping button state flag (starts unclicked)
        self.lights_are_on= False # sucrose pumping button state flag (starts unclicked)
        self.live_data_is_logging = False
        
        if self.flag_connections[2]:
            self.ui.button_lights.clicked.connect(self.skakel_ligte)
            self.ui.button_motors_home.clicked.connect(lambda: self.movement_homing(0))     
       
        self.ui.button_experiment_route.clicked.connect(self.go_to_route2)             
        self.ui.button_dashboard_route.clicked.connect(self.go_to_route1)             
        self.ui.button_dashboard_data_recording.clicked.connect(self.toggle_LDA_popup)
        #endregion
        #===========================================================================================================================================================================================================
        # Sucrose and Ethanol frame functionalities (reading flow rate as ReadSerialWorker thread and sending serial commands are done within the main thread)
        #===========================================================================================================================================================================================================
        #region:
        self.serialWorker = ReadSerialWorker(self.device_serials)
        self.serialThread = QThread()
        self.serialWorker.moveToThread(self.serialThread) 
        
        self.serialWorker.update_data.connect(self.updateEthanolProgressBar) # connect the worker signal to your progress bar update function
        self.serialWorker.update_data.connect(self.updateSucroseProgressBar) # connect the worker signal to your progress bar update function

        self.accumulated_sucrose_volume = 0
        self.accumulated_ethanol_volume = 0

        self.sucrose_is_pumping = False # sucrose pumping button state flag (starts unclicked)
        self.ethanol_is_pumping = False # ethanol pumping button state flag (starts unclicked)
        
        if self.flag_connections[2]:
            self.ui.button_sucrose.pressed.connect(self.start_sucrose_pump) # connect the signal to the slot 
            self.ui.button_ethanol.pressed.connect(self.start_ethanol_pump) # connect the signal to the slot 
        #endregion
        #===============================================================================================================================================================================================
        # Blood frame functionality
        #================================================================================================================================================================================================
        #region:
        self.blood_is_homing= False         
        self.blood_is_jogging_down = False  
        self.blood_is_jogging_up = False    
        self.blood_is_pumping = False

        self.blood_pump_timer = None  

        if self.flag_connections[2]: 
            self.ui.button_blood_top.clicked.connect(lambda: self.movement_homing(1))                       # connect the signal to the slot 
            self.ui.button_blood_up.pressed.connect(lambda: self.movement_startjogging(1, DIR_M1_UP, True)) # connect the signal to the slot    
            self.ui.button_blood_up.released.connect(lambda: self.movement_stopjogging(1))                  # connect the signal to the slot              

            self.ui.button_blood_down.pressed.connect(lambda: self.movement_startjogging(1, DIR_M1_DOWN, True)) # connect the signal to the slot
            self.ui.button_blood_down.released.connect(lambda: self.movement_stopjogging(1))                    # connect the signal to the slot
            self.ui.button_blood_play_pause.pressed.connect(self.toggle_blood_pump)
        #endregion
        #================================================================================================================================================================================================================================
        # Flask frame functionality
        #================================================================================================================================================================================================================================
        #region:
        self.flask_vertical_gantry_is_home= False     

        if self.flag_connections[2]: 
            self.ui.button_flask_bottom.clicked.connect(lambda: self.movement_homing(4))                        # connect the signal to the slot 
            self.ui.button_flask_up.pressed.connect(lambda: self.movement_startjogging(4, DIR_M4_UP, False))     # connect the signal to the slot    
            self.ui.button_flask_up.released.connect(lambda: self.movement_stopjogging(4))                      # connect the signal to the slot              
            self.ui.button_flask_down.pressed.connect(lambda: self.movement_startjogging(4, DIR_M4_DOWN, False)) # connect the signal to the slot
            self.ui.button_flask_down.released.connect(lambda: self.movement_stopjogging(4))                    # connect the signal to the slot

        self.flask_horizontal_gantry_is_home= False    

        if self.flag_connections[2]:
            self.ui.button_flask_rightmost.clicked.connect(lambda: self.movement_homing(3))                           # connect the signal to the slot 
            self.ui.button_flask_right.pressed.connect(lambda: self.movement_startjogging(3, DIR_M3_RIGHT, False))     # connect the signal to the slot    
            self.ui.button_flask_right.released.connect(lambda: self.movement_stopjogging(3))                      # connect the signal to the slot              
            self.ui.button_flask_left.pressed.connect(lambda: self.movement_startjogging(3, DIR_M3_LEFT, False)) # connect the signal to the slot
            self.ui.button_flask_left.released.connect(lambda: self.movement_stopjogging(3))                    # connect the signal to the slot
        #endregion
        #================================================================================================================================================================================================================================================================
        # Cartrige frame functionality
        #================================================================================================================================================================================================================================================================
        #region:
        self.cartrige_gantry_is_home= False 

        if self.flag_connections[2]:
            self.ui.button_cartridge_bottom.clicked.connect(lambda: self.movement_homing(2))                           # connect the signal to the slot 
            self.ui.button_cartridge_up.pressed.connect(lambda: self.movement_startjogging(2, DIR_M2_UP, False))     # connect the signal to the slot    
            self.ui.button_cartridge_up.released.connect(lambda: self.movement_stopjogging(2))                      # connect the signal to the slot              
            self.ui.button_cartridge_down.pressed.connect(lambda: self.movement_startjogging(2, DIR_M2_DOWN, False)) # connect the signal to the slot
            self.ui.button_cartridge_down.released.connect(lambda: self.movement_stopjogging(2))                    # connect the signal to the slot
        #endregion
        #====================================================================================================================================================================================================================================================================================
        # Temp plotting frame functionality (with threads)
        #====================================================================================================================================================================================================================================================================================
        #region:
        self.tempWorker = TempWorker(self.device_serials)
        self.tempThread = QThread()
        self.tempWorker.moveToThread(self.tempThread) 

        self.tempWorker.update_temp.connect(self.update_temp_plot)

        self.temp_is_plotting = False

        self.xdata = np.linspace(0, 499, 500)  
        self.plotdata = np.zeros(500)

        if self.flag_connections[3]:
            self.ui.temp_button.pressed.connect(self.start_stop_temp_plotting)
        #endregion
        #====================================================================================================================================================================================================================================================================================
        # Box plot frame functionality
        #====================================================================================================================================================================================================================================================================================
        #region:
        self.max_temp = float('-inf')
        self.min_temp = float('inf')

        self.tempWorker.update_temp.connect(self.update_temperature_labels)
        #endregion
        #======================================================================================================================================================================================================================================================================================================
        # Voltage plotting frame functionality
        #======================================================================================================================================================================================================================================================================================================
        #region:
        self.pgWorker = PulseGeneratorSerialWorker(self.device_serials)
        self.pgThread = QThread()
        self.pgWorker.moveToThread(self.pgThread)

        self.pgWorker.update_pulse.connect(self.update_voltage_plot)
        self.pgWorker.update_zerodata.connect(self.handleZeroDataUpdate)

        self.voltage_is_plotting = False 

        self.voltage_xdata = np.linspace(0, 499, 500)  
        self.plotdata = np.zeros(500)
        self.zerodata = [2000, 2000]
        
        self.maxval_pulse = 10  
        self.minval_pulse = -10

        if self.flag_connections[0] and self.flag_connections[1]:
            self.ui.voltage_button.pressed.connect(self.start_voltage_plotting)
        #endregion
        #======================================================================================================================================================================================================================================================================================================
        # Connections frame functionality
        #======================================================================================================================================================================================================================================================================
        #region:
        self.coms_timer = QtCore.QTimer()
        self.coms_timer.setInterval(10000)  # 10 seconds
        self.coms_timer.timeout.connect(self.check_coms)
        self.coms_timer.start()
        #endregion
        #======================================================================================================================================================================================================================================================================
        # Voltage signal frame functionality
        #======================================================================================================================================================================================================================================================================================================
        #region:
        self.signal_is_enabled=False 
        if self.flag_connections[0] and self.flag_connections[1]:
            self.ui.psu_button.pressed.connect(self.start_psu_pg)
        #endregion
        #======================================================================================================================================================================================================================================================================
        # Pressure frame functionality
        #======================================================================================================================================================================================================================================================================================================================================
        #region:
        self.reading_pressure = False
        self.resetting_pressure = False 

        if self.flag_connections[2]: 
            self.ui.pressure_check_button.pressed.connect(self.start_stop_pressure_reading)
            self.ui.pressure_reset_button.pressed.connect(self.update_pressure_progress_bar)

        self.serialWorker.update_data.connect(self.update_pressure_line_edit) # connect the worker signal to your progress bar update function
        #endregion
        #================================================================================================================================================================================================================================================================================================================
        # Start the thread that will read from the 3PAC
        #================================================================================================================================================================================================================================================================================================================================================
        #region:
        self.serialThread.started.connect(self.serialWorker.run)  # start the workers run function when the thread starts
        if self.flag_connections[2]:
            self.serialThread.start() #start the thread so that the dashboard always reads incoming serial data from the esp32 
        #endregion
        #================================================================================================================================================================================================================================================================================================================
        # Start the thread that will read from the Temp Sensor
        #================================================================================================================================================================================================================================================================================================================================================
        #region:
        self.tempThread.started.connect(self.tempWorker.run)
        if self.flag_connections[3]:
            self.tempThread.start()  # Start the existing thread
        #endregion
        #================================================================================================================================================================================================================================================================================================================
        # Start the thread that will read from the Pulse Generator
        #================================================================================================================================================================================================================================================================================================================================================
        #region:
        self.pgThread.started.connect(self.pgWorker.run)
        if self.flag_connections[1]:
            self.pgThread.start()  # Start the existing thread
        #endregion
        #================================================================================================================================================================================================================================================
        # Experiment selection 
        #================================================================================================================================================================================================================================================================================================
        #region:
        self.experiment_choice_is_locked_in = False
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

# region : PLOTTING FUNCTIONS  

    #region: Temperature Plot 

    def start_stop_temp_plotting(self):
        if not self.temp_is_plotting and not self.voltage_is_plotting:  
            self.temp_is_plotting = True
            self.ui.temp_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #0796FF;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 30px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }
            """)
        
        else:  # If currently plotting, stop

            self.temp_is_plotting = False
            self.ui.temp_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #222222;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 30px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }

                QPushButton:pressed {
                    background-color: #0796FF;
                }
            """)
    
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


            # Get the Axes object from the Figure for voltage plot
            self.ui.axes_voltage.grid(True, color='black', linestyle='--')
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
            self.ui.axes_voltage.set_xlabel('Time (ms)', color='#FFFFFF', fontsize=15)
            self.ui.axes_voltage.set_ylabel('Temperature (°C)', color='#FFFFFF',  fontsize=15)
            self.ui.axes_voltage.set_title('Electrode Temperature', color='#FFFFFF', fontsize=20, fontweight='bold', y=1.05)

            self.ui.canvas_voltage.draw()
    
    #endregion
     
    #region: Voltage Plot

    def handleZeroDataUpdate(self, zerodata):
        self.zerodata = zerodata

    def start_voltage_plotting(self):
        if not self.voltage_is_plotting and not self.temp_is_plotting:   
            self.ui.voltage_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #0796FF;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 30px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }
            """)
            self.voltage_is_plotting = True         
        
        else: 
            self.ui.voltage_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #222222;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 30px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }

                QPushButton:pressed {
                    background-color: #0796FF;
                }
            """)
            self.voltage_is_plotting = False        

    def update_voltage_plot(self, voltage_y):
        
        if self.voltage_is_plotting: 

            print(f"Data type: {type(voltage_y)}, Shape: {getattr(voltage_y, 'shape', 'N/A')}")

            voltage_y[:, 0] -= self.zerodata[0]            # voltage data
            voltage_y[:, -1] -= self.zerodata[1]           # current data  
                
            maxval_pulse_new = voltage_y.max(axis=0)[0]    # voltage data    

            scale_factor_x = 200 / 1000  # us per unit
            self.voltage_xdata = np.linspace(0, voltage_y.shape[0]-1, voltage_y.shape[0]) * scale_factor_x

            # Data cleanup if the pulse is turned on
            if self.signal_is_enabled:
                self.correct_max_voltage = float(self.ui.line_edit_max_signal.text())
                self.correct_min_voltage = float(self.ui.line_edit_min_signal.text())  
                scale_factor = self.correct_max_voltage/maxval_pulse_new
                voltage_y[:,0] *= scale_factor

            self.ui.axes_voltage.clear()
            self.ui.axes_voltage.plot(self.voltage_xdata, voltage_y[:, 0], color='#FFFFFF')
            self.ui.axes_voltage.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
            self.ui.axes_voltage.set_ylim(-90, 90) #+-90 are the PG voltage limits
            
            # Get the Axes object from the Figure for voltage plot
            self.ui.axes_voltage.grid(True, color='black', linestyle='--')
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
            self.ui.axes_voltage.set_ylabel('Voltage (V)', color='#FFFFFF',  fontsize=15)
            self.ui.axes_voltage.set_title('Voltage Signal', color='#FFFFFF',fontsize=20, fontweight='bold', y=1.05)
            
            self.ui.canvas_voltage.draw()
   
    #endregion

#endregion

# region : SUCROSE PUMPING 

    def start_sucrose_pump(self):
        if not self.ethanol_is_pumping and not self.reading_pressure:
            if not self.sucrose_is_pumping:   #if surcrose is pumping is false (ie the button has just been pressed to start plotting) then we need to:
                self.sucrose_is_pumping = True  
                # Change button color to blue
                self.ui.button_sucrose.setStyleSheet("""
                    QPushButton {
                        border: 2px solid white;
                        border-radius: 10px;
                        background-color: #0796FF;
                        color: #FFFFFF;
                        font-family: Archivo;
                        font-size: 30px;
                    }

                    QPushButton:hover {
                        background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                    }
                """)
        
                FR= float(self.ui.line_edit_sucrose.text()) 
                print(f"sent flow rate for sucrose: {FR} m//mn")

                writeSucrosePumpFlowRate(self.device_serials[2], FR)

            else: #Else if surcrose_is_pumping then it means the button was pressed during a state of pumping sucrose and the user would like to stop pumping which means we need to:
                
                self.ui.button_sucrose.setStyleSheet("""
                    QPushButton {
                        border: 2px solid white;
                        border-radius: 10px;
                        background-color: #222222;
                        color: #FFFFFF;
                        font-family: Archivo;
                        font-size: 30px;
                    }

                    QPushButton:hover {
                        background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                    }

                    QPushButton:pressed {
                        background-color: #0796FF;
                    }
                """)
                
                self.sucrose_is_pumping = False 
                self.accumulated_sucrose_volume=0 
                self.updateSucroseProgressBar(0)
                self.device_serials[2].write(PUMPS_OFF.encode())

#endregion

# region : ETHANOL PUMPING 

    def start_ethanol_pump(self):
        if not self.sucrose_is_pumping and not self.reading_pressure:
            if not self.ethanol_is_pumping:   #if surcrose is pumping is false (ie the button has just been pressed to start plotting) then we need to:
                self.ethanol_is_pumping = True  
                self.ui.button_ethanol.setStyleSheet("""
                    QPushButton {
                        border: 2px solid white;
                        border-radius: 10px;
                        background-color: #0796FF;
                        color: #FFFFFF;
                        font-family: Archivo;
                        font-size: 30px;
                    }

                    QPushButton:hover {
                        background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                    }
                """)


                FR= float(self.ui.line_edit_ethanol.text())
                print(f"sent flow rate for ethanol: {FR} m//mn")

                writeEthanolPumpFlowRate(self.device_serials[2], FR)
                
            else: #Else if surcrose_is_pumping is true then it means the button was pressed during a state of pumping sucrose and the user would like to stop pumping which means we need to:
                self.ui.button_ethanol.setStyleSheet("""
                    QPushButton {
                        border: 2px solid white;
                        border-radius: 10px;
                        background-color: #222222;
                        color: #FFFFFF;
                        font-family: Archivo;
                        font-size: 30px;
                    }

                    QPushButton:hover {
                        background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                    }

                    QPushButton:pressed {
                        background-color: #0796FF;
                    }
                """)
                
                #print("MESSAGE: Stop Ethanol")
                self.ethanol_is_pumping = False 
                self.accumulated_ethanol_volume = 0
                self.device_serials[2].write(PUMPS_OFF.encode())
                self.updateEthanolProgressBar(0)

#endregion 

# region : START PRESSURE READING

    def start_stop_pressure_reading(self):
        if not self.ethanol_is_pumping and not self.sucrose_is_pumping: #if we are currently pumping ethanol or sucrose we will not let this pressure read function run
            if not self.reading_pressure:   #if reading pressure is false (ie the button has just been pressed to start reading pressure) then we need to:
                self.reading_pressure = True  
                # Change button color to blue
                self.ui.pressure_check_button.setStyleSheet("""
                    QPushButton {
                        border: 2px solid white;
                        border-radius: 10px;
                        background-color: #0796FF;
                        color: #FFFFFF;
                        font-family: Archivo;
                        font-size: 30px;
                    }

                    QPushButton:hover {
                        background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                    }
                """)

                fetch_pressure(self.device_serials[2])
            
            else: #Else if reading pressure is true then it means the button was pressed during a state of reading pressure and the user would like to stop reading pressure which means we need to:
                # Change button color back to original
                self.reading_pressure=False
                self.ui.pressure_check_button.setStyleSheet("""
                    QPushButton {
                        border: 2px solid white;
                        border-radius: 10px;
                        background-color: #222222;
                        color: #FFFFFF;
                        font-family: Archivo;
                        font-size: 30px;
                    }

                    QPushButton:hover {
                        background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                    }

                    QPushButton:pressed {
                        background-color: #0796FF;
                    }
                """)
                stop_fetching_pressure(self.device_serials[2])
                self.ui.pressure_data.setText("-       Bar")

#endregion

# region : BLOOD PUMP

    def toggle_blood_pump(self):
        if not self.blood_is_pumping:
            self.start_blood_pump()
        else:
            self.stop_blood_pump()

    def start_blood_pump(self):  
        self.blood_is_pumping = True  
        
        self.ui.button_blood_play_pause.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 10px;
                background-color: #0796FF;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 30px;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }
        """)
        
        blood_volume = float(self.ui.line_edit_blood_2.text()) 
        blood_speed = float(self.ui.line_edit_blood.text())
        
        print(f"Calculating pump time with volume = {blood_volume}ml and speed = {blood_speed}ml/min")
        blood_pump_time = int((blood_volume / blood_speed) * 60000)  # Ensure this is the only place blood_pump_time is calculated
        print(f"Calculated pump time: {blood_pump_time} ms")
        
        writeBloodSyringe(self.device_serials[2], blood_volume, blood_speed)
        
        if self.blood_pump_timer is None:
            self.blood_pump_timer = QTimer()
            self.blood_pump_timer.timeout.connect(self.stop_blood_pump)

        self.blood_pump_timer.start(blood_pump_time)  # Start the timer
            
    def stop_blood_pump(self):
        self.ui.button_blood_play_pause.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 10px;
                background-color: #222222;
                color: #FFFFFF;
                font-family: Archivo;
                font-size: 30px;
            }

            QPushButton:hover {
                background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
            }

            QPushButton:pressed {
                background-color: #0796FF;
            }
        """)

        if self.blood_pump_timer is not None:
            self.blood_pump_timer.stop()  # Stop the timer

        self.blood_is_pumping = False
        writeBloodSyringe(self.device_serials[2], 0, 0)

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

# region : ROUND PROGRESS BAR FUNCTIONS 

    def updateSucroseProgressBar(self, value):
        if self.sucrose_is_pumping:
            if value:
                value = float(value)

                # Check that volume has been reached
                volume_per_interval = value *(ReadSerialWorker.interval/60000)
                self.accumulated_sucrose_volume += volume_per_interval

                try:
                    line_edit_value = float(self.ui.line_edit_sucrose_2.text()) 
                    if self.accumulated_sucrose_volume >= line_edit_value:
                        self.start_sucrose_pump()  
                        return
                except ValueError:
                    pass  
                
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


                # Check that volume has been reached
                volume_per_interval = value *(ReadSerialWorker.interval/60000)
                self.accumulated_ethanol_volume += volume_per_interval

                try:
                    line_edit_value = float(self.ui.line_edit_ethanol_2.text()) 
                    if self.accumulated_ethanol_volume >= line_edit_value:
                        self.start_ethanol_pump()  
                        return
                except ValueError:
                    pass  
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
        
#endregion 

# region : CLOSE EVENT FUNCTION

    def closeEvent(self, event):
        # Clean up resources and exit the application properly
        self.ui.progress_bar_sucrose.deleteLater()
        self.ui.line_edit_sucrose.deleteLater()
        self.coms_timer.stop()
        event.accept()
# endregion 

# region : ENABLE/DISABLE THE VOLTAGE SIGNAL (PSU AND PG)

    def start_psu_pg(self): 
        if not self.signal_is_enabled:  
            
            pos_setpoint_text = self.ui.line_edit_max_signal.text().strip()
            neg_setpoint_text = self.ui.line_edit_min_signal.text().strip()

            self.ui.line_edit_max_signal.setEnabled(False)
            self.ui.line_edit_min_signal.setEnabled(False)


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

            self.ui.psu_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #0796FF;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 15px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }
            """)
            
            self.signal_is_enabled = True

            neg_setpoint = abs(neg_setpoint)
            
            send_PSU_enable(self.device_serials[0], 1)
            time.sleep(0.25)

            send_PSU_setpoints(self.device_serials[0], pos_setpoint, neg_setpoint, 0)
            time.sleep(0.25)

            self.pgWorker.start_pg()

        else: 
            
            self.ui.psu_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #222222;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 15px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }

                QPushButton:pressed {
                    background-color: #0796FF;
                }
            """)
            self.signal_is_enabled = False         
            
            self.ui.line_edit_max_signal.setEnabled(True)
            self.ui.line_edit_min_signal.setEnabled(True)

            send_PSU_disable(self.device_serials[0], 1)
            self.pgWorker.stop_pg()

#endregion

# region : CHANGING PAGES 

    def go_to_route1(self):
        # This is the slot that gets called when the button is clicked
        self.ui.stack.setCurrentIndex(0)

    def go_to_route2(self):
        # This is the slot that gets called when the button is clicked
        self.ui.stack.setCurrentIndex(1)
        
#endregion 

# region : MOTOR MOVEMENTS
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
            self.ui.button_lights.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #0796FF;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 30px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }
            """)

            writeLedStatus(self.device_serials[2], 1, 1, 1)
            writeLogoStatus(self.device_serials[2], 1)

        else: #Else if surcrose_is_pumping is true then it means the button was pressed during a state of pumping sucrose and the user would like to stop pumping which means we need to:
            self.lights_are_on = False 
            self.ui.button_lights.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #222222;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 30px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }

                QPushButton:pressed {
                    background-color: #0796FF;
                }
            """)
            writeLogoStatus(self.device_serials[2], 0)
            writeLedStatus(self.device_serials[2], 0, 0, 0)
   
#endregion

# region : TEMPERATURE FRAME

    @pyqtSlot(float)
    def update_temperature_labels(self, temperature):
        if temperature > self.max_temp:
            self.max_temp = temperature
            self.ui.max_temp_data.setText(f"{self.max_temp}°")
            
        if temperature < self.min_temp:
            self.min_temp = temperature
            self.ui.min_temp_data.setText(f"{self.min_temp}°")

#endregion

# region : UPDATE PRESSURE PROGRESS BAR 

    def update_pressure_progress_bar(self):
        if not self.resetting_pressure:

            self.resetting_pressure = True 

            self.ui.pressure_reset_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #0796FF;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 30px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }
            """)

            # Reset progress bar
            self.ui.pressure_progress_bar.setValue(0)
            
            # Setup timer to update progress bar every second
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_pressure_progress)
            self.timer.start(1000)  # 1000 milliseconds == 1 second
            writePressureCommandStart(self.device_serials[2]); 
            
            # Initialize the counter
            self.counter = 0

        else: 
            self.ui.pressure_reset_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #222222;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 30px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }

                QPushButton:pressed {
                    background-color: #0796FF;
                }
            """)
            self.resetting_pressure = False
        
    def update_pressure_progress(self):
        self.counter += 1
        
        if self.counter <= 60 and self.resetting_pressure:
            self.ui.pressure_progress_bar.setValue(int((self.counter / 60) * 100))
        else:
            # Stop the timer and reset the counter when 60 seconds have passed
            self.timer.stop()
            self.counter = 0
            self.ui.pressure_progress_bar.setValue(0)  # Reset the progress bar to 0%
            self.ui.pressure_reset_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #222222;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 30px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }

                QPushButton:pressed {
                    background-color: #0796FF;
                }
            """)
            writePressureCommandStop(self.device_serials[2]); 


#endregion

# region : UPDATE PRESSURE LINE EDIT VALUE

    def update_pressure_line_edit(self, value):
        if self.reading_pressure and value is not None:
            self.ui.pressure_data.setText(f"{value} Bar")

#endregion

# region : DEMO

    def start_demo(self):
        self.step_two()                                             # start the automation sequence (AS)

    def step_two(self):
        if self.flag_connections[2]: 
            writeMotorDistance(self.device_serials[2], 2, 31, 2)  # connect fluidics to cartridge (move motor two down a distance 27.5mm)
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

# region : EXPERIMENT PAGE LAYOUTS 

    def lock_unlock_experiment_choice(self): 
        if not self.experiment_choice_is_locked_in: 
            self.experiment_choice_is_locked_in=True
            self.ui.user_info_lockin_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #0796FF;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 30px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }
            """)
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
            self.ui.user_info_lockin_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid white;
                    border-radius: 10px;
                    background-color: #222222;
                    color: #FFFFFF;
                    font-family: Archivo;
                    font-size: 30px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }

                QPushButton:pressed {
                    background-color: #0796FF;
                }
            """)
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

# region : EXPERIMENT PAGE LAYOUTS PROGRESS BARS 

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


#endregion

# region : DASHBOARD POP UP 

    def toggle_LDA_popup(self):
        if not self.live_data_is_logging:
            self.showLDAPopup()
            self.live_data_is_logging = True
        else:
            self.showEndLDAPopup()
            self.live_data_is_logging = False

    def showLDAPopup(self):
        self.popup = PopupWindow()
        self.popup.button_LDA_go_live.clicked.connect(self.go_live)
        self.popup.exec_()

    def showEndLDAPopup(self):
        self.endpopup = EndPopupWindow()
        self.endpopup.button_end_LDA.clicked.connect(self.end_go_live)
        self.endpopup.exec_()
    

#endregion 

# region : DASHBOARD LIVE DATA AQUISITION 

    def go_live(self):
        border_style = "#centralwidget { border: 7px solid green; }"
        self.live_data_is_logging = True
        self.ui.centralwidget.setStyleSheet(border_style)
        print("going live")
    
    def end_go_live(self):
        border_style = "#centralwidget { border: 0px solid green; }"
        self.live_data_is_logging = False
        self.ui.centralwidget.setStyleSheet(border_style)



#endregion 

#endregion 