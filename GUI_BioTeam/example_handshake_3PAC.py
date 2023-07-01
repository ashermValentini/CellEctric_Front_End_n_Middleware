import serial
import serial.tools.list_ports
import time

HANDSHAKE = "HANDSHAKE"


# =================
# FUNCTIONS
# =================

# FIND PORT OF ESP32
def find_esp(port=None):
    """Get the name of the port that is connected to the ESP32."""
    if port is None:
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if p.manufacturer is not None and "Silicon" in p.manufacturer:  # "Silicon" is in the name of the ESP32 manufacturer
                port = p.device
    return port











