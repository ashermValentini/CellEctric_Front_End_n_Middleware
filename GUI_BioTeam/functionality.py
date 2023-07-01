from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from layout import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import numpy as np
from read_temperature import read_temperature

from example_handshake_3PAC import find_esp

class Functionality(QtWidgets.QMainWindow):
    def __init__(self):
        super(Functionality, self).__init__()
    
    # Set up the UI layout
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
    # temp plotting frame
        self.temp_is_plotting = False  #temperature plotting button state flag
        
        self.ui.temp_button.pressed.connect(self.start_temp_plotting)
        
        #dynamic x axis 
        self.xdata = np.linspace(0, 499, 500)  # This creates an array from 0 to 499 with 500 elements.

        # Plotting variables
        self.interval = 30  # ms
        self.plotdata = np.zeros(500)
        self.timer = None
        
    # Start the timer for the check_coms method
        self.coms_timer = QtCore.QTimer()
        self.coms_timer.setInterval(10000)  # 10 seconds
        self.coms_timer.timeout.connect(self.check_coms)
        self.coms_timer.start()


    # flow rate frames functionality 
        self.ui.line_edit_sucrose.returnPressed.connect(self.updateSucroseProgressBar)
        self.ui.line_edit_ethanol.returnPressed.connect(self.updateEthanolProgressBar)

# region : PLOTTING FUNCTIONS  
    def start_temp_plotting(self):
        if not self.temp_is_plotting:
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
            self.temp_is_plotting = True
            if self.timer is None:
                self.timer = self.start_timer()
        else:
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
            self.temp_is_plotting = False
            if self.timer:
                self.timer.stop()
                self.timer = None

    def start_timer(self):
        timer = QtCore.QTimer()
        timer.setInterval(self.interval)
        timer.timeout.connect(self.update_temp_plot)
        timer.start()
        return timer

    def update_temp_plot(self):
        temperature = read_temperature()
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

# region : CONNECTION CIRCLE FUNCTION           
    def check_coms(self):
        temperature = read_temperature()
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
