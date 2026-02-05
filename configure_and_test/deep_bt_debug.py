import serial
import time
import os

def check_uart_status():
    print("--- 1. Checking UART Configuration ---")
    try:
        with open("/boot/config.txt", "r") as f:
            content = f.read()
            print(f"UART2 Enabled: {'uart2' in content}")
            print(f"UART3 Enabled: {'uart3' in content}")
            print(f"UART4 Enabled: {'uart4' in content}")
            print(f"UART5 Enabled: {'uart5' in content}")
            print(f"enable_uart=1: {'enable_uart=1' in content}")
    except:
        print("Could not read /boot/config.txt (Permission denied? - Run with sudo)")

    print("\n--- 2. Checking Active Serial Ports ---")
    ports = [f for f in os.listdir('/dev') if 'ttyAMA' in f or 'ttyS' in f or 'ttyUSB' in f or 'rfcomm' in f]
    print(f"Detected ports: {ports}")

def scan_all_ports_and_bauds():
    print("\n--- 3. Scanning All Ports for Data ---")
    print("Action: Keep sending 'f' from your phone continuously now!")
    
    ports = ["/dev/ttyS0", "/dev/ttyAMA0", "/dev/ttyAMA1", "/dev/ttyAMA2", "/dev/ttyAMA3", "/dev/ttyAMA4", "/dev/ttyAMA5", "/dev/rfcomm0"]
    bauds = [9600, 38400, 115200]
    
    found_any = False
    for port_path in ports:
        if not os.path.exists(port_path):
            continue
            
        for baud in bauds:
            try:
                # Use a very short timeout to scan quickly
                ser = serial.Serial(port_path, baud, timeout=0.5)
                # print(f"Checking {port_path} @ {baud}...", end="\r")
                
                # Check for 2 seconds
                end_time = time.time() + 2
                while time.time() < end_time:
                    if ser.in_waiting > 0:
                        data = ser.read(ser.in_waiting)
                        print(f"\n✨ DATA DETECTED! ✨")
                        print(f"PORT: {port_path}")
                        print(f"BAUD: {baud}")
                        print(f"RAW DATA: {data}")
                        try:
                            print(f"DECODED: {data.decode().strip()}")
                        except:
                            print("DECODED: (binary data)")
                        ser.close()
                        return
                ser.close()
            except Exception:
                continue
    
    print("\nNo data detected on any standard port/baud combination.")
    print("\n--- 🔧 TROUBLESHOOTING CHECKLIST ---")
    print("1. SWAP TX/RX: The wire from HC-05 'TX' MUST go to Pi 'RX'.")
    print("2. PINS: Are you on GPIO 14 (TX) & 15 (RX)? That's /dev/ttyS0 or /dev/ttyAMA0.")
    print("3. POWER: The HC-05 needs 5V but 3.3V logic. Ensure GND is shared between Pi and HC-05.")
    print("4. CONSOLE: If using /dev/ttyS0, go to 'sudo raspi-config' -> Interface -> Serial -> No to Login Console, Yes to Hardware Port.")

if __name__ == "__main__":
    check_uart_status()
    scan_all_ports_and_bauds()
