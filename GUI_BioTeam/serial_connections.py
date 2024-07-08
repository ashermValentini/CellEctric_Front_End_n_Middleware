import serial
import serial.tools.list_ports
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
            try:
                self.serial_device = serial.Serial(port, baud_rate, timeout=timeout)
                return self.serial_device
            except serial.SerialException as e:
                print(f"Could not open port {port}: {e}")
                return None
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
# CHILD SERIAL DEVICE CLASS for DEVICES THAT NEED TO BE FOUND BY FTDI SERIAL NUMBERS
class SerialDeviceBySerialNumber(SerialConnections):
    def __init__(self, serial_numbers):
        super().__init__(vendor_id=None, product_id=None)
        self.serial_numbers = serial_numbers
   
    def find_serial_port(self):
        """
        Find a serial port by checking each connected device's serial number against a list of known serial numbers.
        """
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.serial_number in self.serial_numbers:
                print(f"Found device at {port.device} with serial number {port.serial_number}")
                return port.device, port.serial_number  # Return both device and serial number
        print("Device with specified serial numbers not found.")
        return None, None
    
    def establish_connection(self, baud_rate=9600, timeout=1):
        """
        Establishes a serial connection using the serial number to find the port.
        """
        port, found_serial_number = self.find_serial_port()  # Get both port and serial number
        if port:
            self.serial_device = serial.Serial(port, baud_rate, timeout=timeout)
            print(f"Connection established to device with serial number {found_serial_number} at port {port}")
            return self.serial_device
        else:
            print("Failed to establish connection.")
            return None