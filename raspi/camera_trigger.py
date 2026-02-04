import RPi.GPIO as GPIO
import time
import serial

class ESP32Trigger:
    def __init__(self, pin_or_port=11, baud=115200):
        self.is_serial = False
        self.ser = None
        
        # Check if user passed a Serial Port string (e.g. /dev/ttyUSB0)
        # OR if we should auto-detect USB
        
        # Attempts to connect to USB Serial first (as user requested USB connection)
        try:
            # Common USB Serial drivers
            ports = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0"]
            for port in ports:
                try:
                    self.ser = serial.Serial(port, baud, timeout=1)
                    print(f"ESP32-CAM: Connected via USB Serial on {port}")
                    self.is_serial = True
                    break
                except:
                    continue
        except Exception as e:
            print(e)

        # Fallback to GPIO if no Serial found
        if not self.is_serial:
            print("ESP32-CAM: USB Serial not found. Falling back to GPIO Trigger (Pin 11).")
            self.pin = pin_or_port if isinstance(pin_or_port, int) else 11
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.LOW)

    def trigger(self):
        if self.is_serial and self.ser:
            try:
                print("Sending CAPTURE command to ESP32 via USB...")
                self.ser.write(b'c') # Send 'c' character
            except Exception as e:
                print(f"ESP32 Serial Error: {e}")
        else:
            print(f"Triggering ESP32-CAM GPIO {self.pin}...")
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.pin, GPIO.LOW)
