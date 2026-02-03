import serial
import time
import json

class GSM:
    def __init__(self, port, baud=9600):
        self.ser = serial.Serial(port, baud, timeout=1)
        self.init_gsm()

    def init_gsm(self):
        self.send_at("AT")
        self.send_at("AT+SAPBR=3,1,\"Contype\",\"GPRS\"")
        self.send_at("AT+SAPBR=3,1,\"APN\",\"internet\"") # Adjust APN
        self.send_at("AT+SAPBR=1,1")

    def send_at(self, cmd, wait=1):
        self.ser.write((cmd + "\r\n").encode())
        time.sleep(wait)
        return self.ser.read(self.ser.in_waiting).decode()

    def send_data(self, data):
        json_data = json.dumps(data)
        self.send_at("AT+HTTPINIT")
        self.send_at("AT+HTTPPARA=\"CID\",1")
        self.send_at(f"AT+HTTPPARA=\"URL\",\"http://195.35.23.26/api/potholes\"")
        self.send_at("AT+HTTPPARA=\"CONTENT\",\"application/json\"")
        self.send_at(f"AT+HTTPDATA={len(json_data)},10000")
        self.ser.write(json_data.encode())
        time.sleep(2)
        self.send_at("AT+HTTPACTION=1") # POST
        self.send_at("AT+HTTPTERM")
