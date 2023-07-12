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



# CRAFT PACKAGE TO TURN ON PID MODE 
def turnOnPumpPID(ser):
    # Construct the message
    msg = f'wPS-22'
    
    # Write the message
    ser.write(msg.encode())
 
def writePumpFlowRate(ser, val1=2.50, val2=0.00):
    # Construct the message
    msg = f'wPF-{val1:.2f}-{val2:.2f}'
    print(msg)  # Print the message

    # Write the message
    ser.write(msg.encode())  # encode the string to bytes before sending



def read_flowrate(ser):
    if ser.in_waiting > 0:  # Check if there is data waiting in the serial buffer
        line = ser.readline().decode('utf-8').strip()  # Read line from serial port, decode, and strip whitespace
        if line.startswith('rPF-'):  # Check if the line starts with 'rAC-'
            try:
                # Extract the part of the line after 'rAC-', convert to float, and return
                flow_rate = float(line[4:])
                return flow_rate
            except ValueError:
                print("Error: Couldn't convert string to float.")
    return None



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


p1fr=2.50
p2fr=0.00

print("MESSAGE: PID On")
turnOnPumpPID(ser_3PAC)
msg = ser_3PAC.readline()
print("RESPONSE: " + msg.decode())
time.sleep(5)

print("MESSAGE: Send Flow Rates")
writePumpFlowRate(ser_3PAC, p1fr, p2fr)
time.sleep(5)



try:
    while True:  # This loop will run forever
        flow_rate = read_flowrate(ser_3PAC)  # Call the read_flowrate function
        if flow_rate is not None:  # If a float was returned
            print(f"Flow rate: {flow_rate}")  # Print the flow rate
        else:
            time.sleep(0.1)  # Sleep for a short time to reduce CPU usage
except KeyboardInterrupt:
    print("Interrupted by user, closing...")
finally:
    ser_3PAC.flush()
    ser_3PAC.close()
