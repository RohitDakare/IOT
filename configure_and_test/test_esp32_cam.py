import RPi.GPIO as GPIO
import time
import serial
import sys

# Configuration
TRIGGER_PIN = 11
BAUD_RATE = 115200
USB_PORTS = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0"]

def test_esp32_cam():
    print("--- ESP32-CAM Configuration & Test ---")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    connected = False
    ser = None

    # Step 1: Test USB Serial Connection
    print("\n[1] Checking USB Serial Connection...")
    for port in USB_PORTS:
        try:
            ser = serial.Serial(port, BAUD_RATE, timeout=2)
            print(f"SUCCESS: Connected to ESP32 on {port}")
            connected = True
            break
        except Exception:
            continue

    if connected:
        print("Action: Sending 'c' (Capture) command to ESP32...")
        ser.write(b'c')
        time.sleep(1)
        if ser.in_waiting > 0:
            resp = ser.read(ser.in_waiting).decode(errors='ignore')
            print(f"ESP32 Response: {resp}")
        ser.close()
    else:
        print("RESULT: No USB Serial device found.")
        
        # Step 2: Test GPIO Trigger Fallback
        print(f"\n[2] Testing GPIO Trigger Fallback (BCM Pin {TRIGGER_PIN})...")
        try:
            GPIO.setup(TRIGGER_PIN, GPIO.OUT)
            print(f"Action: Pulled Pin {TRIGGER_PIN} HIGH for 1 second...")
            GPIO.output(TRIGGER_PIN, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(TRIGGER_PIN, GPIO.LOW)
            print("SUCCESS: GPIO signal sent. Ensure your ESP32 is wired to GPIO 11.")
        except Exception as e:
            print(f"ERROR: GPIO setup failed: {e}")

    print("\n--- Test Complete ---")
    GPIO.cleanup()

if __name__ == "__main__":
    test_esp32_cam()
