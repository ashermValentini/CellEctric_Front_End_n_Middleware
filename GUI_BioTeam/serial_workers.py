from PyQt5 import QtWidgets, QtCore, QtGui 
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot, QMutex, QTimer

import time
import sys
import os
import serial
import pandas as pd
import datetime
import struct  
import numpy as np                  


# CONSTANTS
NUM_ATTEMPTS = 5
PSU_TYPE_PACKET = 0x1000
PG_TYPE_DATASTART = 0x1000
PG_TYPE_DATAEND = 0x1001
PG_TYPE_PULSEDATA = 0x1002
PG_TYPE_ZERODATA = 0x1003

#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#from Communication_Functions.communication_functions import *

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
            try:
                # Using 'replace' to substitute invalid characters with a placeholder
                return self.esp32_RTOS_serial.serial_device.readline().decode('utf-8', 'replace').strip()
            except UnicodeDecodeError as e:
                #print(f"Failed to decode line, error: {e}")
                pass
        return None

    def parse_and_emit_data(self, line):
        if not line:
            #print("Received empty line")
            return

        try:
            # Print the raw line for debugging
            #print(f"Raw line received: {line}")

            # Find the second occurrence of 'P' and the first occurrence of 'F'
            first_p_index = line.index('P')
            second_p_index = line.index('P', first_p_index + 1)
            f_index = line.index('F')

            # Extract the pressure and flow rate values
            pressure_value = line[second_p_index + 1:second_p_index + 6]
            flow_rate_value = line[f_index + 1:f_index + 6]

            pressure = float(pressure_value)
            flow_rate = float(flow_rate_value)

            # Emit the signals with the parsed data
            self.update_pressure.emit(pressure)
            self.update_flowrate.emit(flow_rate)

        except ValueError as e:
            #print(f"Error parsing pressure or flow rate: {e}")
            # Log or handle the data that caused the error
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
        self._def_crc16_table()


    @pyqtSlot()
    def run(self):
        self._is_running = True
        while True:
            self._lock.lock()
            if not self._is_running:
                self._lock.unlock()
                break
            self._lock.unlock()
            try:
                pg_data, _ = self.read_next_PG_pulse(self.pulse_generator_serial.serial_device)
                if pg_data is not None:
                    self.update_pulse.emit(pg_data)
            except Exception as e:
                print(f"Error in read_next_PG_pulse: {e}")  # or handle the error in a more appropriate way
            QThread.msleep(self.interval)
    
    @pyqtSlot()
    def start_pg(self): 
        self._lock.lock()
        try:
            zerodata = self.send_PG_enable(self.pulse_generator_serial.serial_device, 0)
            self.update_zerodata.emit(zerodata)         
        except Exception as e:
            print(f"Error in start_pg: {e}")  # or handle the error in a more appropriate way
        finally:
            self._lock.unlock()  # Ensure the lock is always released
    
    def set_pulse_shape(self, rep_rate, pulse_length, on_time): 
        self._lock.lock()
        try:
            self.send_PG_pulsetimes(self.pulse_generator_serial.serial_device, 0, rep_rate, pulse_length, on_time, verbose=1)
        except Exception as e:
            print(f"Error in set_pulse_shape: {e}")  # or handle the error in a more appropriate way
        finally:
            self._lock.unlock()  # Ensure the lock is always released

    @pyqtSlot()
    def stop_pg(self): 
        self._lock.lock()
        try:
            self.send_PG_disable(self.pulse_generator_serial.serial_device, 0)
        except Exception as e:
            print(f"Error in stop_pg: {e}")  # or handle the error in a more appropriate way
        finally:
            self._lock.unlock()  # Ensure the lock is always released

    @pyqtSlot()
    def stop(self):
        self._lock.lock()
        self._is_running = False
        self._lock.unlock()

    def _def_crc16_table(self): 
        self.crc16_table = [
            0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
            0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
            0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
            0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
            0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
            0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
            0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
            0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
            0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
            0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
            0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
            0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
            0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
            0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
            0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
            0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
            0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
            0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
            0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
            0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
            0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
            0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
            0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
            0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
            0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
            0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
            0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
            0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
            0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
            0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
            0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
            0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040
        ]

    def crc16(self, buffer_uint8, crc=0):

        for byte in buffer_uint8:
            crc = (crc >> 8) ^ self.crc16_table[(crc ^ byte) & 0xff]
        return crc
    
    def testCRC(self, binaryData, verbose=0):

        if verbose: print("----------------- START: TEST CRC -----------------")        # PRINT FORMATTING

        crc_check = False

        # CHECK IF BINARY DATA IS AVAILABLE
        if not binaryData:
            if verbose: print("No binary data available.")
            return crc_check, None

        # GET AND CALCULATE THE CRC VALUES
        try:
            arr = np.array(struct.unpack('<' + 'H' * (len(binaryData) // 2), binaryData))   # CREATE DATA ARRAY (uint16) 
            dataCRC = arr[0]                                                                # GET CRC VALUE FROM THE ARRAY
            calcCRC = self.crc16(np.frombuffer(binaryData[2:], dtype=np.uint8))              	# CALCULATE CRC VALUE ACCORDING TO DATA

            if verbose >1: print("DATA AS ARRAY:\n{}".format(arr))                          # PRINT FORMATTING
            if verbose: print("CRC IN DATA:\t\t{}".format(dataCRC))                         # PRINT FORMATTING
            if verbose: print("CRC CALCULATED:\t{}".format(calcCRC))                        # PRINT FORMATTING
            
            # CRC CHECK
            if dataCRC == calcCRC:
                crc_check = True
            
            if verbose: print("CRC CHECK:\t\t{}".format(crc_check))                         # PRINT FORMATTING
            if verbose: print("----------------- END: TEST CRC -----------------")          # PRINT FORMATTING
        
        except struct.error as e:
            if verbose: print(f"Error unpacking binaryData: {e}")
            return crc_check, None
        
        # RETURN DATA
        return crc_check, calcCRC
    
    def CraftPackage_run(self, verbose=0):
        payload = np.array([
            0x0003              # Start Command 
            ], dtype=np.uint16) # data type as uint16 (16 bit)

        # FILL IT WITH 0s THAT IT HAS A SIZE OF 31 UINT16 (1 left for CRC)
        datapacket = np.pad(payload, (0, 30), mode='constant')

        # CREATE A BYTE REPRESENTATION FOR CRC CALCULATION
        byte_datapacket = datapacket.tobytes()

        # CALCULATE CRC
        crc = self.crc16(np.frombuffer(byte_datapacket, dtype=np.uint8))

        # CREATE COMPLETE ARRAY FOR USB DATA
        sendable_arr = np.insert(datapacket, 0, crc)

        # CREATE A BYTE REPRESENTATION FOR USB DATA
        sendable_bytedata = sendable_arr.tobytes()
        if verbose: print(sendable_bytedata)

        # TEST THE CRC AND SET DATA TO 0 IF CRC IS WRONG
        crc_check, _ = self.testCRC(sendable_bytedata, verbose)
        if not crc_check: sendable_bytedata = 0

        return sendable_bytedata
    
    def CraftPackage_stop(self, verbose=0):
        payload = np.array([
            0x0004              # Stop Command 
            ], dtype=np.uint16) # data type as uint16 (16 bit)

        # FILL IT WITH 0s THAT IT HAS A SIZE OF 31 UINT16 (1 left for CRC)
        datapacket = np.pad(payload, (0, 30), mode='constant')

        # CREATE A BYTE REPRESENTATION FOR CRC CALCULATION
        byte_datapacket = datapacket.tobytes()

        # CALCULATE CRC
        crc = self.crc16(np.frombuffer(byte_datapacket, dtype=np.uint8))

        # CREATE COMPLETE ARRAY FOR USB DATA
        sendable_arr = np.insert(datapacket, 0, crc)

        # CREATE A BYTE REPRESENTATION FOR USB DATA
        sendable_bytedata = sendable_arr.tobytes()
        if verbose: print(sendable_bytedata)

        # TEST THE CRC AND SET DATA TO 0 IF CRC IS WRONG
        crc_check, _ = self.testCRC(sendable_bytedata, verbose)
        if not crc_check: sendable_bytedata = 0

        return sendable_bytedata

    # CRAFT PULSE PACKAGE FOR PG
    def PG_CraftPackage_setTimes(self, repRate=5000, frequency=0 ,pulseLength=75, onTime=248, verbose=0):
        # CALCULATE THE repRate IF THE FREQUENCY IS SET (from HZ to us)
        if frequency:
            repRate = 1e6 / frequency


        # PACKET AS ARRAY
        payload = np.array([
            0x0001,             # SetSetpoints Command 
            repRate,            # Frequency --> How many pulses per second
            pulseLength,        # Length of the ON-Pulse (also scales the whole pulse)
            onTime,             # Something for clipping. Set it to the repRate to be save
            ], dtype=np.uint16) # data type as uint16 (16 bit)

        # FILL IT WITH 0s THAT IT HAS A SIZE OF 31 UINT16 (1 left for CRC)
        datapacket = np.pad(payload, (0, 27), mode='constant')

        # CREATE A BYTE REPRESENTATION FOR CRC CALCULATION
        byte_datapacket = datapacket.tobytes()

        # CALCULATE CRC
        crc = self.crc16(np.frombuffer(byte_datapacket, dtype=np.uint8))

        # CREATE COMPLETE ARRAY FOR USB DATA
        sendable_arr = np.insert(datapacket, 0, crc)

        # CREATE A BYTE REPRESENTATION FOR USB DATA
        sendable_bytedata = sendable_arr.tobytes()
        if verbose: print(sendable_bytedata)

        # TEST THE CRC AND SET DATA TO 0 IF CRC IS WRONG
        crc_check, _ = self.testCRC(sendable_bytedata, verbose)
        if not crc_check: sendable_bytedata = 0

        return sendable_bytedata

    def readSerialData(self, ser, verbose=0):
        if verbose: print("==================== START: READING ====================")      # PRINT FORMATTING

        serialData = ser.read(64)                                   # READ 64 BYTES OF THE DATA STREAM (= 1 PACKET)
        crc_status, crc_value = self.testCRC(serialData, verbose)        # CHECK THE CRC AND RETURN THE CRC-VALUE

        # SHOW ERROR MESSAGE, IF CRC IS WRONG
        if not crc_status:
            print("CRC Error with received data!")

        if verbose: print("==================== END: READING ====================")      # PRINT FORMATTING
        return serialData, crc_status, crc_value

    def writeSerialData(self, ser, data_to_send, num_attempts=NUM_ATTEMPTS, verbose=0):

        if verbose: print("--- fct: writeSerialData ---")
        success = False
        
        for i in range(num_attempts):
            try:
                ser.flushOutput()
                ser.flushInput()
                time.sleep(0.25)
                ser.write(data_to_send)
                success = True
                if verbose: print('Data sent successfully')
                break  # if data was sent successfully, exit the loop
            except serial.SerialTimeoutException:
                if verbose: print(f'Timeout occurred while sending data. Attempt {i+1}/{num_attempts}')
                time.sleep(0.5)  # wait for a short time before attempting again
        
        if verbose: print("--- end: writeSerialData ---")
        return success

    def send_PG_enable(self, ser, verbose=0):
        # CRAFT ENABLE PACKET
        packet = self.CraftPackage_run()

        # SEND PACKET
        success = self.writeSerialData(ser, packet, verbose=verbose)
        if not success:
            if verbose: print("ERROR: Could not write serial data to PG to enable it.")
            return False

        # READ UNTIL TYPE == "ZEROVALUES" .. maybe not, because I don't receive this type of data
        type = 0
        while type != PG_TYPE_ZERODATA:
            if verbose: print("WAITING FOR ZERO DATA")
            PG_data, type, _= self.read_PG_data(ser)

        
        # [zeroVoltage, zeroCurrent]
        zerodata = [PG_data[0], PG_data[1]]

        return zerodata

    # STOP THE PG
    def send_PG_disable(self, ser, verbose=0):
        package = self.CraftPackage_stop(verbose)
        success = self.writeSerialData(ser, package, verbose=verbose)
        return success

    # SEND ALL SETPOINTS
    def send_PG_pulsetimes(self, ser, repRate=5000, frequency=0, pulseLength=75, onTime=248, verbose=0):
        package = self.PG_CraftPackage_setTimes(repRate, frequency, pulseLength, onTime, verbose)
        success = self.writeSerialData(ser, package, verbose=verbose)
        return success

    # READS AND RESTRUCTURES PG DATA (ACCORDING TO DIFFERENT DATA-TYPES)
    def read_PG_data(self, ser, verbose=0):
        serData, crcStatus, _ = self.readSerialData(ser, verbose)

        # CHECK IF CRC IS CORRECT
        if not crcStatus:
            return 0, False
        
        # TAKE THE FIRST 4 BYTES AND UNPACK THEM AS 2x UINT16
        crc, datatype = struct.unpack('<HH', serData[:4])

        # CHECK THE STATUS AND PACK IT ACCORDINGLY (SEE TABLE FOR DATA STRUCTURE)
        
        # PulseDataEnd
        if datatype == PG_TYPE_DATAEND:
            return 0, datatype, crcStatus

        # PulseDataStart
        elif datatype == PG_TYPE_DATASTART:
            data_fmt = '<' + 'I'*15         # 15 TIMES UINT32              

        # PulseData, ZeroData
        elif datatype in (PG_TYPE_PULSEDATA, PG_TYPE_ZERODATA):              
            data_fmt = '<' + 'H'*30         # 30 TIMES UINT16 

        else:
            data_fmt = '<' + 'H'*30
            if verbose: print('Invalid status value: {}'.format(datatype))

        # CREATE THE ARRAY (UINT8/16/32 DEPENDING ON THE SIZE)
        pgData = np.array(struct.unpack(data_fmt, serData[4:]), dtype=np.uint32 if datatype == PG_TYPE_DATASTART else np.uint16)

        # DELETE ZEROS, IF DATASTRUCTURE IS PLANNED TO BE EMPTY
        if datatype in (PG_TYPE_DATASTART, PG_TYPE_ZERODATA):
            pgData = pgData[pgData != 0]

        return pgData, datatype, crcStatus

    def read_next_PG_pulse(self, ser, timeout=0, verbose=0):
        dtype = 0
        ser.flushInput()

        # Accumulate data here
        all_data = np.empty(0)

        while dtype != PG_TYPE_DATASTART:
            PG_data, dtype, _ = self.read_PG_data(ser)

        if verbose: print("PULSE START RECEIVED")

        # READ ALL PULSE-DATA-ARRAYS UNTIL "DATA END" IS RECEIVED
        while dtype != PG_TYPE_DATAEND:
            PG_data, dtype, _ = self.read_PG_data(ser)

            if dtype == PG_TYPE_PULSEDATA:
                all_data = np.concatenate((all_data, PG_data))

        if verbose: print("PULSE END RECEIVED")

        # Split the data into voltage and current
        half_len = len(all_data) // 2
        voltageData = all_data[:half_len]
        currentData = all_data[half_len:]

        # Combine voltage and current data into two columns
        pulseData = np.column_stack((voltageData, currentData))

        return pulseData, half_len

class PowerSupplyUnitSerialWorker(QObject):

    def __init__(self, power_supply_unit_serial):
        super(PowerSupplyUnitSerialWorker, self).__init__()
        self.power_supply_unit_serial = power_supply_unit_serial 
        self._lock = QMutex()
        self._def_crc16_table()

    @pyqtSlot()
    def stop(self):
        self._lock.lock()
        self._is_running = False
        self._lock.unlock()

    def _def_crc16_table(self): 
        self.crc16_table = [
            0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
            0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
            0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
            0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
            0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
            0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
            0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
            0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
            0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
            0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
            0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
            0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
            0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
            0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
            0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
            0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
            0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
            0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
            0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
            0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
            0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
            0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
            0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
            0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
            0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
            0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
            0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
            0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
            0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
            0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
            0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
            0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040
        ]

    def crc16(self, buffer_uint8, crc=0):

        for byte in buffer_uint8:
            crc = (crc >> 8) ^ self.crc16_table[(crc ^ byte) & 0xff]
        return crc
    
    def testCRC(self, binaryData, verbose=0):

        if verbose: print("----------------- START: TEST CRC -----------------")        # PRINT FORMATTING

        crc_check = False

        # CHECK IF BINARY DATA IS AVAILABLE
        if not binaryData:
            if verbose: print("No binary data available.")
            return crc_check, None

        # GET AND CALCULATE THE CRC VALUES
        try:
            arr = np.array(struct.unpack('<' + 'H' * (len(binaryData) // 2), binaryData))   # CREATE DATA ARRAY (uint16) 
            dataCRC = arr[0]                                                                # GET CRC VALUE FROM THE ARRAY
            calcCRC = self.crc16(np.frombuffer(binaryData[2:], dtype=np.uint8))              	# CALCULATE CRC VALUE ACCORDING TO DATA

            if verbose >1: print("DATA AS ARRAY:\n{}".format(arr))                          # PRINT FORMATTING
            if verbose: print("CRC IN DATA:\t\t{}".format(dataCRC))                         # PRINT FORMATTING
            if verbose: print("CRC CALCULATED:\t{}".format(calcCRC))                        # PRINT FORMATTING
            
            # CRC CHECK
            if dataCRC == calcCRC:
                crc_check = True
            
            if verbose: print("CRC CHECK:\t\t{}".format(crc_check))                         # PRINT FORMATTING
            if verbose: print("----------------- END: TEST CRC -----------------")          # PRINT FORMATTING
        
        except struct.error as e:
            if verbose: print(f"Error unpacking binaryData: {e}")
            return crc_check, None
        
        # RETURN DATA
        return crc_check, calcCRC
    
    def CraftPackage_run(self, verbose=0):
        payload = np.array([
            0x0003              # Start Command 
            ], dtype=np.uint16) # data type as uint16 (16 bit)

        # FILL IT WITH 0s THAT IT HAS A SIZE OF 31 UINT16 (1 left for CRC)
        datapacket = np.pad(payload, (0, 30), mode='constant')

        # CREATE A BYTE REPRESENTATION FOR CRC CALCULATION
        byte_datapacket = datapacket.tobytes()

        # CALCULATE CRC
        crc = self.crc16(np.frombuffer(byte_datapacket, dtype=np.uint8))

        # CREATE COMPLETE ARRAY FOR USB DATA
        sendable_arr = np.insert(datapacket, 0, crc)

        # CREATE A BYTE REPRESENTATION FOR USB DATA
        sendable_bytedata = sendable_arr.tobytes()
        if verbose: print(sendable_bytedata)

        # TEST THE CRC AND SET DATA TO 0 IF CRC IS WRONG
        crc_check, _ = self.testCRC(sendable_bytedata, verbose)
        if not crc_check: sendable_bytedata = 0

        return sendable_bytedata
    
    def CraftPackage_stop(self, verbose=0):
        payload = np.array([
            0x0004              # Stop Command 
            ], dtype=np.uint16) # data type as uint16 (16 bit)

        # FILL IT WITH 0s THAT IT HAS A SIZE OF 31 UINT16 (1 left for CRC)
        datapacket = np.pad(payload, (0, 30), mode='constant')

        # CREATE A BYTE REPRESENTATION FOR CRC CALCULATION
        byte_datapacket = datapacket.tobytes()

        # CALCULATE CRC
        crc = self.crc16(np.frombuffer(byte_datapacket, dtype=np.uint8))

        # CREATE COMPLETE ARRAY FOR USB DATA
        sendable_arr = np.insert(datapacket, 0, crc)

        # CREATE A BYTE REPRESENTATION FOR USB DATA
        sendable_bytedata = sendable_arr.tobytes()
        if verbose: print(sendable_bytedata)

        # TEST THE CRC AND SET DATA TO 0 IF CRC IS WRONG
        crc_check, _ = self.testCRC(sendable_bytedata, verbose)
        if not crc_check: sendable_bytedata = 0

        return sendable_bytedata

    def readSerialData(self, ser, verbose=0):
        if verbose: print("==================== START: READING ====================")      # PRINT FORMATTING

        serialData = ser.read(64)                                   # READ 64 BYTES OF THE DATA STREAM (= 1 PACKET)
        crc_status, crc_value = self.testCRC(serialData, verbose)        # CHECK THE CRC AND RETURN THE CRC-VALUE

        # SHOW ERROR MESSAGE, IF CRC IS WRONG
        if not crc_status:
            print("CRC Error with received data!")

        if verbose: print("==================== END: READING ====================")      # PRINT FORMATTING
        return serialData, crc_status, crc_value

    def writeSerialData(self, ser, data_to_send, num_attempts=NUM_ATTEMPTS, verbose=0):

        if verbose: print("--- fct: writeSerialData ---")
        success = False
        
        for i in range(num_attempts):
            try:
                ser.flushOutput()
                ser.flushInput()
                time.sleep(0.25)
                ser.write(data_to_send)
                success = True
                if verbose: print('Data sent successfully')
                break  # if data was sent successfully, exit the loop
            except serial.SerialTimeoutException:
                if verbose: print(f'Timeout occurred while sending data. Attempt {i+1}/{num_attempts}')
                time.sleep(0.5)  # wait for a short time before attempting again
        
        if verbose: print("--- end: writeSerialData ---")
        return success
    
    def PSU_CraftPackage_setSetpoints(self, posVoltVal, negVoltVal, verbose=0):

        # DATA CHECKS AND PREPARATIONS
        posVoltVal = round(posVoltVal)
        negVoltVal = round(abs(negVoltVal))

        if posVoltVal > 95: posVoltVal = 95
        elif posVoltVal < 12: posVoltVal = 12

        if negVoltVal > 95: negVoltVal = 95
        elif negVoltVal < 0: negVoltVal = 0

        # CRAFT PAYLOAD ARRAY (uint16)
        payload = np.array([
            0x0001,             # SetSetpoints Command 
            posVoltVal,         # posValue
            negVoltVal,         # negValue
            ], dtype=np.uint16) # data type as uint16 (16 bit)

        # FILL IT WITH 0s THAT IT HAS A SIZE OF 31 UINT16 (1 left for CRC)
        datapacket = np.pad(payload, (0, 28), mode='constant')

        # CREATE A BYTE REPRESENTATION FOR CRC CALCULATION
        byte_datapacket = datapacket.tobytes()

        # CALCULATE CRC
        crc = self.crc16(np.frombuffer(byte_datapacket, dtype=np.uint8))

        # CREATE COMPLETE ARRAY FOR USB DATA
        sendable_arr = np.insert(datapacket, 0, crc)

        # CREATE A BYTE REPRESENTATION FOR USB DATA
        sendable_bytedata = sendable_arr.tobytes()
        if verbose: print(sendable_bytedata)

        # TEST THE CRC AND SET DATA TO 0 IF CRC IS WRONG
        crc_check, _ = self.testCRC(sendable_bytedata, verbose)
        if not crc_check: sendable_bytedata = 0

        return sendable_bytedata
    # START THE PSU
    def start_psu(self): 
        self._lock.lock()
        try:
            self.send_PSU_enable(self.power_supply_unit_serial.serial_device, 0)
        except Exception as e:
            print(f"Error in start_psu: {e}")  # or handle the error in a more appropriate way
        finally:
            self._lock.unlock()  # Ensure the lock is always released

    def send_PSU_enable(self, ser, verbose=0):
        package = self.CraftPackage_run(verbose)
        success = self.writeSerialData(ser, package, verbose=verbose)
        return success

    # STOP THE PSU
    def send_PSU_disable(self, ser, verbose=0):
        package = self.CraftPackage_stop(verbose)
        success = self.writeSerialData(ser, package, verbose=verbose)
        return success

    def stop_psu(self): 
        self._lock.lock()
        try:
            self.send_PSU_disable(self.power_supply_unit_serial.serial_device, 0)
        except Exception as e:
            print(f"Error in stop_psu: {e}")  # or handle the error in a more appropriate way
        finally:
            self._lock.unlock()  # Ensure the lock is always released
    # SEND ALL SETPOINTS
    def send_PSU_setpoints(self, ser, posVoltage, negVoltage, verbose=0):
        package = self.PSU_CraftPackage_setSetpoints(posVoltage, negVoltage, verbose)
        self._lock.lock()
        try: 
            success = self.writeSerialData(ser, package, verbose=verbose)
            return success
        except Exception as e: 
            print(f"error in send_PSU_setpoints: {e}")
        finally: 
            self._lock.unlock()

    # READS AND RESTRUCTURES PSU DATA
    def read_PSU_data(self, ser, verbose=0):

        # READ SERIAL DATA FROM PSU
        serData, crcStatus, _ = self.readSerialData(ser, verbose)

        # CHECK IF CRC IS CORRECT
        if not crcStatus:
            return 0, False

        # CONSTRUCT UINT16 ARRAY AND JUST KEEP THE FIRST 9 ENTRIES (EVERYTHING ELSE IS 0 ANYWAYS).
        psuData = np.array(struct.unpack('<' + 'H' * (len(serData) // 2), serData))[:9]

        return psuData, crcStatus

class PeristalticDriverWorker(QObject):
    stop_sucrose = pyqtSignal(bool)
    stop_ethanol = pyqtSignal(bool)

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
        #print(f"Raw line received: {line}")
        if line == "Motor 1 has reached its target position.": 
            #print('sending ethanol stop')
            self.stop_ethanol.emit(1)

        elif line == "Motor 2 has reached its target position.": 
            #print('sending sucrose stop')
            self.stop_sucrose.emit(1)

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