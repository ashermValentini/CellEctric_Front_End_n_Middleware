import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Communication_Functions.communication_functions import *

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot, QMutex
from layout import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import numpy as np

VALVE_OFF = "wVS-010"
VALVE_ON = "wVS-000"
PELTIER_ON = "wCS-1"
PELTIER_OFF = "wCS-0"

#region : Thread Worker Classes 

class TempWorker(QObject):
    update_temp = pyqtSignal(float)
    interval = 10
    
    def __init__(self, device_serials):
        super(TempWorker, self).__init__()
        self.device_serials = device_serials
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
            
            temperature = read_temperature(self.device_serials[3])
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

    interval = 10  # customize the interval as you see fit

    def __init__(self, device_serial):
        super(ReadSerialWorker, self).__init__()
        self.device_serial = device_serial
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
            
            data = read_flowrate(self.device_serial[2])
            if data is not None:
                self.update_data.emit(data)
            QThread.msleep(self.interval)

    @pyqtSlot()
    def stop(self):
        self._lock.lock()
        self._is_running = False
        self._lock.unlock()


#endregion 

#region : Main functionality

class Functionality(QtWidgets.QMainWindow):
    def __init__(self):
        super(Functionality, self).__init__()
        
  
    # START SERIAL CONNECTION TO DEVICES
        self.device_serials = serial_start_connections() 
        handshake_3PAC(self.device_serials[2], print_handshake_message=True)
        
    # Set up the UI layout
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
         
        
    # Sucrose frame functionality (with threads)
    
        self.serialWorker = ReadSerialWorker(self.device_serials)
        self.serialThread = QThread()
        
        self.serialWorker.moveToThread(self.serialThread) 
        self.serialWorker.update_data.connect(self.updateSucroseProgressBar) # connect the worker signal to your progress bar update function

        self.sucrose_is_pumping = False # sucrose pumping button state flag 
        self.serialThread.started.connect(self.serialWorker.run) # start the worker when the thread starts
        self.ui.button_sucrose.pressed.connect(self.start_sucrose_pump)
        
        #self.sucroseTimer = None
        #self.read_sucrose_interval= 1000 #ms
       
    # Temp plotting (with threads)
        
        self.tempWorker = TempWorker(self.device_serials)
        self.tempThread = QThread()
        
        self.tempWorker.moveToThread(self.tempThread) 
        self.tempWorker.update_temp.connect(self.update_temp_plot)
        
        self.temp_is_plotting = False
        self.tempThread.started.connect(self.tempWorker.run)
        self.ui.temp_button.pressed.connect(self.start_stop_temp_plotting)
                    
        self.xdata = np.linspace(0, 499, 500)  
        self.plotdata = np.zeros(500)

    # Voltage plotting frame functionality
        self.voltage_is_plotting = False 
        self.ui.voltage_button.pressed.connect(self.start_voltage_plotting)
        
        self.voltageTimer = None        
        
        self.voltage_xdata = np.linspace(0, 499, 500)  
        self.plotdata = np.zeros(500)
        self.zerodata = [2000, 2000]
        
        self.voltage_plot_interval = 500  # ms
        self.maxval_pulse = 10  
        self.minval_pulse = -10

    # Using the current button to check moving within the page stack 
    
        self.ui.current_button.pressed.connect(self.go_to_route2)
        
    # Connections Frame Functionality
        self.coms_timer = QtCore.QTimer()
        self.coms_timer.setInterval(10000)  # 10 seconds
        self.coms_timer.timeout.connect(self.check_coms)
        self.coms_timer.start()
    
    #Voltage Signal Frame Functionality
        self.signal_is_enabled=False 
        self.ui.psu_button.pressed.connect(self.start_psu_pg)
        


    # flow rate frames functionality 
        #self.ui.line_edit_sucrose.returnPressed.connect(self.updateSucroseProgressBar)
        self.ui.line_edit_ethanol.returnPressed.connect(self.updateEthanolProgressBar)

#region : PLOTTING FUNCTIONS  

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
                    font-size: 15px;
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
                    font-size: 15px;
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
        self.ui.axes_voltage.plot(self.xdata, self.ydata, color='#0796FF')
        self.ui.axes_voltage.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
        self.ui.axes_voltage.set_ylim(min(self.ydata) - 1, max(self.ydata) + 10)  # dynamically update y range

        self.ui.axes_voltage.set_xlabel('Time (ms)', color='#FFFFFF')
        self.ui.axes_voltage.set_ylabel('Temperature (°C)', color='#FFFFFF')
        self.ui.axes_voltage.set_title('My Title', color='#FFFFFF')

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
                    font-size: 15px;
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
                    font-size: 15px;
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

        self.ui.axes_voltage.set_xlabel('Time (not scaled yet) (us)', color='#FFFFFF')
        self.ui.axes_voltage.set_ylabel('Voltage (V)', color='#FFFFFF')
        self.ui.axes_voltage.set_title('Voltage Signal', color='#FFFFFF')
        
        self.ui.canvas_voltage.draw()
   
    #endregion

