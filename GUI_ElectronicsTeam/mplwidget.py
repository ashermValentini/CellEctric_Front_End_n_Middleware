# ------------------------------------------------------
# -------------------- mplwidget.py --------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvas

from matplotlib.figure import Figure

import matplotlib as plt

    
class MplWidget(QWidget):
    
    def __init__(self, parent = None):

        QWidget.__init__(self, parent)
        
        self.canvas = FigureCanvas(Figure())
        
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        #self.canvas.figure.set_facecolor("#222222")
        
        self.canvas.axes1 = self.canvas.figure.add_subplot(311)
        #self.canvas.axes1.set_title("Voltage")
        self.canvas.axes1.set_ylabel("Voltage [V]")
        self.canvas.axes2 = self.canvas.figure.add_subplot(312)
        #self.canvas.axes2.set_title("Current")
        self.canvas.axes2.set_ylabel("Current [A]")
        self.canvas.axes3 = self.canvas.figure.add_subplot(313)
        #self.canvas.axes2.set_title("Temperature")
        self.canvas.axes1.set_ylabel("Temperature [°C]")

        self.setLayout(vertical_layout)
