import serial
import RPi.GPIO as GPIO
import time
import threading
import adafruit_gps 
from communication import SoftwareSerial

GPIO.setwarnings(False)

class LiDAR:
    def __init__(self, port="/dev/ttyS0", baud=115200, tx=None, rx=None):
        self.ser = None
        self.dist = 0
        
        if port and not (tx and rx):
            # Hardware UART
            try:
                self.ser = serial.Serial(port, baud, timeout=1)
            except Exception as e:
                print(f"LiDAR init failed on {port}: {e}")
        elif tx is not None and rx is not None:
            # Software UART
            print(f"LiDAR: Using Software Serial on TX={tx}, RX={rx} (Warning: 115200 baud on SW Serial is unstable)")
            try:
                self.ser = SoftwareSerial(tx, rx, baud)
            except Exception as e:
                print(f"LiDAR SW Init failed: {e}")
        
    def get_distance(self):
        if not self.ser: return 0
        try:
            if isinstance(self.ser, serial.Serial):
                if self.ser.in_waiting >= 9:
                    if self.ser.read(1) == b'\x59':
                        if self.ser.read(1) == b'\x59':
                            d_low = ord(self.ser.read(1))
                            d_high = ord(self.ser.read(1))
                            self.dist = d_low + d_high * 256
                            return self.dist / 100.0
            else:
                # Software Serial Strategy
                # We need to read 9 bytes. This is blocking and unreliable if not synced.
                # Just try to read 9 bytes?
                # Ideally, we should sync to 0x59 0x59.
                # A simple parser for SW Serial:
                byte = self.ser.read(1)
                if byte == b'\x59':
                    byte2 = self.ser.read(1)
                    if byte2 == b'\x59':
                        data = self.ser.read(7) # Read remaining 7 bytes
                        if len(data) == 7:
                            d_low = data[0]
                            d_high = data[1]
                            self.dist = d_low + d_high * 256
                            return self.dist / 100.0
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
    def __init__(self, port=None):
        self.uart = None
        self.gps = None
        self.running = True
        self.latest_data = {'lat': 0.0, 'lon': 0.0, 'alt': 0.0, 'fixed': False}
        
        # Priority: User Argument -> Standard UART0 -> Mini UART -> USB -> UART5
        potential_ports = []
        if port: potential_ports.append(port)
        potential_ports.extend(["/dev/ttyS0", "/dev/serial0", "/dev/ttyAMA0", "/dev/ttyUSB0", "/dev/ttyAMA5"])
        
        for p in potential_ports:
            try:
                self.uart = serial.Serial(p, baudrate=9600, timeout=1)
                self.gps = adafruit_gps.GPS(self.uart, debug=False)
                # PMTK config commands
                self.gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
                self.gps.send_command(b"PMTK220,1000")
                print(f"GPS initialized on {p}...")
                
                self.thread = threading.Thread(target=self._update_loop)
                self.thread.daemon = True
                self.thread.start()
                break
            except Exception as e:
                pass
        
        if not self.gps:
            print("Warning: GPS could not be initialized.")

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
