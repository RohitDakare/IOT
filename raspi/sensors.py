import serial
import RPi.GPIO as GPIO
import time
import adafruit_gps # Requires pip install adafruit-circuitpython-gps

GPIO.setwarnings(False)

class LiDAR:
    def __init__(self, port, baud=115200):
        self.ser = serial.Serial(port, baud, timeout=1)
        
    def get_distance(self):
        # TF02 Pro Data Format: 0x59 0x59 Dist_L Dist_H ...
        if self.ser.in_waiting >= 9:
            if self.ser.read(1) == b'\x59':
                if self.ser.read(1) == b'\x59':
                    d_low = ord(self.ser.read(1))
                    d_high = ord(self.ser.read(1))
                    distance = d_low + d_high * 256
                    return distance / 100.0  # Convert to cm
        return 0

class Ultrasonic:
    def __init__(self, trig, echo):
        self.trig = trig
        self.echo = echo
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def get_distance(self):
        GPIO.output(self.trig, True)
        time.sleep(0.00001)
        GPIO.output(self.trig, False)

        start_time = time.time()
        stop_time = time.time()

        while GPIO.input(self.echo) == 0:
            start_time = time.time()

        while GPIO.input(self.echo) == 1:
            stop_time = time.time()

        time_elapsed = stop_time - start_time
        distance = (time_elapsed * 34300) / 2
        return distance

class GPS:
    def __init__(self, tx, rx):
        self.uart = None
        self.gps = None
        # Neo-6M is usually 9600 baud. Priority: UART5 (Pi 4 pins 12/13), then serial0
        potential_ports = ["/dev/ttyAMA5", "/dev/serial0", "/dev/ttyAMA1", "/dev/ttyS0"]
        
        for port in potential_ports:
            try:
                self.uart = serial.Serial(port, baudrate=9600, timeout=1)
                self.gps = adafruit_gps.GPS(self.uart, debug=False)
                print(f"GPS attempting initialized on {port}...")
                # Simple check: try to read a few bytes
                time.sleep(0.5)
                if self.uart.in_waiting > 0:
                    print(f"GPS data detected on {port}")
                    break
            except:
                continue
        
        if not self.gps:
            print("Warning: GPS could not be initialized.")

    def get_location(self):
        """Fetches and analyzes GPS location. Returns (lat, lon, altitude)"""
        if not self.gps:
            return {'lat': 0.0, 'lon': 0.0, 'alt': 0.0, 'fixed': False}
            
        # Give it a few tries to update and get a fix
        for _ in range(5):
            self.gps.update()
            if self.gps.has_fix:
                return {
                    'lat': self.gps.latitude,
                    'lon': self.gps.longitude,
                    'alt': self.gps.altitude_m if self.gps.altitude_m else 0.0,
                    'fixed': True
                }
            time.sleep(0.1)
            
        print("GPS: Waiting for Fix (Outdoor sight needed)...")
        return {'lat': 0.0, 'lon': 0.0, 'alt': 0.0, 'fixed': False}
