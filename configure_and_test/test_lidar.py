import sys
import os
import time

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'raspi')))

try:
    from sensors import LiDAR
    import RPi.GPIO as GPIO
except ImportError:
    print("Error: Could not import 'sensors' or 'RPi.GPIO'. Run this on the Raspberry Pi.")
    LiDAR = None

def test_lidar():
    if LiDAR is None: return

    # Ensure GPIO mode is set for SoftwareSerial
    GPIO.setmode(GPIO.BCM)

    print("=== Testing LiDAR (TF02-Pro) ===")
    print("Configuration: Using Software Serial (Bit-Banging) due to custom wiring.")
    print("TX Pin (Pi): GPIO 6 (Physical 31) -> Connected to LiDAR RX (Yellow)")
    print("RX Pin (Pi): GPIO 12 (Physical 32) -> Connected to LiDAR TX (Green)")
    print("Baud Rate: 115200 (Default for TF02-Pro)")
    print("WARNING: 115200 baud is very high for Python Software Serial. Data may be unstable.")
    
    # Initialize LiDAR with custom pins
    try:
        lidar = LiDAR(port=None, tx=6, rx=12, baud=115200)
        print("LiDAR Initialized. Starting read loop (Ctrl+C to stop)...")
        
        start_time = time.time()
        valid_readings = 0
        total_attempts = 0
        
        while time.time() - start_time < 10: # Test for 10 seconds
            dist = lidar.get_distance()
            total_attempts += 1
            
            if dist > 0:
                valid_readings += 1
                print(f"Distance: {dist} m")
            else:
                # print(".", end="", flush=True) # Dot for no data
                pass
            
            time.sleep(0.1)
            
        print("\nTest Finished.")
        print(f"Valid Readings: {valid_readings}/{total_attempts}")
        
        if valid_readings == 0:
            print("\nTROUBLESHOOTING:")
            print("1. Check wiring: Green -> Pin 32 (GPIO 12), Yellow -> Pin 31 (GPIO 6).")
            print("2. 115200 baud bit-banging is unreliable. CONSIDER USING HARDWARE UART5:")
            print("   - Connect Green (TX) to Pin 33 (GPIO 13/UART5_RX)")
            print("   - Connect Yellow (RX) to Pin 32 (GPIO 12/UART5_TX)")
            print("   - Enable UART5 in /boot/config.txt")
            
    except Exception as e:
        print(f"Error initializing LiDAR: {e}")
        import traceback
        traceback.print_exc()

def configure_baud_rate():
    """
    Attempt to lower baud rate to 9600 for better SoftwareSerial stability.
    Command: 5A 06 03 LL HH SU
    9600 = 0x2580 -> LL=0x80, HH=0x25
    Checksum = 0x5A + 0x06 + 0x03 + 0x80 + 0x25 = 0x108 -> 0x08
    Command: 5A 06 03 80 25 08
    """
    print("\n--- Baud Rate Configuration (Experimental) ---")
    print("Attempting to decrease baud rate to 9600 for stability...")
    
    # Initialize at 115200 to send command
    try:
        from communication import SoftwareSerial
        # Temporary instance just to write
        ser = SoftwareSerial(tx=6, rx=12, baud=115200)
        
        # Command to set 9600
        cmd = b'\x5A\x06\x03\x80\x25\x08'
        print(f"Sending command: {cmd.hex()}")
        ser.write(cmd)
        
        print("Command sent. waiting 1s...")
        time.sleep(1)
        
        print("Re-initializing at 9600 baud to verify...")
        lidar_low = LiDAR(port=None, tx=6, rx=12, baud=9600)
        
        # Try reading
        start = time.time()
        success = False
        while time.time() - start < 5:
            d = lidar_low.get_distance()
            if d > 0:
                print(f"Success! Distance at 9600: {d} m")
                success = True
                break
            time.sleep(0.1)
            
        if success:
            print("Baud rate successfully changed to 9600. Please update your code to use 9600.")
        else:
            print("Failed to verify 9600 baud. Device might still be at 115200 or command failed.")
            
    except Exception as e:
        print(f"Configuration failed: {e}")

if __name__ == "__main__":
    test_lidar()
    
    # Uncomment to try changing baud rate if reading fails consistently
    # prompt = input("\nAttempt to configure baud rate to 9600? (y/n): ")
    # if prompt.lower() == 'y':
    #     configure_baud_rate()
