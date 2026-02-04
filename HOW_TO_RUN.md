# 🚀 Comprehensive Guide: Running the Pothole Detection System

This project is a multi-device system including a Backend Server, Web Dashboard, AI Model Training, Raspberry Pi Logic, and ESP32 Vision.

---

## 💻 1. Backend Server & Dashboard (On your PC)
The backend is now simplified with **SQLite** (no MySQL installation required).

1.  **Installation**:
    ```powershell
    cd backend
    pip install -r requirements.txt
    ```
2.  **Run the Server**:
    - Just double-click the `backend/run_backend.bat` file, or run:
    ```powershell
    python main.py
    ```
3.  **Open Dashboard**:
    - Open your browser and navigate to `http://localhost:8000`.
4.  **Mock Testing**:
    - To see the map working without the robot, run:
    ```powershell
    python test_api_mock.py
    ```

---

## 🧠 2. AI Model Training (In `ml_training/`)
If you want to train your own custom pothole detection model:

1.  **Preparation**:
    - Collect images of potholes and annotate them in YOLOv8 format.
2.  **Training**:
    ```powershell
    cd ml_training
    python train.py
    ```
3.  **Optimizing for Edge**:
    - Convert your model for the Raspberry Pi and ESP32-CAM:
    ```powershell
    python export.py
    ```

---

## 🤖 3. Raspberry Pi (On the Robot)
The Pi manages the motors, GPS, and sensor fusion.

1.  **Transfer Files**:
    ```powershell
    scp -r raspi <pi_user>@<pi_ip>:~/pothole_detection
    ```
2.  **Terminal Setup**:
    - SSH into your Pi and run:
    ```bash
    cd ~/pothole_detection
    chmod +x setup_pi.sh
    ./setup_pi.sh
    python3 main.py
    ```
3.  **Communication**:
    - Ensure `raspi/communication.py` has the correct `URL` pointing to your PC's IP address.

---

## 📷 4. ESP32-CAM (Vision Sensor)
The camera captures photos when triggered by the Pi or AI.

1.  **Arduino IDE**:
    - Open `esp32cam/esp32cam.ino`.
    - Update your **WiFi SSID/Password**.
    - Update `serverUrl` to your PC's IP address.
2.  **Flash**: Connect the ESP32-CAM via an FTDI adapter and upload.

---

## 🎮 5. Operation & Control
1.  **Connect Bluetooth**: Pair your phone/PC with the **HC-05** module.
2.  **Manual Control**: Use a serial terminal to send movement commands:
    - `f`: Forward | `b`: Backward | `l`: Left | `r`: Right | `s`: Stop
3.  **Detection**: When a pothole is detected (depth > 5cm), the ESP32-CAM will flash, and data will appear on your dashboard instantly.
