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
        self.lidar = LiDAR(LIDAR_PORT)
        self.ultrasonic = Ultrasonic(ULTRA_TRIG, ULTRA_ECHO)
        self.gps = GPS(GPS_TX_PIN, GPS_RX_PIN)
        self.gsm = GSM(GSM_PORT)
        self.camera = ESP32Trigger(ESP_TRIGGER_PIN)
        self.motors = MotorController()
        
        try:
            self.bluetooth = serial.Serial(BT_PORT, 9600, timeout=1)
        except:
            print("Bluetooth not connected or port busy.")
            self.bluetooth = None

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
        """Main detection logic using sensor fusion"""
        print("Detection loop started.")
        while self.running:
            # 1. Continuous LiDAR scanning
            distance = self.lidar.get_distance()
            
            # If distance increases significantly, it's a potential pothole
            if distance > POTHOLE_THRESHOLD:
                print(f"Potential Pothole! LiDAR Depth: {distance}cm")
                
                # 2. Secondary validation with Ultrasonic
                depth_val = self.ultrasonic.get_distance()
                
                # Check if both agree (within 20% margin)
                if abs(distance - depth_val) < (distance * 0.2):
                    print(f"Validated! Final Depth: {depth_val}cm")
                    
                    # 3. Trigger ESP32-CAM
                    self.camera.trigger()
                    
                    # 4. Get GPS Coordinates
                    coords = self.gps.get_location()
                    
                    # 5. Calculate Severity
                    severity = calculate_severity(depth_val)
                    
                    # 6. Prepare Data
                    data = {
                        "latitude": coords['lat'],
                        "longitude": coords['lon'],
                        "depth": depth_val,
                        "severity": severity,
                        "timestamp": time.time()
                    }
                    
                    # 7. Send via GSM
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
