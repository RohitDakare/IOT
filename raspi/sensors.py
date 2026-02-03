import serial
import RPi.GPIO as GPIO
import time
import adafruit_gps # Requires pip install adafruit-circuitpython-gps

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
        # Neo-6M is usually 9600 baud
        # Using Serial because GPIO 12/13 are UART capable on Pi 4
        self.uart = serial.Serial("/dev/ttyAMA1", baudrate=9600, timeout=10)
        self.gps = adafruit_gps.GPS(self.uart, debug=False)

    def get_location(self):
        self.gps.update()
        if not self.gps.has_fix:
            return {'lat': 0.0, 'lon': 0.0}
        return {
            'lat': self.gps.latitude,
            'lon': self.gps.longitude
        }
