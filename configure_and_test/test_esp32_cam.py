import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'raspi')))

try:
    from communication import SoftwareSerial
    import RPi.GPIO as GPIO
except ImportError:
    print("Error: Could not import 'communication' or 'RPi.GPIO'.")
    SoftwareSerial = None
    import RPi.GPIO as GPIO # Fallback for simple GPIO test if needed

def test_esp32():
    print("--- ESP32-CAM Configuration & Test (Software Serial) ---")
    if SoftwareSerial is None: return

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # User Pins: TX=23, RX=24
    TX_PIN = 23
    RX_PIN = 24
    BAUD = 115200 # User specified 115200 for ESP32
    
    print(f"Using Software Serial on Pi TX={TX_PIN}, RX={RX_PIN} @ {BAUD} baud")
    print("WARNING: 115200 baud on Software Serial is unstable. If this fails, lower ESP32 baud.")
    
    try:
        ser = SoftwareSerial(tx=TX_PIN, rx=RX_PIN, baud=BAUD)
        
        print("Sending CAPTURE command ('c')...")
        ser.write('c')
        
        print("Command sent. Waiting 5s for any response (optional)...")
        # ESP might not send anything back, but we listen just in case
        timeout = time.time() + 5
        while time.time() < timeout:
             if ser.in_waiting:
                 try:
                     data = ser.read(1)
                     print(f"Received: {data}")
                 except:
                     pass
                 break
             time.sleep(0.1)
             
        print("Test Complete. Check if ESP32-CAM took a picture (Flash LED might blink).")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    test_esp32()
