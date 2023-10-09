import time
import sys
import os
import serial

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Communication_Functions.communication_functions import *

from PyQt5 import QtWidgets, QtCore, QtGui 
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot, QMutex, QTimer
from layout import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import numpy as np

#==============================
#SERIAL MESSAGES
#==============================

VALVE1_OFF = "wVS-001\n"
VALVE1_ON = "wVS-000\n"
PELTIER_ON = "wCS-1\n"
PELTIER_OFF = "wCS-0\n"
PUMPS_OFF ="wFO\n"

#========================
# DIRECTIONS
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
# THREADS
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
    interval = 250  # customize the interval to the nyquist criteria (half the sending rate from the esp32 so that we dont miss data)

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
            print(data)
            if data is not None:
                self.update_data.emit(data)
            QThread.msleep(self.interval)

    @pyqtSlot()
    def stop(self):
        self._lock.lock()
        self._is_running = False
        self._lock.unlock()

#endregion 

#========================
# MAIN
#========================
# region : Main functionality

class Functionality(QtWidgets.QMainWindow):
    def __init__(self):
        super(Functionality, self).__init__()
        
  
        # =====================================
        # START SERIAL CONNECTION TO DEVICES
        # =====================================
        self.flag_connections = [False, False, False, False]
        self.device_serials = serial_start_connections() 
        # CHECK CONNECTION STATUS
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

        #==============================
        # Set up the UI layout
        #==============================
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #================================
        # Side bar functionality 
        #================================

        self.all_motors_are_home= False # sucrose pumping button state flag (starts unclicked)
        self.lights_are_on= False # sucrose pumping button state flag (starts unclicked)
        

        self.ui.button_motors_home.clicked.connect(lambda: self.movement_homing(0))     # connect the signal to the slot 
        #self.ui.button_experiment_route.clicked.connect(self.go_to_route2)             # connect the signal to the slot
        self.ui.button_lights.clicked.connect(self.skakel_ligte)                        # connect the signal to the slot

        #===========================================================================================================================================================================
        # Edits made below are for the investors presentation: 
        #===========================================================================================================================================================================

        self.ui.button_experiment_route.clicked.connect(self.start_demo)

        #===========================================================================================================================================================================
        # Sucrose and Ethanol frame functionalities (with reading flow rate as ReadSerialWorker thread and sending serial commands are done within the main thread for now)
        #===========================================================================================================================================================================
        self.serialWorker = ReadSerialWorker(self.device_serials)
        self.serialThread = QThread()
        self.serialWorker.moveToThread(self.serialThread) 
        
        self.serialWorker.update_data.connect(self.updateEthanolProgressBar) # connect the worker signal to your progress bar update function
        self.serialWorker.update_data.connect(self.updateSucroseProgressBar) # connect the worker signal to your progress bar update function


        self.sucrose_is_pumping = False # sucrose pumping button state flag (starts unclicked)
        self.ethanol_is_pumping = False # ethanol pumping button state flag (starts unclicked)
        
        if self.flag_connections[2]:
            self.ui.button_sucrose.pressed.connect(self.start_sucrose_pump) # connect the signal to the slot 
            self.ui.button_ethanol.pressed.connect(self.start_ethanol_pump) # connect the signal to the slot 


        #================================
        # Blood frame functionality
        #================================

        self.blood_is_homing= False         # sucrose pumping button state flag (starts unclicked)
        self.blood_is_jogging_down = False  # ethanol pumping button state flag (starts unclicked)
        self.blood_is_jogging_up = False    # ethanol pumping button state flag (starts unclicked)

        if self.flag_connections[2]: 
            self.ui.button_blood_top.clicked.connect(lambda: self.movement_homing(1))                       # connect the signal to the slot 
            self.ui.button_blood_up.pressed.connect(lambda: self.movement_startjogging(1, DIR_M1_UP, True)) # connect the signal to the slot    
            self.ui.button_blood_up.released.connect(lambda: self.movement_stopjogging(1))                  # connect the signal to the slot              

            self.ui.button_blood_down.pressed.connect(lambda: self.movement_startjogging(1, DIR_M1_DOWN, True)) # connect the signal to the slot
            self.ui.button_blood_down.released.connect(lambda: self.movement_stopjogging(1))                    # connect the signal to the slot


        #================================
        # Flask frame functionality
        #================================

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

        #================================
        # Cartrige frame functionality
        #================================

        self.cartrige_gantry_is_home= False 

        if self.flag_connections[2]:
            self.ui.button_cartridge_bottom.clicked.connect(lambda: self.movement_homing(2))                           # connect the signal to the slot 
            self.ui.button_cartridge_up.pressed.connect(lambda: self.movement_startjogging(2, DIR_M2_UP, False))     # connect the signal to the slot    
            self.ui.button_cartridge_up.released.connect(lambda: self.movement_stopjogging(2))                      # connect the signal to the slot              
            self.ui.button_cartridge_down.pressed.connect(lambda: self.movement_startjogging(2, DIR_M2_DOWN, False)) # connect the signal to the slot
            self.ui.button_cartridge_down.released.connect(lambda: self.movement_stopjogging(2))                    # connect the signal to the slot

            
        #====================================================
        # Temp plotting frame functionality(with threads)
        #====================================================
        self.tempWorker = TempWorker(self.device_serials)
        self.tempThread = QThread()
        
        self.tempWorker.moveToThread(self.tempThread) 
        self.tempWorker.update_temp.connect(self.update_temp_plot)
        
        self.temp_is_plotting = False
        self.tempThread.started.connect(self.tempWorker.run)
        self.ui.temp_button.pressed.connect(self.start_stop_temp_plotting)

                    
        self.xdata = np.linspace(0, 499, 500)  
        self.plotdata = np.zeros(500)

        #====================================================
        # Box plot frame functionality
        #====================================================
        self.max_temp = float('-inf')
        self.min_temp = float('inf')

        self.tempWorker.update_temp.connect(self.update_temperature_labels)



        #======================================
        # Voltage plotting frame functionality
        #======================================
        self.voltage_is_plotting = False 
        self.ui.voltage_button.pressed.connect(self.start_voltage_plotting)
        
        self.voltageTimer = None        
        
        self.voltage_xdata = np.linspace(0, 499, 500)  
        self.plotdata = np.zeros(500)
        self.zerodata = [2000, 2000]
        
        self.voltage_plot_interval = 500  # ms
        self.maxval_pulse = 10  
        self.minval_pulse = -10

        
        #======================================
        # Connections frame functionality
        #======================================
        self.coms_timer = QtCore.QTimer()
        self.coms_timer.setInterval(10000)  # 10 seconds
        self.coms_timer.timeout.connect(self.check_coms)
        self.coms_timer.start()
    
        #======================================
        # Voltage signal frame functionality
        #======================================
    
        self.signal_is_enabled=False 
        self.ui.psu_button.pressed.connect(self.start_psu_pg)

        #======================================
        # Pressure frame functionality
        #======================================
        self.reading_pressure = False
        self.resetting_pressure = False 

        if self.flag_connections[2]: 
            self.ui.pressure_check_button.pressed.connect(self.start_stop_pressure_reading)
            self.ui.pressure_reset_button.pressed.connect(self.update_pressure_progress_bar)

        self.serialWorker.update_data.connect(self.update_pressure_line_edit) # connect the worker signal to your progress bar update function

        #================================================
        # Start the thread that will read from the 3PAC
        #================================================
        self.serialThread.started.connect(self.serialWorker.run)  # start the workers run function when the thread starts
        if self.flag_connections[2]:
            self.serialThread.start() #start the thread so that the dashboard always reads incoming serial data from the esp32 
        

