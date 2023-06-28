import sys
from PyQt5 import QtWidgets
from layout import Ui_MainWindow
from functionality import Functionality

app = QtWidgets.QApplication(sys.argv)
window = Functionality()
window.show()
sys.exit(app.exec_())
    
    