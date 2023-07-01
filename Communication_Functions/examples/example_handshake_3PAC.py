import serial
import serial.tools.list_ports
import time

HANDSHAKE = "HANDSHAKE"
VALVE_ON = "wVS-010"
VALVE_OFF = "wVS-000"
PELTIER_ON = "wCS-1"
PELTIER_OFF = "wCS-0"

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


# HANDSHAKE FUNCTION
def handshake_3PAC(ser, sleep_time=1, print_handshake_message=False, handshake_code="HANDSHAKE"):
    """Make sure connection is established by sending and receiving stuff."""
    
    # Close and reopen, just to make sure. Had some troubles without it after uploading new firmware and without manual restart of the 3PAC board.
    print("closing")
    ser.close()
    time.sleep(2)
    print("opening")
    ser.open()

    # Chill out while everything gets set
    time.sleep(15)

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


# =================
# EXAMPLE CODE
# =================

# LIST ALL PORTS
ports = serial.tools.list_ports.comports()
print(ports)

# FIND THE PORT OF THE ESP32 (3PAC)
port = find_esp()
print(port)

# OPEN PORT
ser_3PAC = serial.Serial(port, baudrate=115200, timeout=1)

# HANDSHAKE
handshake_3PAC(ser_3PAC, print_handshake_message=True)



# TEST SOME STUFF
print("MESSAGE: " + VALVE_ON)
ser_3PAC.write(VALVE_ON.encode())
msg = ser_3PAC.readline()
print("RESPONSE: " + msg.decode())
time.sleep(0.25)

print("MESSAGE: " + PELTIER_ON)
ser_3PAC.write(PELTIER_ON.encode())
msg = ser_3PAC.readline()
print("RESPONSE: " + msg.decode())
time.sleep(0.25)

print("MESSAGE: " + VALVE_OFF)
ser_3PAC.write(VALVE_OFF.encode())
msg = ser_3PAC.readline()
print("RESPONSE: " + msg.decode())
time.sleep(0.25)

print("MESSAGE: " + PELTIER_OFF)
ser_3PAC.write(PELTIER_OFF.encode())
msg = ser_3PAC.readline()
print("RESPONSE: " + msg.decode())
time.sleep(0.25)




# CLOSE CONNECTION
ser_3PAC.flush()
ser_3PAC.close()