#endregion

#region : SUCROSE PUMPING 
    def start_sucrose_pump(self):
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
                    font-size: 15px;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }
            """)

            flowRate1 = self.ui.line_edit_sucrose.text()
            if flowRate1: 
                flowRate1 = float(flowRate1)
            else: 
                flowRate1=0.00
    
            flowRate2 = self.ui.line_edit_ethanol.text()
            if flowRate2: 
                flowRate2 = float(flowRate2)
            else: 
                flowRate2=0.00
                
            print("MESSAGE: " + VALVE_ON)
            self.device_serials[2].write(VALVE_ON.encode())
            msg = self.device_serials[2].readline()
            print("RESPONSE: " + msg.decode())
            time.sleep(0.25)
            
            p1fr=1.00
            p2fr=0.00

            print("MESSAGE: PID On")
            turnOnPumpPID(self.device_serials[2])
            msg = self.device_serials[2].readline()
            print("RESPONSE: " + msg.decode())
            time.sleep(.25)

            print("MESSAGE: Send Flow Rates")
            writePumpFlowRate(self.device_serials[2], p1fr, p2fr)
            time.sleep(.25)
            self.serialThread.start()  # Start the existing thread
            #if self.sucroseTimer is None: #If the time is none we can be sure that we were in a state of not reading flow rate but now we should go into a state of reading flow rate
                #self.sucroseTimer = self.start_sucrose_timer() #we get into a state of reading flow rate by starting the timer for the surcrose reading function
        else: #Else if surcrose_is_pumping is true then it means the button was pressed during a state of pumping sucrose and the user would like to stop pumping which means we need to:
            # Change button color back to original
            self.ui.button_sucrose.setStyleSheet("""
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
            #Change the status of temp_is_plotting from true to False because we are about to stop plotting
            self.sucrose_is_pumping = False 
            
            self.device_serials[2].write(VALVE_OFF.encode())
            time.sleep(.25)
            p1fr=0.00
            p2fr=0.00
            writePumpFlowRate(self.device_serials[2], p1fr, p2fr)
            self.serialWorker.stop()  # Ask the worker to stop
            self.serialThread.quit()  # Ask the thread to stop
            self.serialThread.wait()  # Wait for the thread to stop
            #if self.sucroseTimer:                #If the temp plot timer is true it means we were indeed in a state of reading flow rate and can therefore be sure that we need to stop reading flow rate
                #self.sucroseTimer.stop()         #to stop reading the flow rate simply stop the timer
                #self.sucroseTimer = None         #but remember to set the timer to none so that we can start the timer the next time we click the button
                #self.ui.progress_bar_sucrose.setValue(0)
                
    #def start_sucrose_timer(self):
        #sucroseTimer = QtCore.QTimer()
        #sucroseTimer.setInterval(self.read_sucrose_interval)
        #sucroseTimer.timeout.connect(self.updateSucroseProgressBar) #add the reading function later
        #sucroseTimer.start()
        #return sucroseTimer
    
#endregion

# region : CONNECTION CIRCLE FUNCTION           
    def check_coms(self):

        #temperature = find_serial_port(SERIAL_TEMPSENS_VENDOR_ID, SERIAL_TEMPSENS_PRODUCT_ID)
        temp_serial = read_temperature(self.device_serials[3])
        esp = find_esp()
        if temp_serial is not -1:
            # Change circle color to green
            self.ui.circles["Temperature Sensor"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else:
            # Change circle color to white
            self.ui.circles["Temperature Sensor"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")
            
        if esp is not None:
            self.ui.circles["3PAC"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #0796FF; } QRadioButton { background-color: #222222; }")
        else: 
            self.ui.circles["3PAC"].setStyleSheet("QRadioButton::indicator { width: 20px; height: 20px; border: 1px solid white; border-radius: 10px; background-color: #222222; } QRadioButton { background-color: #222222; }")

#endregion 

# region : ROUND PROGRESS BAR FUNCTIONS 
    def updateSucroseProgressBar(self, value):
        
        #value = read_flowrate(self.device_serials[2])
        
        #line_edit_value = self.ui.line_edit_sucrose.text()
        #line_edit_value=float(line_edit_value)
        if value:
            value = float(value)
            if value <= self.ui.progress_bar_sucrose.max:
                self.ui.progress_bar_sucrose.setValue(value)
        else:
            self.ui.progress_bar_sucrose.setValue(2)
        print(value)
            
    def updateEthanolProgressBar(self):
        value = self.ui.line_edit_ethanol.text()
        if value:
            value = int(value)
            if value <= self.ui.progress_bar_ethanol.max:
                self.ui.progress_bar_ethanol.setValue(value)
        else:
            self.ui.progress_bar_ethanol.setValue(0)
        
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

#region : Changing pages 
    def go_to_route1(self):
        # This is the slot that gets called when the button is clicked
        self.ui.stack.setCurrentIndex(0)

    def go_to_route2(self):
        # This is the slot that gets called when the button is clicked
        self.ui.stack.setCurrentIndex(1)
        
#endregion 

#endregion 