import serial
import time
import adafruit_gps

def check_gps():
    print("--- Neo-6M GPS Diagnostic Tool ---")
    potential_ports = ["/dev/ttyAMA5", "/dev/serial0", "/dev/ttyAMA1", "/dev/ttyS0"]
    
    found_port = None
    for port in potential_ports:
        try:
            ser = serial.Serial(port, baudrate=9600, timeout=2)
            print(f"Checking {port}...")
            time.sleep(1)
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
                if "$GP" in data:
                    print(f"SUCCESS: GPS NMEA data found on {port}!")
                    found_port = port
                    ser.close()
                    break
            ser.close()
        except Exception as e:
            print(f"Could not open {port}: {e}")

    if not found_port:
        print("\nERROR: No GPS data detected on any common port.")
        print("1. Ensure GPS TX is connected to Pi RX.")
        print("2. Ensure enable_uarts.sh script was run and Pi was rebooted.")
        return

    # Start live tracking
    ser = serial.Serial(found_port, baudrate=9600, timeout=1)
    gps = adafruit_gps.GPS(ser, debug=False)
    
    print("\nStarting live coordinate tracking. Press Ctrl+C to stop.")
    print("NOTE: GPS needs an outdoor clear sky view to get a 'Fix'.")
    
    try:
        while True:
            gps.update()
            if gps.has_fix:
                print(f"\n--- FIXED ---")
                print(f"Latitude:  {gps.latitude:.6f}")
                print(f"Longitude: {gps.longitude:.6f}")
                print(f"Satellites: {gps.satellites}")
                print(f"Altitude:   {gps.altitude_m}m")
            else:
                print("Waiting for Fix... (Sats: " + str(gps.satellites if gps.satellites else 0) + ")", end="\r")
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Diagnostic.")
    finally:
        ser.close()

if __name__ == "__main__":
    check_gps()
