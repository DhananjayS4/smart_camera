# SmartCam — Intelligent Motion Detection & Monitoring System

A Raspberry Pi–based smart surveillance system with:

* **Real-time camera streaming (via Flask Web UI)**
* **Intelligent motion detection (OpenCV)**
* **Automatic capture & image saving**
* **Telegram alerts with captured images**
* **Modern, stylish dashboard UI**
* **Project PPT download integration**

---

## Project structure

```
smart_camera/
├── app.py                         # Flask server (Web UI + live stream)
├── smart_camera.py                # Motion detection with enhanced filtering
├── motion_detector_telegram    # Motion detection + Telegram alerts
|
├── captures/                      # Saved motion captures
├── templates/
│   └── index.html                 # Modern dashboard UI
├── venv/                          # Python virtual environment
└── README.md
```

---

## Features

* **Live streaming** via Flask UI at `http://<RPI-IP>:5000`.
* **Robust motion detection** using adaptive background subtraction and debounce logic.
* **Telegram image alerts** (async upload) when motion is detected.
* **Stylish web dashboard** with gallery and PPT download.

---

## Quick setup

```bash
# create project folder (if not already)
mkdir -p ~/smart_camera && cd ~/smart_camera

# create virtual environment
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install --upgrade pip
pip install opencv-python-headless flask numpy imutils requests
```

---

## Configure camera stream

Set `STREAM_URL` in your scripts to your camera MJPEG stream (for IP Webcam app):

```python
STREAM_URL = "http://<PHONE-IP>:8080/video"
```

---

## Telegram alerts (optional)

1. Create a bot with **@BotFather** and obtain `BOT_TOKEN`.
2. Get your `TELEGRAM_CHAT_ID` (use `@userinfobot` or check `getUpdates`).
3. Export env vars or paste into the script:

```bash
export TELEGRAM_BOT_TOKEN="<YOUR_TOKEN>"
export TELEGRAM_CHAT_ID="<YOUR_CHAT_ID>"
```

---

## Run

Start motion detector (with Telegram integration):

```bash
cd ~/smart_camera
source venv/bin/activate
python3 motion_detector_telegram.py
```

Start the web UI:

```bash
cd ~/smart_camera
source venv/bin/activate
python3 app.py
```

Open your browser to `http://<RPI-IP>:5000`.

---

## Download project PPT

You can download the project presentation from the dashboard. The PPT uploaded to this environment is available here:

[Download Project PPT](/mnt/data/Advanced_Python_Project.pptx)

---

## Tuning & tips

* Increase `MIN_AREA` or `MOTION_THRESH` in `motion_detector_strict.py` to reduce false positives.
* If your Pi lacks tracker constructors, run in detection-only mode (script supports fallback).
* Use system `python3-opencv` if you want tracker support on Raspberry Pi.

---

## Optional next steps

* Add face recognition (face_recognition library)
* Run MobileNetSSD only after motion is detected (saves CPU)
* Add video clip recording (pre-buffered)
* Auto-delete old captures

---

If you want, I can also generate a PDF report or slides from this README.
