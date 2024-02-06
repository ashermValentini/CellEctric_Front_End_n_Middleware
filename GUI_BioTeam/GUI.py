import sys
import os
from PyQt5 import QtWidgets, QtGui
from layout import Ui_MainWindow
from functionality import Functionality


app = QtWidgets.QApplication(sys.argv)
QtGui.QFontDatabase.addApplicationFont(":/fonts/static/Archivo-Regular.ttf")

window = Functionality()
window.show()
sys.exit(app.exec_())

