from PyQt5 import QtWidgets, QtCore, QtGui 
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot, QMutex, QTimer


class TempWorker(QObject):
    update_temp = pyqtSignal(float)
    interval = 250

    def __init__(self, temperature_sensor_serial):
        super(TempWorker, self).__init__()
        self.temperature_sensor_serial = temperature_sensor_serial
        self._is_running = False
        self._lock = QMutex()

    @pyqtSlot()
    def run(self):
        self._is_running = True
        while self._is_running:
            QThread.msleep(self.interval)
            temperature = self.read_temp()
            if temperature is not None:
                self.update_temp.emit(temperature)

    def read_temp(self):
        if self.temperature_sensor_serial.connection is None:
            return -1
        try:
            # Assuming you're using minimalmodbus or a similar package for MODBUS communication
            raw_temperature = self.temperature_sensor_serial.connection.read_register(0x0E, functioncode=4, signed=True)
            temperature = raw_temperature / 10.0
            return temperature
        except IOError as e:
            print("Failed to read from temperature sensor, retrying...")
            print(f"IOError: {str(e)}")
            return None

    @pyqtSlot()
    def stop(self):
        self._lock.lock()
        self._is_running = False
        self._lock.unlock()
