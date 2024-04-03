from PyQt5 import QtWidgets, QtCore, QtGui 
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot, QMutex, QTimer

import time
import sys
import os
import serial
import pandas as pd
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Communication_Functions.communication_functions import *

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
        if self.temperature_sensor_serial.serial_device is None:
            return -1
        try:
            # Assuming you're using minimalmodbus or a similar package for MODBUS communication
            raw_temperature = self.temperature_sensor_serial.serial_device.read_register(0x0E, functioncode=4, signed=True)
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

class ESP32SerialWorker(QObject):
    update_flowrate = pyqtSignal(float)
    update_pressure = pyqtSignal(float)
    update_fluidic_play_pause_buttons = pyqtSignal(float)

    interval = 250  

    def __init__(self, esp32_RTOS_serial):
        super(ESP32SerialWorker, self).__init__()
        self.esp32_RTOS_serial = esp32_RTOS_serial
        self._is_running = False
        self._lock = QMutex()

    @pyqtSlot()
    def run(self):
        self._is_running = True
        while self._is_running:
            QThread.msleep(self.interval)
            self._lock.lock()
            line = self.read_serial_line()
            self._lock.unlock()
            if line:
                self.parse_and_emit_data(line)

    def read_serial_line(self):
        if self.esp32_RTOS_serial.serial_device.in_waiting:
            return self.esp32_RTOS_serial.serial_device.readline().decode('utf-8').strip()
        return None

    def parse_and_emit_data(self, line):
        # Print the raw line for debugging
        #print(f"Raw line received: {line}")

        try:
            # Find the second occurrence of 'P' and the first occurrence of 'F'
            first_p_index = line.index('P')
            second_p_index = line.index('P', first_p_index + 1)
            f_index = line.index('F')

            # Extract the pressure and flow rate values
            pressure_value = line[second_p_index + 1:second_p_index + 6]
            flow_rate_value = line[f_index + 1:f_index + 6]
            target_volume_reached_char = line[f_index+6]

            pressure = float(pressure_value)
            flow_rate = float(flow_rate_value)
            target_volume_reached_state = float(target_volume_reached_char)
            
            # Emit the signals with the parsed data
            self.update_pressure.emit(pressure)
            self.update_flowrate.emit(flow_rate)
            if target_volume_reached_state: 
                self.update_fluidic_play_pause_buttons.emit(target_volume_reached_state)
                #print("cb")
        except ValueError as e:
            #print(f"Error parsing pressure or flow rate: {e}")
            pass

    def write_serial_message(self, message):
        self._lock.lock()
        try:
            if self.esp32_RTOS_serial.serial_device and self.esp32_RTOS_serial.serial_device.is_open:
                print(f"Sending message to 3PAC: {message}")
                self.esp32_RTOS_serial.serial_device.write(message.encode())
        finally:
            self._lock.unlock()

    @pyqtSlot()
    def stop(self):
        self._lock.lock()
        self._is_running = False
        self._lock.unlock()

class PulseGeneratorSerialWorker(QObject):
    update_pulse = pyqtSignal(np.ndarray)
    update_zerodata = pyqtSignal(object)  
    interval = 500   

    def __init__(self, pulse_generator_serial):
        super(PulseGeneratorSerialWorker, self).__init__()
        self.pulse_generator_serial = pulse_generator_serial 
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
            pg_data, _ = read_next_PG_pulse(self.pulse_generator_serial.serial_device)
            if pg_data is not None:
                self.update_pulse.emit(pg_data)
            QThread.msleep(self.interval)
    
    @pyqtSlot()
    def start_pg(self): 
        self._lock.lock()
        try:
            zerodata = send_PG_enable(self.pulse_generator_serial.serial_device, 0)
            self.update_zerodata.emit(zerodata)         

        finally:
            self._lock.unlock()  # Ensure the lock is always released

    @pyqtSlot()
    def stop_pg(self): 
        self._lock.lock()
        try:
            send_PG_disable(self.pulse_generator_serial.serial_device, 0)
        finally:
            self._lock.unlock()  # Ensure the lock is always released

    @pyqtSlot()
    def stop(self):
        self._lock.lock()
        self._is_running = False
        self._lock.unlock()

class PeristalticDriverWorker(QObject):

    interval = 250  
    def __init__(self, esp32_RTOS_serial):
        super(PeristalticDriverWorker, self).__init__()
        self.esp32_RTOS_serial = esp32_RTOS_serial
        self._is_running = False
        self._lock = QMutex()

    @pyqtSlot()
    def run(self):
        self._is_running = True
        while self._is_running:
            QThread.msleep(self.interval)
            self._lock.lock()
            line = self.read_serial_line()
            self._lock.unlock()
            if line:
                self.parse_and_emit_data(line)

    def read_serial_line(self):
        if self.esp32_RTOS_serial.serial_device.in_waiting:
            return self.esp32_RTOS_serial.serial_device.readline().decode('utf-8').strip()
        return None

    def parse_and_emit_data(self, line):
        print(f"Raw line received: {line}")

    def write_serial_message(self, message):
        self._lock.lock()
        try:
            if self.esp32_RTOS_serial.serial_device and self.esp32_RTOS_serial.serial_device.is_open:
                try: 
                    print(f"Message '{message}'sent to the peristaltic driver.")
                    self.esp32_RTOS_serial.serial_device.write(message.encode())
                except Exception as e: 
                    print(f"Failed to send message Error: {e}")
        finally:
            self._lock.unlock()

    @pyqtSlot()
    def stop(self):
        self._lock.lock()
        self._is_running = False
        self._lock.unlock()