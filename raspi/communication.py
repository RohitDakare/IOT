import serial
import time
import json
import RPi.GPIO as GPIO

class GSM:
    def __init__(self, port="/dev/ttyAMA1", baud=9600):
        # GSM on UART2 (GPIO 0/1) -> /dev/ttyAMA1
        self.ser = None
        self.port = port
        self.baud = baud
        
        if self.connect(port, baud):
            self.init_gsm()
        else:
            print(f"GSM: Failed to connect on {port}. Check wiring (GPIO 0/1).")

    def connect(self, port, baud):
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            self.send_at("AT") 
            return True
        except Exception:
            return False

    def init_gsm(self):
        if not self.ser: return
        self.send_at("AT+CFUN=1")
        time.sleep(1)
        self.send_at("AT+SAPBR=3,1,\"Contype\",\"GPRS\"")
        self.send_at("AT+SAPBR=3,1,\"APN\",\"internet\"")
        self.send_at("AT+SAPBR=1,1")

    def send_at(self, cmd, wait=1):
        if not self.ser: return ""
        try:
            self.ser.write((cmd + "\r\n").encode())
            time.sleep(wait)
            return self.ser.read(self.ser.in_waiting).decode(errors='ignore')
        except:
            return ""

    def send_data(self, data):
        if not self.ser: return
        json_data = json.dumps(data)
        self.send_at("AT+HTTPINIT")
        self.send_at("AT+HTTPPARA=\"CID\",1")
        self.send_at("AT+HTTPPARA=\"URL\",\"http://195.35.23.26/api/potholes\"")
        self.send_at("AT+HTTPPARA=\"CONTENT\",\"application/json\"")
        
        resp = self.send_at(f"AT+HTTPDATA={len(json_data)},10000", wait=0.5)
        # Assuming prompt
        try:
            self.ser.write(json_data.encode())
            time.sleep(1)
            self.send_at("AT+HTTPACTION=1", wait=3)
            self.send_at("AT+HTTPTERM")
        except:
            pass

    def close(self):
        if self.ser: self.ser.close()

class BluetoothSoft:
    """
    Since the user requested BT on GPIO 27 (TX) and 22 (RX) which are NOT hardware UART pins,
    we must simulate a serial port or warn. 
    REAL-TIME BIT-BANGING IN PYTHON IS UNRELIABLE.
    This is a simplified receiver for 'single character' commands like 'f', 'b', 'l', 'r'.
    """
    def __init__(self, tx_pin=27, rx_pin=22, baud=9600):
        self.tx = tx_pin
        self.rx = rx_pin
        GPIO.setup(self.tx, GPIO.OUT)
        GPIO.setup(self.rx, GPIO.IN)
        self.baud_delay = 1.0 / baud
        # print("WARNING: Software Serial for Bluetooth on 27/22 is experimental/unreliable in Python.")

    def in_waiting(self):
        # Very simple check: is the start bit (LOW) present?
        # Note: This blocks or requires polling. 
        # Ideally, we should use a hardware interrupt or 'pigpio' library for this.
        # For now, we return 0 unless we want to implement a blocking read loop in the main thread.
        # This is a placeholder. Manual control via this method is likely to fail without kernel support.
        return 0 
    
    def read(self):
        return b''
