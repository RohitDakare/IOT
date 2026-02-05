import os
import subprocess
import RPi.GPIO as GPIO

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
        print("SUCCESS: GPIO library initialized.")
    except Exception as e:
        print(f"FAILED: GPIO library error: {e}")
    
    # 3. Disk Space
    print("\n[3] Disk Space Usage:")
    try:
        usage = subprocess.check_output(["df", "-h", "/"]).decode().split('\n')[1]
        print(usage)
    except:
        print("Error reading disk usage.")

    # 4. UART Check
    print("\n[4] Enabled Serial/UART Ports:")
    try:
        uarts = subprocess.check_output(["ls", "/dev/ttyAMA*", "/dev/ttyS0", "/dev/ttyUSB*"], stderr=subprocess.DEVNULL).decode().split()
        for u in uarts:
            print(f"- {u}")
    except:
        print("No standard UART ports found or none enabled.")

    print("\n--- System Check Complete ---")

if __name__ == "__main__":
    test_pi_system()
