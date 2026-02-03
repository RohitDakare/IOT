import time
import serial
import RPi.GPIO as GPIO
import threading
from sensors import LiDAR, Ultrasonic, GPS
from communication import GSM
from camera_trigger import ESP32Trigger
from motors import MotorController

# Configuration
POTHOLE_THRESHOLD = 5.0  # Depth in cm to trigger alert
SEVERITY_LEVELS = {
    "Minor": (1, 3),
    "Moderate": (3, 7),
    "Critical": (7, 100)
}

# Pin Definitions
LIDAR_PORT = "/dev/ttyS0"
GPS_TX_PIN = 12
GPS_RX_PIN = 13
ULTRA_TRIG = 23
ULTRA_ECHO = 24
ESP_TRIGGER_PIN = 27
GSM_PORT = "/dev/ttyAMA0"
BT_PORT = "/dev/ttyAMA1" # HC-05

def calculate_severity(depth):
    for level, (low, high) in SEVERITY_LEVELS.items():
        if low <= depth < high:
            return level
    return "Unknown"

class PotholeSystem:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        # self.lidar = LiDAR(LIDAR_PORT) # Commented out LiDAR
        self.ultrasonic = Ultrasonic(ULTRA_TRIG, ULTRA_ECHO)
        self.gps = GPS(GPS_TX_PIN, GPS_RX_PIN)
        self.gsm = GSM(GSM_PORT)
        self.camera = ESP32Trigger(ESP_TRIGGER_PIN)
        self.motors = MotorController()
        
        # Try to initialize Bluetooth handle multiple potential ports
        self.bluetooth = None
        potential_bt_ports = [BT_PORT, "/dev/ttyAMA2", "/dev/rfcomm0", "/dev/ttyS0"]
        
        for port in potential_bt_ports:
            try:
                self.bluetooth = serial.Serial(port, 9600, timeout=1)
                print(f"Bluetooth initialized on {port}")
                break
            except:
                continue

        if not self.bluetooth:
            print("Warning: Bluetooth not connected or ports busy. Manual control disabled.")

        self.running = True

    def bluetooth_control(self):
        """Handle manual RC car control via Bluetooth"""
        if not self.bluetooth:
            return
            
        print("Bluetooth control thread started.")
        while self.running:
            if self.bluetooth.in_waiting > 0:
                cmd = self.bluetooth.read().decode().lower()
                if cmd == 'f': self.motors.forward()
                elif cmd == 'b': self.motors.backward()
                elif cmd == 'l': self.motors.left()
                elif cmd == 'r': self.motors.right()
                elif cmd == 's': self.motors.stop()
            time.sleep(0.05)

    def detection_loop(self):
        """Main detection logic using Ultrasonic (LiDAR disabled)"""
        print("Detection loop started (LiDAR Disabled).")
        while self.running:
            # 1. Primary scanning now via Ultrasonic
            depth_val = self.ultrasonic.get_distance()
            
            # If distance increases significantly, it's a potential pothole
            if depth_val > POTHOLE_THRESHOLD:
                print(f"Pothole Detected! Depth: {depth_val}cm")
                
                # 2. Trigger ESP32-CAM
                self.camera.trigger()
                
                # 3. Get GPS Coordinates
                coords = self.gps.get_location()
                
                # 4. Calculate Severity
                severity = calculate_severity(depth_val)
                
                # 5. Prepare Data
                data = {
                    "latitude": coords['lat'],
                    "longitude": coords['lon'],
                    "depth": depth_val,
                    "severity": severity,
                    "timestamp": time.time()
                }
                
                # 6. Send via GSM
                self.gsm.send_data(data)
                print(f"Data sent: {data}")
                
                # Debounce
                time.sleep(2)
            
            time.sleep(0.1)

    def run(self):
        # Start threads
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
            GPIO.cleanup()

if __name__ == "__main__":
    system = PotholeSystem()
    system.run()
