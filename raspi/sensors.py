import serial
import RPi.GPIO as GPIO
import time
import threading
import adafruit_gps 

GPIO.setwarnings(False)

class LiDAR:
    def __init__(self, port="/dev/ttyS0", baud=115200):
        # LiDAR on UART0 (GPIO 14/15)
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
        except Exception as e:
            self.ser = None
            print(f"LiDAR init failed on {port}: {e}")
        
    def get_distance(self):
        if not self.ser: return 0
        try:
            if self.ser.in_waiting >= 9:
                if self.ser.read(1) == b'\x59':
                    if self.ser.read(1) == b'\x59':
                        d_low = ord(self.ser.read(1))
                        d_high = ord(self.ser.read(1))
                        distance = d_low + d_high * 256
                        return distance / 100.0
        except Exception:
            pass
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
        timeout = time.time() + 0.1 

        while GPIO.input(self.echo) == 0:
            start_time = time.time()
            if start_time > timeout: return 0

        while GPIO.input(self.echo) == 1:
            stop_time = time.time()
            if stop_time > timeout: return 0

        time_elapsed = stop_time - start_time
        distance = (time_elapsed * 34300) / 2
        return distance

class GPS:
    def __init__(self):
        self.uart = None
        self.gps = None
        self.running = True
        self.latest_data = {'lat': 0.0, 'lon': 0.0, 'alt': 0.0, 'fixed': False}
        
        # GPS on UART5 (GPIO 12/13) -> /dev/ttyAMA5 (or sometimes AMA4/AMA1 depending on Pi model/config)
        # We try explicit ports first
        potential_ports = ["/dev/ttyAMA5", "/dev/ttyAMA4", "/dev/ttyAMA1"]
        
        for port in potential_ports:
            try:
                self.uart = serial.Serial(port, baudrate=9600, timeout=1)
                self.gps = adafruit_gps.GPS(self.uart, debug=False)
                self.gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
                self.gps.send_command(b"PMTK220,1000")
                print(f"GPS initialized on {port}...")
                
                self.thread = threading.Thread(target=self._update_loop)
                self.thread.daemon = True
                self.thread.start()
                break
            except Exception as e:
                pass
        
        if not self.gps:
            print("Warning: GPS could not be initialized on UART5/Standard Ports.")

    def _update_loop(self):
        while self.running:
            try:
                if not self.gps: break
                self.gps.update()
                if self.gps.has_fix:
                    self.latest_data = {
                        'lat': self.gps.latitude,
                        'lon': self.gps.longitude,
                        'alt': self.gps.altitude_m,
                        'fixed': True
                    }
                else:
                    self.latest_data['fixed'] = False
                time.sleep(0.1) 
            except:
                time.sleep(1)

    def get_location(self):
        return self.latest_data

    def stop(self):
        self.running = False
