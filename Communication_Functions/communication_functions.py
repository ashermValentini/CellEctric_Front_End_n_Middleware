'''
This module contains all functions needed to communicate with the CELLECTRIC BIOSCIENCES serial communication modules (PSU, PG, 3PAC, Temperature sensor, and Pressure Sensor).
'''

import serial                       # communication with the board
from serial.tools import list_ports # check all ports to automatically detect devices
import numpy as np                  # because science
import struct                       # needed for CRC Check (unpacking bytes to array)
import time                         # to sleep
import matplotlib.pyplot as plt     # to print stuff nicely
import minimalmodbus                # speceific to the temp sensor

__author__ = "Nicolas Heimburger Asher Valentini"
__version__ = "1.0.0"
__status__ = "Production"

# IDs FOR ALL BOARDS AND DEVICES
SERIAL_VENDOR_ID = 0x6666           # VENDOR ID FROM HANS
SERIAL_PSU_PRODUCT_ID = 0x0100      # PSU PRODUCT ID FROM HANS
SERIAL_PG_PRODUCT_ID = 0x0200       # PG PRODUCT ID FROM HANS
SERIAL_TEMPSENS_VENDOR_ID = 0x0403  # TEMPERATURE-SENSOR VENDOR ID
SERIAL_TEMPSENS_PRODUCT_ID = 0x6015 # TEMPERATURE-SENSOR PRODUCT ID

# CONSTANTS
NUM_ATTEMPTS = 5
PSU_TYPE_PACKET = 0x1000
PG_TYPE_DATASTART = 0x1000
PG_TYPE_DATAEND = 0x1001
PG_TYPE_PULSEDATA = 0x1002
PG_TYPE_ZERODATA = 0x1003

# ======================================================================================================================================================================
# .___________. __    __   _______     _______. _______         ___      .______       _______    .__   __.   ______   .___________.   .___________. __    __   _______  
# |           ||  |  |  | |   ____|   /       ||   ____|       /   \     |   _  \     |   ____|   |  \ |  |  /  __  \  |           |   |           ||  |  |  | |   ____| 
# `---|  |----`|  |__|  | |  |__     |   (----`|  |__         /  ^  \    |  |_)  |    |  |__      |   \|  | |  |  |  | `---|  |----`   `---|  |----`|  |__|  | |  |__    
#     |  |     |   __   | |   __|     \   \    |   __|       /  /_\  \   |      /     |   __|     |  . `  | |  |  |  |     |  |            |  |     |   __   | |   __|   
#     |  |     |  |  |  | |  |____.----)   |   |  |____     /  _____  \  |  |\  \----.|  |____    |  |\   | |  `--'  |     |  |            |  |     |  |  |  | |  |____  
#     |__|     |__|  |__| |_______|_______/    |_______|   /__/     \__\ | _| `._____||_______|   |__| \__|  \______/      |__|            |__|     |__|  |__| |_______| 
#                                                                                                                                                                        
#  _______  __    __  .__   __.   ______ .___________. __    ______   .__   __.      _______.   ____    ____  ______    __    __          ___      .______       _______ 
# |   ____||  |  |  | |  \ |  |  /      ||           ||  |  /  __  \  |  \ |  |     /       |   \   \  /   / /  __  \  |  |  |  |        /   \     |   _  \     |   ____|
# |  |__   |  |  |  | |   \|  | |  ,----'`---|  |----`|  | |  |  |  | |   \|  |    |   (----`    \   \/   / |  |  |  | |  |  |  |       /  ^  \    |  |_)  |    |  |__   
# |   __|  |  |  |  | |  . `  | |  |         |  |     |  | |  |  |  | |  . `  |     \   \         \_    _/  |  |  |  | |  |  |  |      /  /_\  \   |      /     |   __|  
# |  |     |  `--'  | |  |\   | |  `----.    |  |     |  | |  `--'  | |  |\   | .----)   |          |  |    |  `--'  | |  `--'  |     /  _____  \  |  |\  \----.|  |____ 
# |__|      \______/  |__| \__|  \______|    |__|     |__|  \______/  |__| \__| |_______/           |__|     \______/   \______/     /__/     \__\ | _| `._____||_______|
#                                                                                                                                                                        
#  __        ______     ______    __  ___  __  .__   __.   _______     _______   ______   .______                                                                        
# |  |      /  __  \   /  __  \  |  |/  / |  | |  \ |  |  /  _____|   |   ____| /  __  \  |   _  \                                                                       
# |  |     |  |  |  | |  |  |  | |  '  /  |  | |   \|  | |  |  __     |  |__   |  |  |  | |  |_)  |                                                                      
# |  |     |  |  |  | |  |  |  | |    <   |  | |  . `  | |  | |_ |    |   __|  |  |  |  | |      /                                                                       
# |  `----.|  `--'  | |  `--'  | |  .  \  |  | |  |\   | |  |__| |    |  |     |  `--'  | |  |\  \----.    __     __     __
# |_______| \______/   \______/  |__|\__\ |__| |__| \__|  \______|    |__|      \______/  | _| `._____|   (__)   (__)   (__)
#
# ======================================================================================================================================================================
# source: https://patorjk.oftware/taag/#p=display&f=Star%20Wars&t=text
# style: Star Wars