# region : PLOTTING FUNCTIONS  

    #region: Temperature Plot 
    def start_stop_temp_plotting(self):
        if not self.temp_is_plotting:  # If not currently plotting, start
            self.tempThread.start()  # Start the existing thread

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
            self.tempWorker.stop()  # Ask the worker to stop
            self.tempThread.quit()  # Ask the thread to stop
            self.tempThread.wait()  # Wait for the thread to stop
            
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
    def start_voltage_plotting(self):
        if not self.voltage_is_plotting:   #if voltage_is_plottingt is false (ie the button has just been pressed to start plotting) the change the color to blue
            # Change button color to blue
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
            self.voltage_is_plotting = True  #Change the status of temp_is_plotting from false to true because we are about to begin plotting
            if self.voltageTimer is None:        #If the time is none we can be sure that we were in a state of not plotting but now we should go into a state of plotting 
                self.voltageTimer = self.start_voltage_timer() #we get into a stat of plotting by starting the timer for the temp plot (which has been poorly named timer-too generic must change it)
        else: #Else if temp_is_plotting is true then it means the button was pressed during a state of plotting and the user would like to stop plotting which means we need to:
            # Change button color back to original
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
            self.voltage_is_plotting = False #Change the status of temp_is_plotting from true to False because we are about to stop plotting
            if self.voltageTimer:                #If the temp plot timer is true it means we were indeed in a state of plotting and can therefore be sure that we need to stop plotting
                self.voltageTimer.stop()         #to stop plottng simply stop the timer
                self.voltageTimer = None         #but remember to set the timer to none so that we can start the timer the next time we click the button

    def start_voltage_timer(self):
        voltageTimer = QtCore.QTimer()
        voltageTimer.setInterval(self.voltage_plot_interval)
        voltageTimer.timeout.connect(self.update_voltage_plot)
        voltageTimer.start()
        return voltageTimer

    def update_voltage_plot(self):
        
    
        self.voltage_y, _ = read_next_PG_pulse(self.device_serials[1])  # READ NEXT PULSE
        
        self.voltage_y[:, 0] -= self.zerodata[0]        # ZERO THE VOLTAGE DATA
        self.voltage_y[:, -1] -= self.zerodata[1]       # ZERO THE CURRENT DATA
        
        maxval_pulse_new = self.voltage_y.max(axis=0)[0]    # GET MAX VALUE FROM VOLTAGE PULSE
        minval_pulse_new = self.voltage_y.min(axis=0)[0]    # GET MIN VALUE FROM VOLTAGE PULSE

        if maxval_pulse_new > self.maxval_pulse:        # CHECK MAX VALUE OVER TIME
            self.maxval_pulse = maxval_pulse_new
            
        if minval_pulse_new < self.minval_pulse:        # CHECK MIN VALUE OVER TIME
            self.minval_pulse = minval_pulse_new
        
        
        self.voltage_xdata = np.linspace(0, self.voltage_y.shape[0]-1, self.voltage_y.shape[0])
        
        self.ui.axes_voltage.clear()
        self.ui.axes_voltage.plot(self.voltage_xdata,self.voltage_y[:, 0], color='#0796FF')
        self.ui.axes_voltage.set_ylim(self.minval_pulse-10, self.maxval_pulse+10)  

        self.ui.axes_voltage.set_xlabel('Time (not scaled yet) (us)', color='#FFFFFF',  fontsize=15)
        self.ui.axes_voltage.set_ylabel('Voltage (V)', color='#FFFFFF',  fontsize=15)
        self.ui.axes_voltage.set_title('Voltage Signal', color='#FFFFFF',fontsize=20, fontweight='bold')
        
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
            
                p1fr=2.50

                writeSucrosePumpFlowRate(self.device_serials[2], p1fr)


                
            else: #Else if surcrose_is_pumping is true then it means the button was pressed during a state of pumping sucrose and the user would like to stop pumping which means we need to:
                # Change button color back to original
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
                #Change the status of temp_is_plotting from true to False because we are about to stop plotting
                self.sucrose_is_pumping = False 
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
                p1fr=2.50

                #writeEthanolPumpFlowRate(self.device_serials[2], p1fr)
                writeSucrosePumpFlowRate(self.device_serials[2], p1fr) #only for the investors presentation
                
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
        # see motor movement functions
