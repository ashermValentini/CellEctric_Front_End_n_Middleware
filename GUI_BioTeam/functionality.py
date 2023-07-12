import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Communication_Functions.communication_functions import *

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from layout import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import numpy as np

VALVE_ON = "wVS-010"
PELTIER_ON = "wCS-1"
PELTIER_OFF = "wCS-0"

class Functionality(QtWidgets.QMainWindow):
    def __init__(self):
        super(Functionality, self).__init__()
        
  
    # START SERIAL CONNECTION TO DEVICES
        self.device_serials = serial_start_connections() 
        
        
        #for device_serial in self.device_serials:
        #    if device_serial.name is not None:
        #        self.ui.display_system_log.append("Port: " + device_serial.name)
        #    else:
        #        self.ui.display_system_log.append("Port: None")
    
    # Set up the UI layout
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        
        handshake_3PAC(self.device_serials[2], print_handshake_message=True)
       
    # Sucrose frame functionality
        self.sucrose_is_pumping = False # sucrose pumping button state flag 
        self.ui.button_sucrose.pressed.connect(self.start_sucrose_pump)
        self.sucroseTimer = None
        self.read_sucrose_interval= 500 #ms
       
        
    # Temp plotting frame functionality
        self.temp_is_plotting = False  #temperature plotting button state flag
        self.ui.temp_button.pressed.connect(self.start_temp_plotting)
        
        self.xdata = np.linspace(0, 499, 500)  # This creates an array from 0 to 499 with 500 elements.

        self.interval = 30  # ms
        self.plotdata = np.zeros(500)
        self.timer = None
        
    # Connections Frame Functionality
        self.coms_timer = QtCore.QTimer()
        self.coms_timer.setInterval(10000)  # 10 seconds
        self.coms_timer.timeout.connect(self.check_coms)
        self.coms_timer.start()


    # flow rate frames functionality 
        self.ui.line_edit_sucrose.returnPressed.connect(self.updateSucroseProgressBar)
        self.ui.line_edit_ethanol.returnPressed.connect(self.updateEthanolProgressBar)

# region : PLOTTING FUNCTIONS  
    def start_temp_plotting(self):
        if not self.temp_is_plotting:   #if temp_is_plotting is false (ie the button has just been pressed to start plotting) the change the color to blue
            # Change button color to blue
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
            self.temp_is_plotting = True  #Change the status of temp_is_plotting from false to true because we are about to begin plotting
            if self.timer is None:        #If the time is none we can be sure that we were in a state of not plotting but now we should go into a state of plotting 
                self.timer = self.start_timer() #we get into a stat of plotting by starting the timer for the temp plot (which has been poorly named timer-too generic must change it)
        else: #Else if temp_is_plotting is true then it means the button was pressed during a state of plotting and the user would like to stop plotting which means we need to:
            # Change button color back to original
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
            self.temp_is_plotting = False #Change the status of temp_is_plotting from true to False because we are about to stop plotting
            if self.timer:                #If the temp plot timer is true it means we were indeed in a state of plotting and can therefore be sure that we need to stop plotting
                self.timer.stop()         #to stop plottng simply stop the timer
                self.timer = None         #but remember to set the timer to none so that we can start the timer the next time we click the button

    def start_timer(self):
        timer = QtCore.QTimer()
        timer.setInterval(self.interval)
        timer.timeout.connect(self.update_temp_plot)
        timer.start()
        return timer

    def update_temp_plot(self):
        temperature = read_temperature(self.device_serials[3])
        if temperature is not None:
            shift = 1
            self.plotdata = np.roll(self.plotdata, -shift)
            self.plotdata[-shift:] = temperature
            self.ydata = self.plotdata[:]
            
            self.xdata = np.roll(self.xdata, -shift)
            self.xdata[-1] = self.xdata[-2] + 1  # This will keep increasing the count on the x-axis

            self.ui.axes_voltage.clear()
            self.ui.axes_voltage.plot(self.xdata, self.ydata, color='blue')
            self.ui.axes_voltage.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
            self.ui.axes_voltage.set_ylim(min(self.ydata) - 1, max(self.ydata) + 10)  # dynamically update y range

            self.ui.axes_voltage.set_xlabel('Time (ms)', color='#FFFFFF')
            self.ui.axes_voltage.set_ylabel('Temperature (°C)', color='#FFFFFF')
            self.ui.axes_voltage.set_title('My Title', color='#FFFFFF')
        
        self.ui.canvas_voltage.draw()
#endregion

#region : SUCROSE PUMPING 
    def start_sucrose_pump(self):
        if not self.sucrose_is_pumping:   #if surcrose is pumping is false (ie the button has just been pressed to start plotting) then we need to:
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
            self.sucrose_is_pumping = True  
            
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
                
            self.device_serials[2].write(PELTIER_ON.encode())
            
            if self.sucroseTimer is None: #If the time is none we can be sure that we were in a state of not reading flow rate but now we should go into a state of reading flow rate
                self.sucroseTimer = self.start_sucrose_timer() #we get into a state of reading flow rate by starting the timer for the surcrose reading function
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
            self.device_serials[2].write(PELTIER_OFF.encode())
            if self.sucroseTimer:                #If the temp plot timer is true it means we were indeed in a state of reading flow rate and can therefore be sure that we need to stop reading flow rate
                self.sucroseTimer.stop()         #to stop reading the flow rate simply stop the timer
                self.sucroseTimer = None         #but remember to set the timer to none so that we can start the timer the next time we click the button

    def start_sucrose_timer(self):
        sucroseTimer = QtCore.QTimer()
        sucroseTimer.setInterval(self.read_sucrose_interval)
        #sucroseTimer.timeout.connect(self.update_temp_plot) #add the reading function later
        sucroseTimer.start()
        return sucroseTimer
       

        
#endregion


# region : CONNECTION CIRCLE FUNCTION           
    def check_coms(self):

        #temperature = find_serial_port(SERIAL_TEMPSENS_VENDOR_ID, SERIAL_TEMPSENS_PRODUCT_ID)
        temperature = read_temperature(self.device_serials[3])
        esp = find_esp()
        if temperature is not None:
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
    def updateSucroseProgressBar(self):
        value = self.ui.line_edit_sucrose.text()
        if value:
            value = int(value)
            if value <= self.ui.progress_bar_sucrose.max:
                self.ui.progress_bar_sucrose.setValue(value)
        else:
            self.ui.progress_bar_sucrose.setValue(0)
            
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
