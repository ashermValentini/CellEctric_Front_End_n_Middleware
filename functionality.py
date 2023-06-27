from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from layout import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import numpy as np
from read_temperature import read_temperature

class Functionality(QtWidgets.QMainWindow):
    def __init__(self):
        super(Functionality, self).__init__()
    

    # Set up the UI layout
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        

    # psu enbaled button frame
        self.ui.psu_button.pressed.connect(self.start_plotting)
        
    #plotting frame
        self.is_plotting = False  #psuEnabled Button state flag
        
        #dynamic x axis 
        self.xdata = np.linspace(0, 499, 500)  # This creates an array from 0 to 499 with 500 elements.

        # Plotting variables
        self.interval = 30  # ms
        self.plotdata = np.zeros(500)
        self.timer = None


    # flow rate frames functionality 
        self.ui.line_edit_sucrose.returnPressed.connect(self.updateSucroseProgressBar)
        self.ui.line_edit_blood.returnPressed.connect(self.updateBloodProgressBar)
        self.ui.line_edit_ethanol.returnPressed.connect(self.updateEthanolProgressBar)

#plotting functions 
    def start_plotting(self):
        if not self.is_plotting:
            # Change button color to blue
            # Change button color to blue
            self.ui.psu_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid #8f8f91;
                    border-radius: 6px;
                    background-color: #0796FF;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }
            """)
            self.is_plotting = True
            if self.timer is None:
                self.timer = self.start_timer()
        else:
            # Change button color back to original
            self.ui.psu_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid #8f8f91;
                    border-radius: 6px;
                    background-color: #222222;
                }

                QPushButton:hover {
                    background-color: rgba(7, 150, 255, 0.7);  /* 70% opacity */
                }

                QPushButton:pressed {
                    background-color: #0796FF;
                }
            """)
            self.is_plotting = False
            if self.timer:
                self.timer.stop()
                self.timer = None

    def start_timer(self):
        timer = QtCore.QTimer()
        timer.setInterval(self.interval)
        timer.timeout.connect(self.update_plot)
        timer.start()
        return timer

    def update_plot(self):
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

            

#ROUND PROGRESS BARS 
    def updateSucroseProgressBar(self):
        value = self.ui.line_edit_sucrose.text()
        if value:
            value = int(value)
            if value <= self.ui.progress_bar_sucrose.max:
                self.ui.progress_bar_sucrose.setValue(value)
        else:
            self.ui.progress_bar_sucrose.setValue(0)
    
    def updateBloodProgressBar(self):
        value = self.ui.line_edit_blood.text()
        if value:
            value = int(value)
            if value <= self.ui.progress_bar_blood.max:
                self.ui.progress_bar_blood.setValue(value)
        else:
            self.ui.progress_bar_blood.setValue(0)
            
    def updateEthanolProgressBar(self):
        value = self.ui.line_edit_ethanol.text()
        if value:
            value = int(value)
            if value <= self.ui.progress_bar_ethanol.max:
                self.ui.progress_bar_ethanol.setValue(value)
        else:
            self.ui.progress_bar_ethanol.setValue(0)


    def closeEvent(self, event):
        # Clean up resources and exit the application properly
        self.ui.progress_bar_sucrose.deleteLater()
        self.ui.line_edit_sucrose.deleteLater()
        event.accept()
    
