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

class SoftwareSerial:
    """
    Software Serial implementation for pins that do not support hardware UART.
    Note: Standard RPi.GPIO is slow. For higher baud rates (>=9600), this is unreliable.
    pigpio is recommended for robust software serial, but this serves as a fallback.
    """
    def __init__(self, tx, rx, baud=9600):
        self.tx = tx
        self.rx = rx
        self.baud = baud
        self.bit_time = 1.0 / baud
        
        GPIO.setup(self.tx, GPIO.OUT)
        GPIO.output(self.tx, GPIO.HIGH) # Idle High
        GPIO.setup(self.rx, GPIO.IN)
        
    def write(self, data):
        """Blocking bit-bang write"""
        if isinstance(data, str):
            data = data.encode()
            
        for byte in data:
            # Start bit (Low)
            GPIO.output(self.tx, GPIO.LOW)
            time.sleep(self.bit_time)
            
            # Data bits (LSB first)
            val = byte
            for _ in range(8):
                bit = val & 1
                GPIO.output(self.tx, bit)
                time.sleep(self.bit_time)
                val >>= 1
                
            # Stop bit (High)
            GPIO.output(self.tx, GPIO.HIGH)
            time.sleep(self.bit_time)
            
    def read(self, count=1):
        """
        Blocking bit-bang read. 
        WARNING: This consumes 100% CPU waiting for start bit and is timing sensitive.
        """
        data = b''
        for _ in range(count):
            # Wait for start bit (Low)
            while GPIO.input(self.rx) == GPIO.HIGH:
                pass
            
            # Align to center of start bit? No, align to end of start bit.
            # Simple approach: Wait 1.5 bit times to sample first data bit
            time.sleep(self.bit_time * 1.5)
            
            val = 0
            for i in range(8):
                bit = GPIO.input(self.rx)
                val |= (bit << i)
                time.sleep(self.bit_time)
            
            # Stop bit
            time.sleep(self.bit_time) 
            data += bytes([val])
            
        return data

    @property
    def in_waiting(self):
        # We cannot easily check in_waiting without buffering in a thread/interrupt.
        # Check if RX line is Low (Start bit)?
        return 0 if GPIO.input(self.rx) == GPIO.HIGH else 1

    def close(self):
        pass

class GSM:
    def __init__(self, port=None, tx=None, rx=None, baud=9600):
        self.ser = None
        self.baud = baud
        
        if port:
            # Hardware UART
            try:
                self.ser = serial.Serial(port, baud, timeout=1)
                self.send_at("AT")
            except Exception as e:
                print(f"GSM: HW UART {port} failed: {e}")
        elif tx is not None and rx is not None:
             # Software UART
             print(f"GSM: Using Software Serial on TX={tx}, RX={rx}")
             try:
                 self.ser = SoftwareSerial(tx, rx, baud)
                 self.send_at("AT")
             except Exception as e:
                 print(f"GSM: SW UART failed: {e}")
        
        if self.ser:
            self.init_gsm()
        else:
            print("GSM: Initialization failed (No valid port or pins).")

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
            if isinstance(self.ser, serial.Serial):
                self.ser.write((cmd + "\r\n").encode())
                time.sleep(wait)
                if self.ser.in_waiting:
                    return self.ser.read(self.ser.in_waiting).decode(errors='ignore')
            else:
                # Software Serial
                self.ser.write(cmd + "\r\n")
                time.sleep(wait)
                # Read? SW Serial read is tricky/blocking. 
                # We skip reading response for now to avoid hanging, or implement timeout.
                return "" 
        except:
            return ""
        return ""

    def send_data(self, data):
        if not self.ser: return
        json_data = json.dumps(data)
        self.send_at("AT+HTTPINIT")
        self.send_at("AT+HTTPPARA=\"CID\",1")
        self.send_at("AT+HTTPPARA=\"URL\",\"http://195.35.23.26/api/potholes\"")
        self.send_at("AT+HTTPPARA=\"CONTENT\",\"application/json\"")
        
        self.send_at(f"AT+HTTPDATA={len(json_data)},10000", wait=0.5)
        try:
            if isinstance(self.ser, serial.Serial):
                self.ser.write(json_data.encode())
            else:
                self.ser.write(json_data)
                
            time.sleep(1)
            self.send_at("AT+HTTPACTION=1", wait=3)
            self.send_at("AT+HTTPTERM")
        except:
            pass

    def close(self):
        if self.ser and hasattr(self.ser, 'close'): self.ser.close()
