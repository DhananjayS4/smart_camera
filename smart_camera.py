import cv2, time, datetime, os, threading
import numpy as np
from collections import deque


STREAM_URL = os.environ.get("STREAM_URL", "http://ip_address/video")
SAVE_DIR = "captures"
os.makedirs(SAVE_DIR, exist_ok=True)

TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID  = "TELEGRAM_CHAT_ID"
TELEGRAM_ENABLED = True

RESIZE_WIDTH = 400
GAUSS_BLUR = (21,21)
ACCUM_WEIGHT = 0.05
MOTION_THRESH = 30
MIN_AREA = 3500
DETECT_CONS_FRAMES = 3
COOLDOWN = 8.0
DEDUP_DIFF = 6.0

def open_capture(url):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        try:
            cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        except Exception:
            pass
    return cap

def mean_gray_diff(a, b):
    d = cv2.absdiff(a, b)
    return float(d.mean())

def send_telegram_image_async(path, caption=None):
    if not TELEGRAM_ENABLED:
        return
    def _upload():
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        try:
            with open(path, "rb") as fh:
                files = {"photo": fh}
                data = {"chat_id": TELEGRAM_CHAT_ID}
                if caption:
                    data["caption"] = caption
                r = requests.post(url, files=files, data=data, timeout=30)
                if r.status_code != 200:
                    print("[WARN] Telegram send failed", r.status_code, r.text[:200])
                else:
                    print("[INFO] Telegram image sent")
        except Exception as e:
            print("[WARN] Telegram upload error:", e)
    threading.Thread(target=_upload, daemon=True).start()

def main():
    print("[INFO] Starting motion detector with Telegram alerts:", TELEGRAM_ENABLED)
    cap = open_capture(STREAM_URL)
    if not cap or not cap.isOpened():
        print("[ERROR] Cannot open stream:", STREAM_URL)
        return

    bg_acc = None
    last_saved = 0
    recent = deque(maxlen=DETECT_CONS_FRAMES)
    last_saved_small = None
    time.sleep(1.0)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.2)
            continue

        frame = cv2.resize(frame, (RESIZE_WIDTH, int(frame.shape[0] * RESIZE_WIDTH / frame.shape[1])))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, GAUSS_BLUR, 0)

        if bg_acc is None:
            bg_acc = gray.astype("float")
            recent.append(0)
            continue

        cv2.accumulateWeighted(gray, bg_acc, ACCUM_WEIGHT)
        background = cv2.convertScaleAbs(bg_acc)

        diff = cv2.absdiff(background, gray)
        _, thresh = cv2.threshold(diff, MOTION_THRESH, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)

        cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        motion_found = False
        for c in cnts:
            if cv2.contourArea(c) < MIN_AREA:
                continue
            motion_found = True
            break

        recent.append(1 if motion_found else 0)
        if sum(recent) >= DETECT_CONS_FRAMES:
            now = time.time()
            if (now - last_saved) >= COOLDOWN:
                small = cv2.resize(gray, (100,100))
                if last_saved_small is None:
                    diffval = DEDUP_DIFF + 1.0
                else:
                    diffval = mean_gray_diff(small, last_saved_small)

                if diffval >= DEDUP_DIFF:
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    fname = os.path.join(SAVE_DIR, f"motion_{ts}.jpg")
                    cv2.imwrite(fname, frame)
                    print(f"[MOTION] Saved {fname} diff={diffval:.2f}")
                    # send to telegram (async)
                    if TELEGRAM_ENABLED:
                        caption = f"Motion alert {ts}"
                        send_telegram_image_async(fname, caption=caption)
                    last_saved = now
                    last_saved_small = small.copy()
                else:
                    print(f"[SKIP] Similar to last saved (diff={diffval:.2f})")
        time.sleep(0.01)

    cap.release()

if __name__ == "__main__":
    main()
