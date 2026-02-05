import serial
import time

def test_gps():
    print("--- NEO-6M GPS Configuration & Test ---")
    
    # Potential UART ports on Raspberry Pi
    # UART0 (/dev/ttyS0), UART1 (/dev/ttyAMA0), UART2-5 (/dev/ttyAMA1-4)
    ports = ["/dev/ttyAMA0", "/dev/ttyS0", "/dev/ttyAMA1", "/dev/ttyAMA5"]
    baud = 9600
    
    found = False
    for port in ports:
        print(f"Checking {port}...")
        try:
            ser = serial.Serial(port, baudrate=baud, timeout=1)
            time.sleep(1) # Wait for buffer
            
            # Read a few lines to check for NMEA data ($GPRMC, $GPGGA, etc.)
            for _ in range(5):
                line = ser.readline().decode('ascii', errors='ignore')
                if "$" in line:
                    print(f"SUCCESS: GPS data detected on {port}!")
                    print(f"Sample Data: {line.strip()}")
                    found = True
                    break
            
            if found:
                print("\nNote: Valid fix (location) requires an antenna and outdoor view.")
                print("If you see '$GPGGA,,,,,,' it means connection is good but no satellites yet.")
                ser.close()
                break
            ser.close()
        except Exception as e:
            continue

    if not found:
        print("\nRESULT: GPS not found.")
        print("Required Fixes:")
        print("1. Ensure 'enable_uart=1' is in /boot/config.txt")
        print("2. Check wiring: GPS TX -> Pi RX, GPS RX -> Pi TX")
        print("3. Check Power: NEO-6M needs stable 3.3V or 5V (standard is 3.3V VCC)")

if __name__ == "__main__":
    test_gps()
