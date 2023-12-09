import serial
from serial.tools import list_ports

# SUPER SERIAL CLASS
class SerialConnections:
    def __init__(self, vendor_id, product_id):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.connection = None

    def find_serial_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.vid == self.vendor_id and port.pid == self.product_id:
                return port.device
        return None

    def establish_connection(self, baud_rate=9600, timeout=1):
        device = self.find_serial_port()
        if device:
            self.connection = serial.Serial(device, baud_rate, timeout=timeout)
            return True
        else:
            print(f"Device with VID: {self.vendor_id} and PID: {self.product_id} not found")
            return False

    def close_connection(self):
        if self.connection and self.connection.is_open:
            self.connection.close()




import minimalmodbus

# CHILD SERIAL CLASS FOR TEMPERATURE SENSOR

class TemperatureSensorSerial(SerialConnections):
    def establish_connection(self):
        device = self.find_serial_port()
        if device is not None:
            self.connection = minimalmodbus.Instrument(device, 1)  # Assuming slave address is 1
            self.connection.serial.baudrate = 9600
            self.connection.serial.bytesize = 8
            self.connection.serial.parity = serial.PARITY_NONE
            self.connection.serial.stopbits = 1
            self.connection.serial.timeout = 0.1
            self.connection.mode = minimalmodbus.MODE_RTU
            return True
        else:
            print(f"Temperature sensor with VID: {self.vendor_id} and PID: {self.product_id} not found")
            return False