#endregion

# region : CONNECTION CIRCLE FUNCTION           
    def check_coms(self):

        #temperature = find_serial_port(SERIAL_TEMPSENS_VENDOR_ID, SERIAL_TEMPSENS_PRODUCT_ID)
    
        if self.flag_connections[3]:
            self.ui.circles["Temperature Sensor"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else:
            self.ui.circles["Temperature Sensor"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")
            
        if self.flag_connections[2]:
            self.ui.circles["3PAC"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else: 
            self.ui.circles["3PAC"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")

#endregion 

# region : ROUND PROGRESS BAR FUNCTIONS 
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
                    self.ui.progress_bar_sucrose.setValue(0)
                # Check if the value is greater than the maximum allowed value
                elif value > self.ui.progress_bar_sucrose.max:
                    self.ui.progress_bar_sucrose.setValue(self.ui.progress_bar_sucrose.max)
                else:
                    self.ui.progress_bar_sucrose.setValue(value)
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
            send_PSU_enable(self.device_serials[0], 1)
            send_PG_pulsetimes(self.device_serials[1], 0)
            self.zerodata = send_PG_enable(self.device_serials[1], 1)
            # CHECK IF DATA WAS SENT SUCESSFULLY
            if self.zerodata:                                         
                self.maxval_pulse = 0   
                self.minval_pulse = 0

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
            self.signal_is_enabled = False #Change the status of temp_is_plotting from true to False because we are about to stop plotting        
            send_PSU_disable(self.device_serials[0], 1)
            time.sleep(0.25)
            send_PG_disable(self.device_serials[1], 1)
                 
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

#region : TEMPERATURE FRAME

    @pyqtSlot(float)
    def update_temperature_labels(self, temperature):
        if temperature > self.max_temp:
            self.max_temp = temperature
            self.ui.max_temp_data.setText(f"{self.max_temp}°")
            
        if temperature < self.min_temp:
            self.min_temp = temperature
            self.ui.min_temp_data.setText(f"{self.min_temp}°")

#endregion

#region : UPDATE PRESSURE PROGRESS BAR 

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

#region : UPDATE PRESSURE LINE EDIT VALUE

    def update_pressure_line_edit(self, value):
        if self.reading_pressure and value is not None:
            self.ui.pressure_data.setText(f"{value} Bar")




#endregion

# region : Investors Presentation

    def start_demo(self):
        self.step_two()                                         # start the automation sequence (AS)

    def step_two(self):
        writeMotorDistance(self.device_serials[2], 2, 27.5, 2)  # connect fluidics to cartridge (move motor two down a distance 27.5mm)
        writeLedStatus(self.device_serials[2], 0, 1, 0)         # syringe region LED on
        QTimer.singleShot(5000, self.step_three)                # give the motor 5 seconds to reach its posistion before executing the next step in the AS 
 
    def step_three(self):
        writeMotorDistance(self.device_serials[2], 4, 37, 1)    # connect waste flask to cartridge (move motor 4 up a distance 38mm)
        QTimer.singleShot(6500, self.step_four)                 # give the motor 6.5 seconds to reach its posistion before executing the next step in the AS

    def step_four(self):
        self.start_ethanol_pump()                               # flush ethanol
        writeLedStatus(self.device_serials[2], 0, 0, 2)         # blink the resevoir region LED  
        QTimer.singleShot(30000, self.step_four_part_two)       # let ethanol flush for 30 seconds 

    def step_four_part_two(self):
        self.start_ethanol_pump()                               # stop ethanol 
        writeLedStatus(self.device_serials[2], 0, 0, 0)         # turn of all LEDs
        QTimer.singleShot(3000, self.step_five)                 # wait 3 seconds before proceeding to next step (can reduce this time) 

    def step_five(self):
        writeMotorDistance(self.device_serials[2], 4, 37, 2)    # disconnect waste flask (move motor 4 down a distance of 37mm)
        writeLedStatus(self.device_serials[2], 1, 0, 0)         # flask region led on 
        QTimer.singleShot(6500, self.step_five_part_two)        # give motor 4 6.5 seconds to get to its position before proceeding to the next step in the AS
    
    def step_five_part_two(self):
        writeMotorDistance(self.device_serials[2], 3, 60, 1)    # connect mixing flask to cartridge (move motor three left a distance of 60mm)
        QTimer.singleShot(10000, self.step_five_part_three)     # give motor 3 10 seconds to get to its position before proceeding to the next step in the AS
    
    def step_five_part_three(self): 
        writeMotorDistance(self.device_serials[2], 4, 37 , 1)   # connect mixing flask to cartridge (move motor 3 up a distance of 38mm)
        QTimer.singleShot(7000, self.step_six)                  # give motor 4 7 seconds to get to its position before proceeding to the next step in the AS
    
    def step_six(self): 
        writeBloodSyringe(self.device_serials[2], 0.115, 0.125) # flush blood 
        writeLedStatus(self.device_serials[2], 0, 2, 0)         # blink syring region LED 
        QTimer.singleShot(50, self.step_six_part_two)           # wait 50ms before proceeding to the next step in the AS to allow the serial coms to complete
    
    def step_six_part_two(self): 
        self.start_sucrose_pump()                               # flush sucrose (with blood running)
        QTimer.singleShot(60000, self.step_six_part_three)      # let sucrose flush with blood for 60 seconds

    def step_six_part_three(self): 
        self.start_sucrose_pump()                               # stop sucrose
        writeLedStatus(self.device_serials[2], 0, 0, 0)         # turn off all LEDs
        QTimer.singleShot(7000, self.step_seven)                

    def step_seven(self): 
        writeMotorDistance(self.device_serials[2], 4, 37, 2)    # disconnect mixing flask (move motor 4 down a distnace of 38 mm)
        writeLedStatus(self.device_serials[2], 1, 0, 0)         # flask region led on 
        QTimer.singleShot(7000, self.step_seven_part_two)       # give motor 4 7 seconds to get to its position before proceeding to the next step in the AS

    def step_seven_part_two(self): 
        writeMotorDistance(self.device_serials[2], 3, 62, 1)    # retrieve mixing flask (move motor three a distance of 62 mm left)
        QTimer.singleShot(7000, self.end_demo)                  # give motor 3 7 seconds to get to its posistion before proceeding to the next step
    
    def end_demo(self): 
        writeLedStatus(self.device_serials[2], 2, 2, 2)         # blink lights to take the flask
        QTimer.singleShot(10000, self.end_demo_part_two)        # let the lights blink for 10 seconds
    
    def end_demo_part_two(self):
        writeLedStatus(self.device_serials[2], 1, 0, 0)         # turn light back on 





#endregion

#endregion 