import os
import subprocess
import RPi.GPIO as GPIO
import glob

def get_cpu_temp():
    try:
        temp = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        return temp.replace("temp=", "").strip()
    except:
        return "Unknown"

def test_pi_system():
    print("--- Raspberry Pi 4B System Health Check ---")
    
    # 1. CPU Temperature
    print(f"\n[1] CPU Temperature: {get_cpu_temp()}")
    
    # 2. GPIO Verification
    print("\n[2] GPIO Verification...")
    try:
        GPIO.setmode(GPIO.BCM)
        print("SUCCESS: GPIO library initialized (BCM Mode).")
    except Exception as e:
        print(f"FAILED: GPIO library error: {e}")
    
    # 3. Disk Space
    print("\n[3] Disk Space Usage:")
    try:
        usage = subprocess.check_output(["df", "-h", "/"]).decode().split('\n')[1]
        print(usage)
    except:
        print("Error reading disk usage.")

    # 4. UART Check (Robust)
    print("\n[4] Enabled Serial/UART Ports:")
    ports = []
    # Check common patterns
    patterns = ["/dev/ttyAMA*", "/dev/ttyS0", "/dev/ttyUSB*", "/dev/serial0", "/dev/serial1"]
    for p in patterns:
        ports.extend(glob.glob(p))
    
    # Dedup and sort
    ports = sorted(list(set(ports)))
    
    if ports:
        for u in ports:
            print(f"- {u}")
        
        # Determine primary console UART
        if "/dev/serial0" in ports:
            real_path = os.path.realpath("/dev/serial0")
            print(f"Note: /dev/serial0 -> {real_path} (Primary UART)")
    else:
        print("WARNING: No standard UART ports found!")
        print("Check /boot/config.txt for 'enable_uart=1'.")
        # Try to read config (might need permissions, but worth a shot)
        try:
            config_path = "/boot/firmware/config.txt"
            if not os.path.exists(config_path):
                config_path = "/boot/config.txt"
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    content = f.read()
                    if "enable_uart=1" in content:
                        print(f"Config Check: 'enable_uart=1' FOUND in {config_path}.")
                    else:
                        print(f"Config Check: 'enable_uart=1' NOT FOUND in {config_path}.")
        except Exception as e:
            print(f"Config Check: Could not read config file: {e}")

    print("\n--- System Check Complete ---")

if __name__ == "__main__":
    test_pi_system()
