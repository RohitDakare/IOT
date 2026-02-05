import serial
import time

def test_bluetooth():
    print("--- HC-05 (SC-05) Bluetooth Configuration & Test ---")
    
    # HC-05 is typically configured via AT mode (Pin 34/Key HIGH) at 38400
    # or Data mode at 9600.
    ports = ["/dev/rfcomm0", "/dev/ttyAMA2", "/dev/ttyAMA3", "/dev/ttyS0"]
    baud = 9600
    
    print("Searching for paired device or serial connection...")
    
    found = False
    for port in ports:
        try:
            print(f"Trying {port}...")
            ser = serial.Serial(port, baud, timeout=1)
            print(f"Connected to {port}. Listening for data...")
            print("Action: Send any character from your Bluetooth Terminal App (e.g. 'f', 'b', 'l', 'r')")
            
            # Wait 10 seconds for user input
            timeout = time.time() + 10
            while time.time() < timeout:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting).decode(errors='ignore')
                    print(f"SUCCESS: Received Data: '{data}'")
                    found = True
                    break
                time.sleep(0.1)
            
            ser.close()
            if found: break
        except Exception:
            continue

    if not found:
        print("\nRESULT: Bluetooth connection failed or no data received.")
        print("Required Fixes:")
        print("1. Power: Ensure LED on HC-05 is blinking.")
        print("2. Pairing: Pair your phone/PC with HC-05 first.")
        print("3. Binding: If using /dev/rfcomm0, ensure you ran 'sudo rfcomm bind 0 <MAC>'")

if __name__ == "__main__":
    test_bluetooth()
