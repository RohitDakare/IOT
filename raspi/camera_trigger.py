import RPi.GPIO as GPIO
import time

class ESP32Trigger:
    def __init__(self, pin=11):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

    def trigger(self):
        print("Triggering ESP32-CAM on Pin 11...")
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(1) # Keep signal HIGH for 1 second
        GPIO.output(self.pin, GPIO.LOW)
