#!/bin/bash

# This script helps enable additional UARTs on Raspberry Pi 4/5
# Required for LiDAR, GPS, GSM, and Bluetooth modules

CONFIG_FILE="/boot/firmware/config.txt"
if [ ! -f "$CONFIG_FILE" ]; then
    CONFIG_FILE="/boot/config.txt"
fi

echo "Updating $CONFIG_FILE to enable UARTs..."

# Backup config.txt
sudo cp $CONFIG_FILE "${CONFIG_FILE}.bak"

# Add UART overlays if they don't exist
# UART2: GPIO 0, 1 (GSM)
# UART3: GPIO 4, 5 
# UART4: GPIO 8, 9 
# UART5: GPIO 12, 13 (GPS)

grep -q "dtoverlay=uart2" $CONFIG_FILE || echo "dtoverlay=uart2" | sudo tee -a $CONFIG_FILE
grep -q "dtoverlay=uart5" $CONFIG_FILE || echo "dtoverlay=uart5" | sudo tee -a $CONFIG_FILE

echo "UART2 (GPIO 0/1) and UART5 (GPIO 12/13) enabled."
echo "PLEASE REBOOT YOUR RASPBERRY PI FOR CHANGES TO TAKE EFFECT:"
echo "sudo reboot"
