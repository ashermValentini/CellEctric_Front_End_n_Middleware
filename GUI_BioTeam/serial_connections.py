import serial
from serial.tools import list_ports
import minimalmodbus


# SUPER SERIAL DEVICE CLASS
class SerialConnections:
    def __init__(self, vendor_id, product_id):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.serial_device = None

    def find_serial_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.vid == self.vendor_id and port.pid == self.product_id:
                return port.device
        return None

    def establish_connection(self, baud_rate=9600, timeout=1):
        port = self.find_serial_port()
        if port:
            self.serial_device = serial.Serial(port, baud_rate, timeout=timeout)
            return self.serial_device
        else:
            print(f"Device with VID: {self.vendor_id} and PID: {self.product_id} not found")
            return None

    def close_connection(self):
        if self.serial_device and self.serial_device.is_open:
            self.serial_device.close()

# CHILD SERIAL DEVICE CLASS FOR TEMPERATURE SENSOR
class TemperatureSensorSerial(SerialConnections):
    def establish_connection(self):
        port = self.find_serial_port()
        if port is not None:
            self.serial_device = minimalmodbus.Instrument(port, 1)  # Assuming slave address is 1
            self.serial_device.serial.baudrate = 9600
            self.serial_device.serial.bytesize = 8
            self.serial_device.serial.parity = serial.PARITY_NONE
            self.serial_device.serial.stopbits = 1
            self.serial_device.serial.timeout = 0.1
            self.serial_device.mode = minimalmodbus.MODE_RTU
            return self.serial_device
        else:
            print(f"Temperature sensor with VID: {self.vendor_id} and PID: {self.product_id} not found")
            return None

# CHILD SERIAL DEVICE CLASS for ESP32 RTOS dubbed 3PAC
class ESP32Serial(SerialConnections):
    def __init__(self):
        super().__init__(vendor_id=None, product_id=None)

    def find_serial_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            print(f"Found port: {port.device}, Manufacturer: {port.manufacturer}")
            if port.manufacturer is not None and "Silicon" in port.manufacturer:
                return port.device
        return None


    def establish_connection(self, baud_rate=115200, timeout=1):
        port = self.find_serial_port()
        if port:
            self.serial_device = serial.Serial(port, baud_rate, timeout=timeout)
            return self.serial_device
        else:
            print("ESP32 device not found")
            return None