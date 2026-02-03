import serial
import time
import json

class GSM:
    def __init__(self, port, baud=9600):
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            self.init_gsm()
            print(f"GSM initialized on {port}")
        except Exception as e:
            self.ser = None
            print(f"Warning: GSM could not be initialized on {port}. {e}")

    def init_gsm(self):
        if not self.ser: return
        self.send_at("AT")
        self.send_at("AT+SAPBR=3,1,\"Contype\",\"GPRS\"")
        self.send_at("AT+SAPBR=3,1,\"APN\",\"internet\"") # Adjust APN
        self.send_at("AT+SAPBR=1,1")

    def send_at(self, cmd, wait=1):
        if not self.ser: return ""
        try:
            self.ser.write((cmd + "\r\n").encode())
            time.sleep(wait)
            return self.ser.read(self.ser.in_waiting).decode()
        except:
            return ""

    def send_data(self, data):
        if not self.ser: return
        json_data = json.dumps(data)
        self.send_at("AT+HTTPINIT")
        self.send_at("AT+HTTPPARA=\"CID\",1")
        self.send_at(f"AT+HTTPPARA=\"URL\",\"http://195.35.23.26/api/potholes\"")
        self.send_at("AT+HTTPPARA=\"CONTENT\",\"application/json\"")
        self.send_at(f"AT+HTTPDATA={len(json_data)},10000")
        try:
            self.ser.write(json_data.encode())
            time.sleep(2)
            self.send_at("AT+HTTPACTION=1") # POST
            self.send_at("AT+HTTPTERM")
        except:
            pass
