import RPi.GPIO as GPIO
import time
import serial
from communication import SoftwareSerial

class ESP32Trigger:
    def __init__(self, port=None, tx=None, rx=None, baud=115200):
        self.ser = None
        self.is_serial = False
        
        # 1. Try specified hardware port (if any)
        if port:
            try:
                self.ser = serial.Serial(port, baud, timeout=1)
                self.is_serial = True
                print(f"ESP32-CAM: Connected on {port}")
            except:
                pass
        
        # 2. Try Auto-Detect USB Serial
        if not self.ser and not (tx and rx):
            ports = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0"]
            for p in ports:
                try:
                    self.ser = serial.Serial(p, baud, timeout=1)
                    self.is_serial = True
                    print(f"ESP32-CAM: Connected via USB Auto-Detect on {p}")
                    break
                except:
                    continue
        
        # 3. Use Software Serial if pins provided
        if not self.ser and tx is not None and rx is not None:
            print(f"ESP32-CAM: Using Software Serial on TX={tx}, RX={rx}")
            try:
                self.ser = SoftwareSerial(tx, rx, baud)
                self.is_serial = True # Treat as serial
            except Exception as e:
                print(f"ESP32-CAM: SW Serial Init Failed: {e}")

        # 4. Fallback? No fallback GPIO trigger unless specifically requested, but user wiring is Serial.
        if not self.ser:
            print("ESP32-CAM: Formatting error - No valid connection method found.")

    def trigger(self):
        if self.ser:
            try:
                print("Sending CAPTURE command to ESP32...")
                if isinstance(self.ser, serial.Serial):
                    self.ser.write(b'c')
                else:
                    self.ser.write(b'c') # Software Serial handle bytes or string? Updated SoftwareSerial handles bytes.
            except Exception as e:
                print(f"ESP32 Trigger Error: {e}")
        else:
            print("ESP32 Trigger Failed: No Connection")
