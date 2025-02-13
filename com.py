"""Small example Emotiv OSC with Arduino control

This program listens to several addresses, controls an Arduino based on OSC input.
"""

import argparse
import math
from pythonosc import dispatcher
from pythonosc import osc_server
import serial
import time

# Initialize serial connection to Arduino
arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.4)
time.sleep(2)  # Wait for Arduino connection to establish

PORT_NUMBER = 8500
IP_DEFAULT = "192.168.100.149"

def filter_handler(address,*args):
    print(f"{address}: {args}")

def blink_light(address, *args):
    """Controls Arduino based on intensity value"""
    intensity = args[0]
    
    # Send command to Arduino based on intensity threshold
    if intensity > 0.2:
        print("THINKING VERY LEFT - ACTIVATING ARDUINO")
        arduino.write(b'H')  # Send 'H' to Arduino (turn on)
    else:
        print("NOT LEFT - DEACTIVATING ARDUINO")
        arduino.write(b'L')  # Send 'L' to Arduino (turn off)
    
    print(f"{address}: {args[0]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default=IP_DEFAULT, help="The ip to listen on")
    parser.add_argument("--port", type=int, default=PORT_NUMBER, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    
    # Mapped handlers
    dispatcher.map("/fac/uAct/neutral", blink_light)
    dispatcher.map("/com/neutral", blink_light)
    dispatcher.map("/com/left", filter_handler)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        arduino.close()  # Clean up serial connection
        print("\nServer stopped and Arduino connection closed")