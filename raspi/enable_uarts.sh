#!/bin/bash

# Updated enable_uarts.sh to match the explicit wiring request
# LiDAR: UART0 (Default)
# GSM: UART2 (GPIO 0/1)
# GPS: UART5 (GPIO 12/13)

CONFIG_FILE="/boot/firmware/config.txt"
if [ ! -f "$CONFIG_FILE" ]; then
    CONFIG_FILE="/boot/config.txt"
fi

echo "Updating $CONFIG_FILE configuration..."

# 1. Enable UART2 for GSM (GPIO 0, 1)
grep -q "dtoverlay=uart2" $CONFIG_FILE || echo "dtoverlay=uart2" | sudo tee -a $CONFIG_FILE

# 2. Enable UART5 for GPS (GPIO 12, 13)
grep -q "dtoverlay=uart5" $CONFIG_FILE || echo "dtoverlay=uart5" | sudo tee -a $CONFIG_FILE

# 3. Ensure UART0 is enabled (enabled by default usually, but good to check)
grep -q "enable_uart=1" $CONFIG_FILE || echo "enable_uart=1" | sudo tee -a $CONFIG_FILE

echo "Configuration updated."
echo "CRITICAL: You MUST reboot for these UART ports to appear."
echo "sudo reboot"