# ===============================================================
# ======================== FUNCTIONS: CRC =======================
# ===============================================================

#region: 
# CRC TABLE FOR CRC CALCULATION
crc16_table = [
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

# FUNCTION FOR CRC CALCULATION (Python implementation of Hans' Code)
def crc16(buffer_uint8, crc=0):
    '''
    Returns the calculated crc data depending on the buffer-data.

        Parameters:
                buffer_uint8 (uint8):	uint8 array of data which is needed to calculate the crc from

                crc (int):    			a predefined crc 
                                        DEFAULT: 0 
                                        NOTE: this is not needed most of the time

        Returns:
                crc (int):				calculated crc value
    '''
    for byte in buffer_uint8:
        crc = (crc >> 8) ^ crc16_table[(crc ^ byte) & 0xff]
    return crc

# FUNCTION TO TEST THE CRC OF A COMPLETE DATA PACKAGE
def testCRC(binaryData, verbose=0):
    '''
    Checks if the crc within the data packet is correct and returns a flag and the crc.

        Parameters:
                binaryData (String):	Serial Data (byte) that includes crc (first uint16)

                verbose (int):      	0.. printing OFF, 1.. basic printing, 2.. print ALL
                                        DEFAULT: 0
                                        
        Returns:
                crc_check (bool):		status of the crc test (True = OK)
                calc_crc (int):			the calculated crc value of the data itself
    '''
    if verbose: print("----------------- START: TEST CRC -----------------")        # PRINT FORMATTING

    crc_check = False
    # GET AND CALCULATE THE CRC VALUES
    arr = np.array(struct.unpack('<' + 'H' * (len(binaryData) // 2), binaryData))   # CREATE DATA ARRAY (uint16) 
    dataCRC = arr[0]                                                                # GET CRC VALUE FROM THE ARRAY
    calcCRC = crc16(np.frombuffer(binaryData[2:], dtype=np.uint8))              	# CALCULATE CRC VALUE ACCORDING TO DATA

    if verbose >1: print("DATA AS ARRAY:\n{}".format(arr))                          # PRINT FORMATTING
    if verbose: print("CRC IN DATA:\t\t{}".format(dataCRC))                         # PRINT FORMATTING
    if verbose: print("CRC CALCULATED:\t{}".format(calcCRC))                        # PRINT FORMATTING
    
    # CRC CHECK
    if dataCRC == calcCRC:
        crc_check = True
    
    if verbose: print("CRC CHECK:\t\t{}".format(crc_check))                         # PRINT FORMATTING
    if verbose: print("----------------- END: TEST CRC -----------------")          # PRINT FORMATTING
    
    # RETURN DATA
    return crc_check, calcCRC

#endregion

# ===============================================================
# ====================== FUNCTIONS: SERIAL ======================
# ===============================================================

#region

# FIND SERIAL PORT DEPENDING ON VENDOR_ID AND PRODUCT_ID
def find_serial_port(vendor_id, product_id):
    '''
    Finds and returns the serial device (pyserial) for the specific vendor_id and product_id.

        Parameters:
                vendor_id (hex):    HEX value of the vendor-ID of the device 
                
                product_id (hex):   HEX value of the product-ID of the device 

        Returns:
                ser (str):	Device (e.g. "COM12")
    '''
    serial = None

    # LIST ALL COM PORTS
    ports = list_ports.comports()

    # SEARCH FOR IDs IN ALL COM PORTS. IF FOUND, RETURN DEVICE
    for port in ports:
        try: 
            if port.vid == vendor_id and port.pid == product_id:
                serial = port.device
        except Exception as error:
            print("An exception occurred while searching for ports:", error)

    #if serial == None:
    #    raise Exception("Could not find the device: Vendor-ID: {}, Product-ID: {}".format(hex(vendor_id), hex(product_id)))
    
    return serial


# FIND PORT OF ESP32
def find_esp(port=None):
    """Get the name of the port that is connected to the ESP32."""
    if port is None:
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if p.manufacturer is not None and "Silicon" in p.manufacturer:  # "Silicon" is in the name of the ESP32 manufacturer
                port = p.device
    return port

# ESTABLISH ALL SERIAL CONNECTIONS TO DEVICES IN THE LIST
def establish_serial_connections(com_list):
    '''
    Establishes a serial communication (pyserial) with the chosen devices in the list and returns a list of "Serial"-objects.

        Parameters:
                com_list:   List of devices to connect to (e.g. "COM12") 

        Returns:
                serials (Serial[]):	Array of Serial-objects with established connection and connection details (baud rate, timeout, etc.) --> see "pyserial"
    '''
    serials = []

    for i, com_port in enumerate(com_list):
        try:
            if i == 2:  # Check if it's the third COM port ie this is the 3PAC which for some reason hates to be spoken to on a 9600 baudrate setting
                ser = serial.Serial(com_port, 115200, write_timeout=5)
            else:
                ser = serial.Serial(com_port, 9600, write_timeout=5)
            serials.append(ser)
        except:
            raise Exception("Could not establish a connection to the port {}".format(com_port))

    return serials


# FUNCTION TO READ AND PRINT SERIAL DATA FROM CONNECTED DEVICE
def readSerialData(ser, verbose=0):
    '''
    Reads serial data from device and returns read data, crc value and crc status.

        Parameters:
                ser:      			Reference to serial connection to the device (pyserial) 
                
                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 0

        Returns:
                serialData (str):	Data gathered from the device (64 Bytes)
                
                crc_status (bool):	Flag, if the CRC is correct
                
                crc_value (int): 	Value of the CRC
    '''
    if verbose: print("==================== START: READING ====================")      # PRINT FORMATTING

    serialData = ser.read(64)                                   # READ 64 BYTES OF THE DATA STREAM (= 1 PACKET)
    crc_status, crc_value = testCRC(serialData, verbose)        # CHECK THE CRC AND RETURN THE CRC-VALUE

    # SHOW ERROR MESSAGE, IF CRC IS WRONG
    if not crc_status:
        print("CRC Error with received data!")

    if verbose: print("==================== END: READING ====================")      # PRINT FORMATTING
    return serialData, crc_status, crc_value

# FUNCTION TO TRY WRITING TO SERIAL X TIMES
def writeSerialData(ser, data_to_send, num_attempts=NUM_ATTEMPTS, verbose=0):
    '''
    Writes serial data to the device.

        Parameters:
                ser:      			Reference to serial connection to the device (pyserial) 
                
                data_to_send (str):	Datapacket that needs to be sent (already converted to bytes)
                
                num_attempts (int):	Number of sending attempts (sometimes sending does not work right away)
                                    DEFAULT: 5
                
                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 0
                
        Returns:
                success (bool):    Flag to show the status of the package (sending done and OK = TRUE)
    '''
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

#endregion

# ===============================================================
# =============== FUNCTIONS: PREPARE DATA PACKETS ===============
# ===============================================================

#region

# CRAFT RUN PACKAGE FOR PSU
def CraftPackage_run(verbose=0):
    '''
    PSU or PG RUN: Returns the crafted byte-packet including crc. READY TO SEND.

        Parameters:
                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 

        Returns:
                sendable_bytedata (str): final byte packet
    '''
    payload = np.array([
        0x0003              # Start Command 
        ], dtype=np.uint16) # data type as uint16 (16 bit)

    # FILL IT WITH 0s THAT IT HAS A SIZE OF 31 UINT16 (1 left for CRC)
    datapacket = np.pad(payload, (0, 30), mode='constant')

    # CREATE A BYTE REPRESENTATION FOR CRC CALCULATION
    byte_datapacket = datapacket.tobytes()

    # CALCULATE CRC
    crc = crc16(np.frombuffer(byte_datapacket, dtype=np.uint8))

    # CREATE COMPLETE ARRAY FOR USB DATA
    sendable_arr = np.insert(datapacket, 0, crc)

    # CREATE A BYTE REPRESENTATION FOR USB DATA
    sendable_bytedata = sendable_arr.tobytes()
    if verbose: print(sendable_bytedata)

    # TEST THE CRC AND SET DATA TO 0 IF CRC IS WRONG
    crc_check, _ = testCRC(sendable_bytedata, verbose)
    if not crc_check: sendable_bytedata = 0

    return sendable_bytedata

# CRAFT STOP PACKAGE FOR PSU
def CraftPackage_stop(verbose=0):
    '''
    PSU or PG STOP: Returns the crafted byte-packet including crc. READY TO SEND.

        Parameters:
                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 

        Returns:
                sendable_bytedata (str): final byte packet
    '''
    payload = np.array([
        0x0004              # Stop Command 
        ], dtype=np.uint16) # data type as uint16 (16 bit)

    # FILL IT WITH 0s THAT IT HAS A SIZE OF 31 UINT16 (1 left for CRC)
    datapacket = np.pad(payload, (0, 30), mode='constant')

    # CREATE A BYTE REPRESENTATION FOR CRC CALCULATION
    byte_datapacket = datapacket.tobytes()

    # CALCULATE CRC
    crc = crc16(np.frombuffer(byte_datapacket, dtype=np.uint8))

    # CREATE COMPLETE ARRAY FOR USB DATA
    sendable_arr = np.insert(datapacket, 0, crc)

    # CREATE A BYTE REPRESENTATION FOR USB DATA
    sendable_bytedata = sendable_arr.tobytes()
    if verbose: print(sendable_bytedata)

    # TEST THE CRC AND SET DATA TO 0 IF CRC IS WRONG
    crc_check, _ = testCRC(sendable_bytedata, verbose)
    if not crc_check: sendable_bytedata = 0

    return sendable_bytedata

# CRAFT SETPOINT PACKAGE FOR PSU
def PSU_CraftPackage_setSetpoints(posVoltVal, negVoltVal, verbose=0):
    '''
    PSU SET SETPOINTS: Returns the crafted byte-packet including crc. READY TO SEND.

        Parameters:
                posVoltVal (int):   Positive PSU Voltage (V)                [12 .. 95]
                                    NOTE: Positive voltage cannot go lower than 12V. For 0V PSU needs to be disabled!

                negVoltVal (int):   Negative PSU Voltage (V)                [0 .. 95]

                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 

        Returns:
                sendable_bytedata (str): final byte packet
    '''
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
    crc = crc16(np.frombuffer(byte_datapacket, dtype=np.uint8))

    # CREATE COMPLETE ARRAY FOR USB DATA
    sendable_arr = np.insert(datapacket, 0, crc)

    # CREATE A BYTE REPRESENTATION FOR USB DATA
    sendable_bytedata = sendable_arr.tobytes()
    if verbose: print(sendable_bytedata)

    # TEST THE CRC AND SET DATA TO 0 IF CRC IS WRONG
    crc_check, _ = testCRC(sendable_bytedata, verbose)
    if not crc_check: sendable_bytedata = 0

    return sendable_bytedata

# CRAFT PULSE PACKAGE FOR PG
def PG_CraftPackage_setTimes(repRate=5000, frequency=0 ,pulseLength=75, onTime=248, verbose=0):
    '''
    PG SET TIMES: Returns the crafted byte-packet including crc. READY TO SEND.

        Parameters:
                repRate (int):      Time between pulses (us)                [750 .. inf]
                                    DEFAULT: 5000 (every 5000us --> 200Hz)

                frequency (int):    Frequency for pulses (HZ)               [1 .. 1300]
                                    DEFAULT: 0 
                                    NOTE: (if it is set, this value has more importance than repRate!)

                pulseLength (int):  Length of the positive pulse (us)       [10 .. 250]
                                    DEFAULT: 75

                onTime (int):       Time of the Transistor being ON (us)    [5 .. pulseLength-2]
                                    DEFAULT: 248 (is the maximum possible value. Gets capped anyways due to the pulseLength)

                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 

        Returns:
                sendable_bytedata (str): final byte packet
    '''
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
    crc = crc16(np.frombuffer(byte_datapacket, dtype=np.uint8))

    # CREATE COMPLETE ARRAY FOR USB DATA
    sendable_arr = np.insert(datapacket, 0, crc)

    # CREATE A BYTE REPRESENTATION FOR USB DATA
    sendable_bytedata = sendable_arr.tobytes()
    if verbose: print(sendable_bytedata)

    # TEST THE CRC AND SET DATA TO 0 IF CRC IS WRONG
    crc_check, _ = testCRC(sendable_bytedata, verbose)
    if not crc_check: sendable_bytedata = 0

    return sendable_bytedata


#endregion

# ===========================================================================================================================================================
#  _______  __    __  .__   __.   ______ .___________. __    ______   .__   __.      _______.   .___________.  ______       __    __       _______. _______ 
# |   ____||  |  |  | |  \ |  |  /      ||           ||  |  /  __  \  |  \ |  |     /       |   |           | /  __  \     |  |  |  |     /       ||   ____|
# |  |__   |  |  |  | |   \|  | |  ,----'`---|  |----`|  | |  |  |  | |   \|  |    |   (----`   `---|  |----`|  |  |  |    |  |  |  |    |   (----`|  |__   
# |   __|  |  |  |  | |  . `  | |  |         |  |     |  | |  |  |  | |  . `  |     \   \           |  |     |  |  |  |    |  |  |  |     \   \    |   __|  
# |  |     |  `--'  | |  |\   | |  `----.    |  |     |  | |  `--'  | |  |\   | .----)   |          |  |     |  `--'  |    |  `--'  | .----)   |   |  |____ 
# |__|      \______/  |__| \__|  \______|    |__|     |__|  \______/  |__| \__| |_______/           |__|      \______/      \______/  |_______/    |_______|
#                                                                                                                                                           
# ===========================================================================================================================================================

# ===============================================================
#      _______. _______ .______       __       ___       __      
#     /       ||   ____||   _  \     |  |     /   \     |  |     
#    |   (----`|  |__   |  |_)  |    |  |    /  ^  \    |  |     
#     \   \    |   __|  |      /     |  |   /  /_\  \   |  |     
# .----)   |   |  |____ |  |\  \----.|  |  /  _____  \  |  `----.
# |_______/    |_______|| _| `._____||__| /__/     \__\ |_______|
#                                                               
# ===============================================================

#region

# START THE CONNECTION TO THE PSU AND THE PG
def serial_start_connections(verbose=0):
    '''
    Starts all serial communication (pyserial) with the PSU and the PG.

        Parameters:
                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
        
        returns:
                my_serials (dict):  A dictionary of the serial connections. KEYS: ["psu_serial", "pg_serial"]
    '''
    # FIND SERIAL PORTS OF THE DEVICES AND PUT IT INTO A LIST
    
    pac_serial=None
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if p.manufacturer is not None and "Silicon" in p.manufacturer:  # "Silicon" is in the name of the ESP32 manufacturer
            pac_serial = p.device
    
    psu_serial = find_serial_port(SERIAL_VENDOR_ID, SERIAL_PSU_PRODUCT_ID)
    pg_serial = find_serial_port(SERIAL_VENDOR_ID, SERIAL_PG_PRODUCT_ID)
    
    com_list = [psu_serial, pg_serial, pac_serial]
    if verbose: print(com_list)

    # ESTABLISH ALL SERIAL CONNECTIONS (OR RETURN FALSE, IF NOT POSSIBLE)
    my_serials = establish_serial_connections(com_list)
    if my_serials == False:
        return False

    temperature_port = find_serial_port(SERIAL_TEMPSENS_VENDOR_ID, SERIAL_TEMPSENS_PRODUCT_ID)
    if not temperature_port:
        temperature_port=None
    
    temp_sensor=None
    if temperature_port is not None:
        temp_sensor = minimalmodbus.Instrument(temperature_port, 1) 
        temp_sensor.serial.baudrate = 9600
        temp_sensor.serial.bytesize = 8
        temp_sensor.serial.parity = serial.PARITY_NONE
        temp_sensor.serial.stopbits = 1
        temp_sensor.serial.timeout = 0.1
        temp_sensor.mode = minimalmodbus.MODE_RTU

    my_serials.append(temp_sensor)
    
    # PRINT STUFF
    if verbose:
        print("SERIAL CONNECTIONS FOUND AND ESTABLISHED:")
        for connection in com_list:
            print(connection)
        print("---------------------------------------------")
    print(my_serials)
    return my_serials

# CLOSE THE CONNECTION TO THE PSU AND THE PG
def serial_close_connections(ser_list, verbose=0):
    '''
    Closes all serial communication (pyserial) with the chosen "Serial"-objects in a list.

        Parameters:
                ser_list:           List of Serial-objects to close the connection
        
        returns:
                success (bool):    Flag to show the status of the package (sending done and OK = TRUE)
    '''
    success = True
    for serial_element in ser_list:
        try:
            serial_element.close()
        except Exception as error:
            if verbose: print("An exception occurred:", error)
            success = False
    
    return success

#endregion

# ==============================
# .______     _______. __    __  
# |   _  \   /       ||  |  |  | 
# |  |_)  | |   (----`|  |  |  | 
# |   ___/   \   \    |  |  |  | 
# |  |   .----)   |   |  `--'  | 
# | _|   |_______/     \______/  
#                                 
# ==============================

#region

# COMMUNICATION WITH THE POWER SUPPLY UNIT

# START THE PSU
def send_PSU_enable(ser, verbose=0):
    '''
    Crafts and sends the command to the PSU to START (enable with currently stored setpoints).
    NOTE: It is recommended to set the setpoints before calling this function.

        Parameters:
                ser:      			Reference to serial connection to the device (pyserial) 
                
                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 0
                
        Returns:
                success (bool):    Flag to show the status of the package (sending done and OK = TRUE)
    '''
    package = CraftPackage_run(verbose)
    success = writeSerialData(ser, package, verbose=verbose)
    return success

# STOP THE PSU
def send_PSU_disable(ser, verbose=0):
    '''
    Crafts and sends the command to the PSU to STOP.

        Parameters:
                ser:      			Reference to serial connection to the device (pyserial) 
                
                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 0
                
        Returns:
                success (bool):    Flag to show the status of the package (sending done and OK = TRUE)
    '''
    package = CraftPackage_stop(verbose)
    success = writeSerialData(ser, package, verbose=verbose)
    return success

# SEND ALL SETPOINTS
def send_PSU_setpoints(ser, posVoltage, negVoltage, verbose=0):
    '''
    Crafts and sends the command to set the voltage-setpoints of the PSU.
    NOTE: This does not enable the psu. To enable it, use send_PSU_enable() command.

        Parameters:
                ser:      			Reference to serial connection to the device (pyserial) 

                posVoltage (int):   Voltage level of the positive output voltage

                negVoltage (int):   Voltage level of the negative output voltage
                
                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 0
                
        Returns:
                success (bool):    Flag to show the status of the package (sending done and OK = TRUE)
    '''
    package = PSU_CraftPackage_setSetpoints(posVoltage, negVoltage, verbose)
    success = writeSerialData(ser, package, verbose=verbose)
    return success

# READS AND RESTRUCTURES PSU DATA
def read_PSU_data(ser, verbose=0):
    '''
    Reads serial data (single line) from PSU (from specified serial port) and restructures the message according to the datasheet.

        Parameters:
                ser:      			Reference to serial connection to the device (pyserial) 
                
                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 0
                
        Returns:
                success (bool):    Flag to show the status of the package (sending done and OK = TRUE)
    '''
    # READ SERIAL DATA FROM PSU
    serData, crcStatus, _ = readSerialData(ser, verbose)

    # CHECK IF CRC IS CORRECT
    if not crcStatus:
        return 0, False

    # CONSTRUCT UINT16 ARRAY AND JUST KEEP THE FIRST 9 ENTRIES (EVERYTHING ELSE IS 0 ANYWAYS).
    psuData = np.array(struct.unpack('<' + 'H' * (len(serData) // 2), serData))[:9]

    return psuData, crcStatus

#endregion

# ====================
# .______     _______ 
# |   _  \   /  _____|
# |  |_)  | |  |  __  
# |   ___/  |  | |_ | 
# |  |      |  |__| | 
# | _|       \______| 
#                               
# ====================

#region

# COMMUNICATION WITH THE PULSE GENERATOR
# ENABLES THE PG AND READS THE NEXT RETURN VALUES TO GET "ZEROCURRENT" AND "ZEROVOLTAGE"
def send_PG_enable(ser, verbose=0):
    '''
    Crafts and sends the enable command to the Pulse Generator and waits for the "zero data" response.

        Parameters:
                ser:      			Reference to serial connection to the device (pyserial) 
                
                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 0
                
        Returns:
                zerodata (int[2]):  Numpy Array of the received "zero data" [Voltage, Current]
    '''
    # CRAFT ENABLE PACKET
    packet = CraftPackage_run()

    # SEND PACKET
    success = writeSerialData(ser, packet, verbose=verbose)
    if not success:
        if verbose: print("ERROR: Could not write serial data to PG to enable it.")
        return False

    # READ UNTIL TYPE == "ZEROVALUES" .. maybe not, because I don't receive this type of data
    type = 0
    while type != PG_TYPE_ZERODATA:
        if verbose: print("WAITING FOR ZERO DATA")
        PG_data, type, _= read_PG_data(ser)

    
    # [zeroVoltage, zeroCurrent]
    zerodata = [PG_data[0], PG_data[1]]

    return zerodata

# STOP THE PG
def send_PG_disable(ser, verbose=0):
    '''
    Crafts and sends the command to the PG to STOP.

        Parameters:
                ser:      			Reference to serial connection to the device (pyserial) 
                
                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 0
                
        Returns:
                success (bool):    Flag to show the status of the package (sending done and OK = TRUE)
    '''
    package = CraftPackage_stop(verbose)
    success = writeSerialData(ser, package, verbose=verbose)
    return success

# SEND ALL SETPOINTS
def send_PG_pulsetimes(ser, repRate=5000, frequency=0, pulseLength=75, onTime=248, verbose=0):
    '''
    Crafts and sends the times for the pulse to the PG. Returns the crafted byte-packet including crc.

        Parameters:
                repRate (int):      Time between pulses (us)                [750 .. inf]
                                    DEFAULT: 5000 (every 5000us --> 200Hz)

                frequency (int):    Frequency for pulses (HZ)               [1 .. 1300]
                                    DEFAULT: 0 
                                    NOTE: (if it is set, this value has more importance than repRate!)

                pulseLength (int):  Length of the positive pulse (us)       [10 .. 250]
                                    DEFAULT: 75

                onTime (int):       Time of the Transistor being ON (us)    [5 .. pulseLength-2]
                                    DEFAULT: 248 (is the maximum possible value. Gets capped anyways due to the pulseLength)

                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 

        Returns:
                success (bool):     final byte packet
    '''
    package = PG_CraftPackage_setTimes(repRate, frequency, pulseLength, onTime, verbose)
    success = writeSerialData(ser, package, verbose=verbose)
    return success

# READS AND RESTRUCTURES PG DATA (ACCORDING TO DIFFERENT DATA-TYPES)
def read_PG_data(ser, verbose=0):
    '''
    Reads serial data from PG (from specified serial port) and restructures the message according to the datasheet.

        Parameters:
                ser:      			Reference to serial connection to the device (pyserial) 
                
                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 0
                
        Returns:
                pgData (numpy array):   Numpy Array of the Data from the PG according to the type of data (structure: see datasheet)
                                        NOTE:   START:  0x1000: [PulseDataLength]                                   length: 15
                                                END:    0x1001: 0                                                   length: 30 (can be ignored)
                                                DATA:   0x1002: [Voltage1, Current1, ... , Voltage15, Current15]    length: 30
                                                ZERO:   0x1003: [ZeroVoltage, ZeroCurrent, 'status', 'p_setpoint', 'p_value', 'n_setpoint', 'n_value', 'p_current', 'n_current']

                datatype (int (hex)):   Datatype of the received array (see datasheet)                  

                crcStatus (bool):       Flag to show the status of the received packet (CRC == True --> OK)
    '''
    serData, crcStatus, _ = readSerialData(ser, verbose)

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

    # RESHAPE IT TO [[VOLTAGE, CURRENT],[VOLTAGE, CURRENT]...] (2 COLUMNS, x ROWS)
    if datatype == PG_TYPE_PULSEDATA:
        pgData = pgData.reshape(-1, 2)

    # DELETE ZEROS, IF DATASTRUCTURE IS PLANNED TO BE EMPTY
    elif datatype in (PG_TYPE_DATASTART, PG_TYPE_ZERODATA):
        pgData[pgData != 0]

    return pgData, datatype, crcStatus

# READS A WHOLE PULSE OF DATA, RIGHT AFTER "START"-DATA IS RECEIVED
def read_next_PG_pulse(ser, timeout=0, verbose=0):
    '''
    Reads serial data from PG (from specified serial port) and restructures the message according to the datasheet.
    NOTE: This function waits for the received type to be "pulse-data-start" (see datasheet)

        Parameters:
                ser:      			Reference to serial connection to the device (pyserial) 
                
                timeout:            NOTE: NOT USED YET

                verbose (int):      0.. printing OFF, 1.. basic printing, 2.. print ALL
                                    DEFAULT: 0
                
        Returns:
                pulseData (numpy array):    2D Numpy Array of the Data [n,2] --> [voltage, current] (structure: see datasheet)

                pulseDataLength (int):      length of the data for a single pulse
    '''
    # READ DATA AND WAIT UNTIL "PULSE DATA START"-SIGNAL IS RECEIVED
    dtype = 0

    ser.flushInput()

    while dtype != PG_TYPE_DATASTART:
        PG_data, dtype, _= read_PG_data(ser)

    if verbose: print("PULSE START RECEIVED")

    # SAVE RECEIVED PULSE DATA LENGTH
    pulseDataLength = PG_data[0]

    # CREATE EMPTY ARRAY
    pulseData = np.empty(shape=[0,2])

    # READ ALL PULSE-DATA-ARRAYS UNTIL "DATA END" IS RECEIVED
    start_time = time.time()
    while dtype != PG_TYPE_DATAEND:
        PG_data, dtype, _= read_PG_data(ser)

        # ADD NEW DATA TO THE ARRAY
        if dtype == PG_TYPE_PULSEDATA:
            pulseData = np.concatenate((pulseData, PG_data), axis=0)

    if verbose: print("PULSE END RECEIVED")

    return pulseData, pulseDataLength


#endregion

# =============================================================================================
# .___________. _______ .___  ___. .______             _______. _______ .__   __.      _______.
# |           ||   ____||   \/   | |   _  \           /       ||   ____||  \ |  |     /       |
# `---|  |----`|  |__   |  \  /  | |  |_)  |  ______ |   (----`|  |__   |   \|  |    |   (----`
#     |  |     |   __|  |  |\/|  | |   ___/  |______| \   \    |   __|  |  . `  |     \   \    
#     |  |     |  |____ |  |  |  | |  |           .----)   |   |  |____ |  |\   | .----)   |   
#     |__|     |_______||__|  |__| | _|           |_______/    |_______||__| \__| |_______/    
#
# =============================================================================================


#==================================================================
#=============FETCH TEMPERATURE DATA===============================
#==================================================================

def read_temperature(ser):
    if ser is None:
        return -1

    try:
        raw_temperature = ser.read_register(0x0E, functioncode=4, signed=True)
        temperature = raw_temperature / 10.0
        return temperature
    except IOError as e:
        print("Failed to read from temperature sensor, retrying...")
        print(f"IOError: {str(e)}")
        return None





#=============================================================================================
#____   .______      ___       ______ 
#|___ \  |   _  \    /   \     /      |
#  __) | |  |_)  |  /  ^  \   |  ,----'
# |__ <  |   ___/  /  /_\  \  |  |     
# ___) | |  |     /  _____  \ |  `----.
#|____/  | _|    /__/     \__\ \______|
#                                     
#==============================================================================================


#==================================================================
#=============FETCH FLOWRATE DATA==================================
#================================================================== 

# SEND SIGNAL TO 3PAC TO SEND FLOWRATE BACK TO BACKEND
def fetchFlowrate(ser):
    msg = f'rP\n'
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending


#==================================================================
#=============FETCH PRESSURE DATA==================================
#================================================================== 

# SEND SIGNAL TO 3PAC TO SEND PRESSURE DATA TO MIDDLEWARE
def fetch_pressure(ser):
    msg = f'rRS\n'
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending

#==================================================================
#=============STOP FETCHING PRESSURE DATA==========================
#================================================================== 

# SEND SIGNAL TO 3PAC TO STOP SENDING PRESSURE DATA TO MIDDLEWARE
def stop_fetching_pressure(ser):
    msg = f'rRO\n'
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending

#==================================================================
#=============PROCESS DATA SENT FROM THE 3PAC======================
#================================================================== 
def read_flowrate(ser):
    line = ''
    if ser.in_waiting: # Check if there is data waiting in the buffer

        while ser.in_waiting:
            line = ser.readline().decode('utf-8')
            if '\n' in line:
                received_line = line.strip()

        if received_line.startswith('rPF-'): # Check if the line starts with 'rPF-'
            try:
                # Extract the part of the line after 'rPF-', convert to float, and return
                flow_rate = float(line[4:])
                return flow_rate
            except ValueError:
                print("Error: Couldn't convert string to float.")
        elif received_line.startswith('rRP-'): # Check if the line starts with 'rRP-'
            try:
                # Extract the part of the line after 'rRP-', convert to float, and return
                pressure = float(line[4:])
                return pressure
            except ValueError:
                print("Error: Couldn't convert string to float.")
    else:
        return None
    
#==================================================================
#=============3PAC COMMANDS========================================
#================================================================== 

# HANDSHAKE FUNCTION
def handshake_3PAC(ser, sleep_time=1, print_handshake_message=False, handshake_code="HANDSHAKE\n"):
    """Make sure connection is established by sending and receiving stuff."""
    
    # Close and reopen, just to make sure. Had some troubles without it after uploading new firmware and without manual restart of the 3PAC board.
    print("closing")
    ser.close()
    time.sleep(2)
    print("opening")
    ser.open()

    # Chill out while everything gets set (SETUP LIGHT SEQUENCE)
    time.sleep(5)

    # Set a long timeout to complete handshake (and save original timeout in variable for later)
    timeout = ser.timeout
    ser.timeout = 2

    # Read and discard everything that may be in the input buffer
    _ = ser.read_all()

    # Send request to Arduino & read in what Arduino sent
    ser.write(handshake_code.encode())
    handshake_message = ser.readline()
    # Print the handshake message, if desired
    if print_handshake_message:
        print("Handshake message: " + handshake_message.decode())

    # Send and receive request again
    ser.write(handshake_code.encode())
    handshake_message = ser.readline()
    # Print the handshake message, if desired
    if print_handshake_message:
        print("Handshake message: " + handshake_message.decode())

    # Reset the timeout
    ser.timeout = timeout

      


def turnOnPumpPID(ser):
    # Construct the message
    msg = f'wPS-22\n'
    # Write the message
    ser.write(msg.encode())

def writePumpFlowRate(ser, val1=2.50, val2=0.00):
    ser.flush()
    # Construct the message
    msg = f'wPF-{val1:.2f}-{val2:.2f}\n'
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending


def writePressureCommandStart(ser):
    ser.flush()
    # Construct the message
    msg = f'wRS\n'
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending

def writePressureCommandStop(ser):
    ser.flush()
    # Construct the message
    msg = f'wRO\n'
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending
    
 
def writeSucrosePumpFlowRate(ser, val1=2.50):
    # Construct the message
    msg = f'wFS-{val1:.2f}\n'
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending
    

def writeEthanolPumpFlowRate(ser, val1=2.50):
    # Construct the message
    msg = f'wFE-{val1:.2f}\n'
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending
    
   

def writeMotorPosition(ser, motor_nr, position):
    # Construct the message
    msg = f'wMP-{motor_nr}-{position:06.2f}\n'
    print(msg)
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending

def writeMotorDistance(ser, motor_nr, distance_in_mm, direction): # "direction": 1 = positive; 2 = negative; 0 = stop
    # Construct the message
    
    msg = f'wMD-{motor_nr}-{distance_in_mm:06.2f}-{direction}\n'
    print(msg)
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending

def writeMotorJog(ser, motor_nr, direction, fast):  # "direction": 1 = positive; 2 = negative; 0 = stop jogging
    # Construct the message
    if fast:
        speed = 1
    else:
        speed = 0
    msg = f'wMJ-{motor_nr}-{direction}-{speed}\n'   
    print(msg)
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sendingw

def writeMotorHoming(ser, motor_nr):
    # motor_nr = 0 --> ALL STEPPERS
    # Construct the message
    msg = f'wMH-{motor_nr}\n'
    print(msg)
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending

def writeFlaskPosition(ser, flask_nr):
    # flask_nr = 0 --> PARKING POSITION
    msg = f'wMF-{flask_nr}\n'
    print(msg)
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending

def writeBloodSyringe(ser, volume, speed):
    # if volume == 0.00 --> STOP MOVEMENT
    msg = f'wMB-{volume:04.2f}-{speed:04.2f}\n'
    print(msg)
    #Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending

# SETS THE LED STATUS OF THE USER-SECTION-LIGHTS
# 0 --> OFF
# 1 --> ON
# 2 --> BLINK
# THERE IS ROOM FOR MORE FUNCTIONALITY IF NEEDED
def writeLedStatus(ser, led1=0, led2=0, led3=0):
    msg = f'wLS-{led1}{led2}{led3}\n'
    print(msg)
    # Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending


# SETS THE LED STATUS OF THE USER-SECTION-LIGHTS
# 0 --> OFF
# 1 --> ON
# THERE IS ROOM FOR MORE FUNCTIONALITY IF NEEDED
def writeLogoStatus(ser, Logo=0):
    msg = f'wLO-{Logo}\n'
    print(msg)
    # Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending    

