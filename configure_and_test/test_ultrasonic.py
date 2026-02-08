import RPi.GPIO as GPIO
import time

# Configuration (BCM Pins)
TRIG = 17
ECHO = 18

def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()
    timeout = time.time() + 0.1

    while GPIO.input(ECHO) == 0:
        start_time = time.time()
        if start_time > timeout: return -1

    while GPIO.input(ECHO) == 1:
        stop_time = time.time()
        if stop_time > timeout: return -1

    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance

def test_ultrasonic():
    print("--- HC-SR04 Ultrasonic Configuration & Test ---")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    print(f"Pins: TRIG={TRIG}, ECHO={ECHO}")
    print("Starting readings... Hold an object in front of the sensor. Press Ctrl+C to stop.")
    
    try:
        while True:
            dist = get_distance()
            if dist == -1:
                print("Error: Sensor Timeout. Check wiring (VCC=5V, GND, Trig=23, Echo=24)")
            else:
                print(f"Distance: {dist:.1f} cm")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    test_ultrasonic()
