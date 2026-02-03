# How to Run the Smart Pothole Detection System

This project is divided into 4 main parts. Follow these steps to get everything running:

## 1. Local Backend & Dashboard (Run on your PC)
This part receives data from the RC car and displays it on the web map.
1. **Navigate to the backend folder**:
   ```powershell
   cd backend
   ```
2. **Install Dependencies**:
   ```powershell
   pip install fastapi uvicorn mysql-connector-python
   ```
3. **Setup Database**:
   - Open your MySQL terminal.
   - Run the commands found in `backend/schema.sql`.
4. **Start the Server**:
   ```powershell
   python main.py
   ```
5. **View Dashboard**: Open `dashboard/index.html` in your browser.

---

## 2. Raspberry Pi (Run on the RC Car)
Ensure you are connected to the Raspberry Pi via SSH.
1. **Move files to the Pi**: (You already seem to be using `scp` for this)
   ```powershell
   scp -r raspi admin@192.168.137.17:~/pothole_detection
   ```
2. **SSH into the Pi**:
   ```powershell
   ssh admin@192.168.137.17
   ```
3. **Run Setup**:
   ```bash
   cd ~/pothole_detection
   chmod +x setup_pi.sh
   ./setup_pi.sh
   ```
4. **Start the System**:
   ```bash
   python3 main.py
   ```

---

## 3. ESP32-CAM (The Camera)
1. Open `esp32cam/esp32cam.ino` in the **Arduino IDE**.
2. **Update WiFi**: Change `YOUR_WIFI_SSID` and `YOUR_WIFI_PASSWORD` to your actual details.
3. **Flash**: Connect your ESP32-CAM and click "Upload".

---

## 4. Testing (Bluetooth Control)
1. Pair your phone/PC with the **HC-05 Bluetooth module**.
2. Open a Bluetooth Serial Terminal app.
3. Send these characters to move the car:
   - `f` (Forward)
   - `b` (Backward)
   - `l` (Left)
   - `r` (Right)
   - `s` (Stop)

---

### Troubleshooting the "requirements.txt" error:
The reason your command failed is that you were in the root folder, but the file is inside the `raspi` folder. On your PC, you should run:
```powershell
pip install -r raspi/requirements.txt
```
*(Note: RPi.GPIO will only work on the Raspberry Pi hardware, not on Windows)*.
