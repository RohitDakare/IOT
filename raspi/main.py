import time
import serial
import RPi.GPIO as GPIO
import threading
from sensors import LiDAR, Ultrasonic, GPS
from communication import GSM, BluetoothSoft
from camera_trigger import ESP32Trigger
from motors import MotorController

# Configuration
POTHOLE_THRESHOLD = 5.0
SEVERITY_LEVELS = {"Minor": (1, 3), "Moderate": (3, 7), "Critical": (7, 100)}

# Pin Definitions aligned with User Request
# -----------------------------------------
# LiDAR: UART0 (GPIO 14/15)
# GPS: UART5 (GPIO 12/13) -> /dev/ttyAMA5
# GSM: UART2 (GPIO 0/1) -> /dev/ttyAMA1
# Motors: IN 5,6,17,26. ENA/ENB moved to 20/21 (Code override) due to conflict with GPS.
# ESP32 Trigger: GPIO 11
# Ultrasonic: TRIG=23, ECHO=24 (Assumed, as not specified in wiring text but standard)

def calculate_severity(depth):
    for level, (low, high) in SEVERITY_LEVELS.items():
        if low <= depth < high: return level
    return "Unknown"

class PotholeSystem:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        
        # Initialize Sensors
        # self.lidar = LiDAR() # UART0 default
        self.ultrasonic = Ultrasonic(23, 24)
        self.gps = GPS() # Auto-detects on UART5
        self.gsm = GSM("/dev/ttyAMA1") # UART2
        self.camera = ESP32Trigger(11) # GPIO 11
        
        # Motors
        # WARNING: User asked for ENA/ENB on 12/13. This conflicts with GPS.
        # Code uses 20/21. PLEASE REWIRE ENA->20, ENB->21.
        self.motors = MotorController() 
        
        self.bluetooth = None
        # Try finding hardware BT first (e.g., if rewired to UART3 GPIO 4/5)
        potential_bt_ports = ["/dev/ttyAMA2", "/dev/ttyAMA3", "/dev/rfcomm0"]
        for port in potential_bt_ports:
            try:
                self.bluetooth = serial.Serial(port, 9600, timeout=1)
                print(f"Bluetooth connected on {port}")
                break
            except:
                continue
        
        if not self.bluetooth:
             # Fallback to the SoftUART class for 27/22 if needed (Non-functional placeholder)
             # print("Bluetooth hardware UART not found. Checking GPIO 27/22...")
             pass

        self.running = True

    def bluetooth_control(self):
        if not self.bluetooth: return
        print("Bluetooth control started.")
        while self.running:
            try:
                if self.bluetooth.in_waiting > 0:
                    cmd = self.bluetooth.read().decode().lower()
                    if cmd == 'f': self.motors.forward()
                    elif cmd == 'b': self.motors.backward()
                    elif cmd == 'l': self.motors.left()
                    elif cmd == 'r': self.motors.right()
                    elif cmd == 's': self.motors.stop()
                time.sleep(0.05)
            except:
                break

    def detection_loop(self):
        print("Detection loop started.")
        while self.running:
            depth_val = self.ultrasonic.get_distance()
            
            if depth_val > POTHOLE_THRESHOLD:
                print(f"Pothole Detected! Depth: {depth_val:.2f}cm")
                self.camera.trigger()
                coords = self.gps.get_location()
                severity = calculate_severity(depth_val)
                
                data = {
                    "latitude": coords['lat'],
                    "longitude": coords['lon'],
                    "depth": float(f"{depth_val:.2f}"),
                    "severity": severity,
                    "timestamp": time.time()
                }
                
                if coords['fixed']:
                     print(f"Location: {coords['lat']}, {coords['lon']}")
                
                self.gsm.send_data(data)
                time.sleep(2)
            
            time.sleep(0.1)

    def run(self):
        bt_thread = threading.Thread(target=self.bluetooth_control)
        bt_thread.daemon = True
        bt_thread.start()
        
        try:
            self.detection_loop()
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.running = False
            self.motors.stop()
            self.gps.stop()
            self.gsm.close()
            GPIO.cleanup()

if __name__ == "__main__":
    system = PotholeSystem()
    system.run()
