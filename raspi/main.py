import time
import serial
import RPi.GPIO as GPIO
import threading
from sensors import LiDAR, Ultrasonic, GPS
from communication import GSM, SoftwareSerial
from camera_trigger import ESP32Trigger
from motors import MotorController

# Configuration
POTHOLE_THRESHOLD = 5.0 # cm
SEVERITY_LEVELS = {"Minor": (1, 3), "Moderate": (3, 7), "Critical": (7, 100)}
ESTIMATED_SPEED_CM_S = 30.0 # avg speed of toy car

class PotholeSystem:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        
        # Initialize Sensors (User PINOUT)
        # ultrasonic: Trig=17 (Pin 11), Echo=18 (Pin 12)
        self.ultrasonic = Ultrasonic(17, 18)
        
        # GPS: Defaults to UART0 (GPIO 14/15) which matches User Request
        self.gps = GPS() 
        
        # GSM: User defined PINS 20(RX) and 16(TX). 
        # CAUTION: Software Serial at 9600.
        self.gsm = GSM(tx=16, rx=20)
        
        # Camera: User defined PINS 24(RX) and 23(TX).
        self.camera = ESP32Trigger(tx=23, rx=24)
        
        # LiDAR: User defined PINS 12(RX) and 6(TX).
        self.lidar = LiDAR(tx=6, rx=12) # Added LiDAR Instance (Missed in original file?)
        # Wait, original file imported LiDAR but didn't instantiate it in __init__ except maybe checking pins? 
        # Ah, original file didn't instantiate LiDAR! It was in imports but unused. 
        # Or maybe I missed it. Let's check original.
        # Original: self.ultrasonic = ... self.gps... self.gsm... self.camera... self.motors...
        # NO LIDAR in original __init__? 
        # Detection loop uses self.ultrasonic. 
        # The user's system relies on Ultrasonic for detection? 
        # User REQ: "TF02-Pro LiDAR... on custom PCB".
        # I should add LiDAR to the system if it's meant to be used. 
        # But detection_loop uses self.ultrasonic. 
        # I will instantiate it but leave detection logic to ultrasonic for now unless asked to change logic.
        
        self.motors = MotorController() 
        
        self.bluetooth = None
        self.running = True
        
        # BT Init: User defined PINS 21(RX) and 19(TX).
        print("Bluetooth: Initializing Software Serial on 19(TX), 21(RX)...")
        try:
            self.bluetooth = SoftwareSerial(tx=19, rx=21, baud=9600)
            print("Bluetooth SoftSerial Started.")
        except Exception as e:
            print(f"Bluetooth Init Failed: {e}") 
        
        # Fallback to Hardware Search if SoftSerial fails?
        if not self.bluetooth:
            for port in ["/dev/ttyAMA2", "/dev/ttyAMA3", "/dev/rfcomm0"]:
                try:
                    self.bluetooth = serial.Serial(port, 9600, timeout=1)
                    print(f"Bluetooth connected on {port}")
                    break
                except:
                    continue

    def bluetooth_control(self):
        if not self.bluetooth: return
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
        print("Detection loop started...")
        in_pothole = False
        start_time = 0
        max_depth = 0
        
        while self.running:
            current_depth = self.ultrasonic.get_distance()
            
            # Filter noise
            if current_depth > 200 or current_depth < 0: 
                time.sleep(0.05)
                continue

            if not in_pothole:
                if current_depth > POTHOLE_THRESHOLD:
                    # --- START OF POTHOLE ---
                    in_pothole = True
                    start_time = time.time()
                    max_depth = current_depth
                    print(f"Pothole Start! Initial Depth: {current_depth:.1f}cm")
                    
                    # 1. Trigger Camera Immediately to capture the hole
                    self.camera.trigger()
                    
            else:
                # We are IN a pothole
                if current_depth > max_depth:
                    max_depth = current_depth
                
                # Check if we are out of the pothole (depth returns to normal)
                if current_depth < POTHOLE_THRESHOLD:
                    # --- END OF POTHOLE ---
                    in_pothole = False
                    duration = time.time() - start_time
                    
                    # Calculate Dimensions
                    length = duration * ESTIMATED_SPEED_CM_S
                    width = 0.0 # Requires image processing, placeholder
                    
                    print(f"Pothole End. Max Depth: {max_depth:.1f}cm, Length: {length:.1f}cm")
                    
                    # Get Location
                    coords = self.gps.get_location()
                    severity = self.calculate_severity(max_depth)
                    
                    # Prepare Payload including Dimensions
                    data = {
                        "latitude": coords['lat'],
                        "longitude": coords['lon'],
                        "depth": float(f"{max_depth:.2f}"),
                        "length": float(f"{length:.2f}"),
                        "width": 0.0, # Placeholder
                        "severity": severity,
                        "timestamp": time.time()
                    }
                    
                    if coords['fixed']:
                        print(f"  > Location: {coords['lat']:.5f}, {coords['lon']:.5f}")
                    else:
                        print("  > Warning: No GPS Fix (Outdoor view needed)")
                        
                    self.gsm.send_data(data)
                    time.sleep(1) # Debounce next hole

            time.sleep(0.05) # Sampling rate (20Hz)

    def calculate_severity(self, depth):
        for level, (low, high) in SEVERITY_LEVELS.items():
            if low <= depth < high: return level
        return "Critical"

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
    sys = PotholeSystem()
    sys.run()
