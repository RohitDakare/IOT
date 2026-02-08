import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'raspi')))

try:
    from communication import SoftwareSerial
    import RPi.GPIO as GPIO
except ImportError:
    print("Error: Could not import 'communication' or 'RPi.GPIO'.")
    SoftwareSerial = None

def test_bluetooth():
    print("--- HC-05 (SC-05) Bluetooth Configuration & Test (Software Serial) ---")
    if SoftwareSerial is None: return

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # User Pins: TX=19, RX=21
    TX_PIN = 19
    RX_PIN = 21
    BAUD = 9600
    
    print(f"Using Software Serial on Pi TX={TX_PIN}, RX={RX_PIN} @ {BAUD} baud")
    print("Action: Send any character from your Bluetooth Terminal App (e.g. 'f', 'b', 'l', 'r')")
    
    try:
        ser = SoftwareSerial(tx=TX_PIN, rx=RX_PIN, baud=BAUD)
        
        # Wait 10 seconds for user input
        timeout = time.time() + 10
        found = False
        
        print("Listening for 10 seconds...")
        while time.time() < timeout:
            if ser.in_waiting:
                data = ser.read(1) # Read 1 byte
                val = data.decode(errors='ignore')
                print(f"SUCCESS: Received Data: '{val}'")
                found = True
                
                # Echo back?
                ser.write(f" Echo: {val}")
                break
                
            time.sleep(0.05)
            
        if not found:
            print("\nRESULT: Bluetooth connection failed or no data received.")
            print("Required Fixes:")
            print("1. Pair your phone with HC-05.")
            print("2. Connect via App (Serial Bluetooth Terminal).")
            print("3. Send a character.")
            print(f"4. Verify wiring: Pi Pin 35 (GPIO 19) -> HC-05 RX, Pi Pin 40 (GPIO 21) -> HC-05 TX.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_bluetooth()
