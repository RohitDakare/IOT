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

def test_gsm():
    print("--- SIM800L GSM Configuration & Test (Software Serial) ---")
    if SoftwareSerial is None: return

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # User Wiring: TX=16, RX=20
    TX_PIN = 16
    RX_PIN = 20
    BAUD = 9600

    print(f"Using Software Serial on TX={TX_PIN}, RX={RX_PIN} @ {BAUD} baud")
    
    try:
        ser = SoftwareSerial(tx=TX_PIN, rx=RX_PIN, baud=BAUD)
        
        def send_at(cmd, expected="OK", wait=2):
            print(f"Sending: {cmd}")
            ser.write(cmd + "\r\n") # SoftwareSerial write string or bytes
            time.sleep(wait)
            # SoftwareSerial read is blocking and tricky.
            # We implemented a simplistic read in communication.py
            # Let's try to read response?
            # Or just wait and assume if no error?
            # Ideally we read back.
            try:
                # Attempt to read some bytes. 
                # Since we don't know how many, we might read a few times?
                # SoftwareSerial.read(count) blocks until start bit.
                # If no response, it hangs forever!
                # We need a non-blocking check? 
                # Our implementation has in_waiting property now!
                start = time.time()
                resp = ""
                while time.time() - start < wait:
                   if ser.in_waiting:
                       data = ser.read(1)
                       resp += data.decode(errors='ignore')
                   else:
                       time.sleep(0.01)
                
                print(f"Response: {resp.strip()}")
                return expected in resp
            except Exception as e:
                print(f"Read Error: {e}")
                return False

        # Tests
        tests = [
            ("AT", "Basic Communication"),
            ("AT+CPIN?", "SIM Card Presence"),
            ("AT+CSQ", "Signal Strength"),
            ("AT+CREG?", "Network Registration"),
            ("AT+COPS?", "Network Carrier Name")
        ]
        
        success_count = 0
        for cmd, desc in tests:
            print(f"\n[Test] {desc}")
            # Try/Except generic to avoid crash on single command failure
            try:
                if send_at(cmd):
                    success_count += 1
                    print("PASS")
                else:
                    print(f"FAILED: {desc} (No 'OK' or expected response)")
            except:
                print("FAILED: Timeout/Exception")

        print(f"\n--- Result: {success_count}/{len(tests)} tests passed ---")
        if success_count == 0:
            print("Troubleshooting:")
            print("- Ensure SIM800L has 4V-4.2V (High current during burst).")
            print("- Check TX/RX wiring: Pi TX(16) -> SIM RX, Pi RX(20) -> SIM TX.")
            print("- SoftwareSerial is timing sensitive. Ensure no heavy load on Pi.")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gsm()
