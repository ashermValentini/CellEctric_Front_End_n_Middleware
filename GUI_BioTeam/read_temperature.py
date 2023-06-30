#==================================================================
#==========READING FROM THE PYRO MINI USB TEMPERATURE SENSOR=======
#==================================================================



import minimalmodbus
import serial
from serial.tools import list_ports




SERIAL_TEMPSENS_VENDOR_ID = 0x0403  # TEMPERATURE-SENSOR VENDOR ID
SERIAL_TEMPSENS_PRODUCT_ID = 0x6015 # TEMPERATURE-SENSOR PRODUCT ID


#==================================================================
#=============FIND THE SENSORS PORT================================
#==================================================================

def find_serial_port(vendor_id, product_id):
    ser = None
    ports = list_ports.comports()

    for port in ports:
        try: 
            if port.vid == vendor_id and port.pid == product_id:
                ser = port.device
        except Exception as error:
            print("An exception occurred:", error)
    return ser

#==================================================================
#=============FETCH TEMPERATURE DATA===============================
#==================================================================

def read_temperature():
    com_port = find_serial_port(SERIAL_TEMPSENS_VENDOR_ID, SERIAL_TEMPSENS_PRODUCT_ID)
    if not com_port:
        print("Cannot find device")
        return None

    sensor = minimalmodbus.Instrument(com_port, 1) 
    sensor.serial.baudrate = 9600
    sensor.serial.bytesize = 8
    sensor.serial.parity = serial.PARITY_NONE
    sensor.serial.stopbits = 1
    sensor.serial.timeout = 0.1
    sensor.mode = minimalmodbus.MODE_RTU

    try:
        raw_temperature = sensor.read_register(0x0E, functioncode=4, signed=True)
        temperature = raw_temperature / 10.0
        return temperature
    except IOError:
        print("Failed to read from sensor, retrying...")
        return None

if __name__ == "__main__":
    while True:
        temperature = read_temperature()
        if temperature is not None:
            print(f"Temperature: {temperature}°C")
