import serial
import time

def test_gsm():
    print("--- SIM800L GSM Configuration & Test ---")
    
    # Normally on UART2 (GPIO 0/1) -> /dev/ttyAMA1
    port = "/dev/ttyAMA1" 
    baud = 9600
    
    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"Opening port {port}...")
        
        def send_at(cmd, expected="OK", wait=2):
            print(f"Sending: {cmd}")
            ser.write((cmd + "\r\n").encode())
            time.sleep(wait)
            resp = ser.read(ser.in_waiting).decode(errors='ignore')
            print(f"Response: {resp.strip()}")
            return expected in resp

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
            if send_at(cmd):
                success_count += 1
            else:
                print(f"FAILED: {desc}")

        print(f"\n--- Result: {success_count}/{len(tests)} tests passed ---")
        if success_count < len(tests):
            print("Troubleshooting:")
            print("- Ensure SIM800L has 4V-4.2V (High current during burst).")
            print("- Ensure Antenna is connected.")
            print("- Check TX/RX wiring.")
        
        ser.close()
    except Exception as e:
        print(f"CRITICAL ERROR: Could not open serial port: {e}")

if __name__ == "__main__":
    test_gsm()
