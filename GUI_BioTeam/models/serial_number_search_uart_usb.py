import serial.tools.list_ports

def find_serial_number():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.vid is not None and port.pid is not None:
            print(f"Device: {port.device}")
            print(f"Manufacturer: {port.manufacturer}")
            print(f"Description: {port.description}")
            print(f"HWID: {port.hwid}")
            print(f"VID:PID = {port.vid}:{port.pid}")
            print(f"Serial Number: {port.serial_number}")
            print("=========================================")

if __name__ == "__main__":
    find_serial_number()
