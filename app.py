from flask import Flask, render_template, Response, send_from_directory, request, redirect, url_for, jsonify
import cv2, os, time, threading

ROOT = os.path.expanduser("~/smart_camera")
CAPTURES_DIR = os.path.join(ROOT, "captures")
STREAM_URL = os.environ.get("STREAM_URL", "http://10.22.145.12:8080/video")
PPT_LOCAL_PATH = os.environ.get("PPT_PATH", "/mnt/data/Advanced_Python_Project.pptx")
ALERT_FLAG = os.path.join(ROOT, ".alerts_enabled")  

os.makedirs(CAPTURES_DIR, exist_ok=True)
app = Flask(__name__, template_folder="templates")

class VideoGrabber:
    def __init__(self, src):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.frame = None
        self.grabbed = False
        self.stopped = False
        t = threading.Thread(target=self.update, daemon=True)
        t.start()

    def update(self):
        while not self.stopped:
            if not self.cap.isOpened():
                try:
                    self.cap = cv2.VideoCapture(self.src)
                except Exception:
                    time.sleep(0.5)
                    continue
            grabbed, frame = self.cap.read()
            if grabbed:
                self.grabbed = True
                self.frame = frame
            else:
                time.sleep(0.05)

    def read_jpeg(self):
        if not self.grabbed or self.frame is None:
            return None
        ret, buf = cv2.imencode(".jpg", self.frame)
        if not ret:
            return None
        return buf.tobytes()

    def stop(self):
        self.stopped = True
        try:
            self.cap.release()
        except Exception:
            pass

vg = VideoGrabber(STREAM_URL)

def gen_frames():
    while True:
        jpg = vg.read_jpeg()
        if jpg is None:
            time.sleep(0.05)
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')

@app.route("/")
def index():
    files = sorted(os.listdir(CAPTURES_DIR), reverse=True)
    alerts_enabled = os.path.exists(ALERT_FLAG)
    return render_template("index.html", files=files, alerts_enabled=alerts_enabled)

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/captures/<path:filename>")
def capture_file(filename):
    return send_from_directory(CAPTURES_DIR, filename, as_attachment=False)

@app.route("/download_ppt")
def download_ppt():
    ppt = PPT_LOCAL_PATH
    if not os.path.exists(ppt):
        return "PPT not found on server.", 404
    d, fname = os.path.split(ppt)
    return send_from_directory(d, fname, as_attachment=True)

@app.route("/toggle_alerts", methods=["POST"])
def toggle_alerts():
    action = request.form.get("action")
    if action == "enable":
        open(ALERT_FLAG, "w").close()
    else:
        try:
            os.remove(ALERT_FLAG)
        except Exception:
            pass
    return redirect(url_for("index"))

@app.route("/api/alerts_enabled")
def api_alerts_enabled():
    return jsonify({"enabled": os.path.exists(ALERT_FLAG)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
