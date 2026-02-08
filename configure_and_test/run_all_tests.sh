#!/bin/bash

# Main Test Runner for Smart Pothole Detection System
# This script executes all hardware diagnostic tests in sequence.

echo "=========================================================="
echo "   🚀 STARTING FULL SYSTEM HARDWARE DIAGNOSTICS   "
echo "=========================================================="
date
echo ""

# 1. Raspberry Pi System Check
echo "----------------------------------------------------------"
echo "1. Checking Raspberry Pi 4B Health..."
python3 test_raspberry_pi.py
echo "----------------------------------------------------------"
echo ""

# 2. ESP32-CAM Trigger Test
echo "2. Triggering ESP32-CAM..."
python3 test_esp32_cam.py
echo ""

# 3. GPS Module Scan
echo "3. Scanning NEO-6M GPS Data..."
python3 test_gps.py
echo ""

# 4. GSM Module Diagnostics
echo "4. Running SIM800L AT Command Suite..."
python3 test_gsm.py
echo ""

# 5. Bluetooth Connectivity
echo "5. Testing HC-05 Connection (10s Timeout)..."
echo "Tip: Send a character from your phone now!"
python3 test_bluetooth.py
echo ""

# 6. Ultrasonic Sensor (Timed Test)
echo "6. Testing HC-SR04 Ultrasonic (5 seconds)..."
# We run this in the background, wait 5, then kill it so it doesn't block forever
python3 test_ultrasonic.py &
PID=$!
sleep 5
kill $PID 2>/dev/null
echo ""
# 7. LiDAR Test (TF02-Pro)
echo "7. Testing TF02-Pro LiDAR (Software Serial)..."
python3 test_lidar.py
echo ""
echo "----------------------------------------------------------"
echo "✅ ALL DIAGNOSTICS COMPLETED"
echo "Check the outputs above for any 'FAILED' or 'Error' messages."
echo "=========================================================="
