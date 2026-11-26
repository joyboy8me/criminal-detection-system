import face_recognition
import cv2
import pickle
import requests
from datetime import datetime

# -------------------------------
# CONFIGURATION
# -------------------------------
ALERT_API_URL = "http://localhost:5000/api/alert"  # FIXED
CAMERA_INDEX = 0
TOLERANCE = 0.45
FRAME_SCALE = 0.25
ALERT_COOLDOWN = 15  # seconds
DEFAULT_LOCATION = "Unknown Location"  # You can make this dynamic later

# -------------------------------
# ALERT FUNCTION
# -------------------------------
def send_alert(name):
    try:
        data = {
            "name": name,
            "location": DEFAULT_LOCATION,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        response = requests.post(ALERT_API_URL, json=data)
        if response.status_code == 200:
            print(f"[✅ ALERT SENT] {name}")
        else:
            print(f"[❌ ERROR] Alert failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[❌ EXCEPTION] Failed to send alert: {e}")

# -------------------------------
# LOAD KNOWN ENCODINGS
# -------------------------------
print("[INFO] Loading known encodings...")
with open("encodings.pickle", "rb") as file:
    data = pickle.load(file)
print(f"[INFO] Loaded encodings for {len(data['names'])} faces")

# -------------------------------
# START CAMERA
# -------------------------------
video_capture = cv2.VideoCapture(CAMERA_INDEX)
if not video_capture.isOpened():
    raise IOError("[ERROR] Cannot access webcam")

print("[INFO] Starting video stream...")

# To avoid spamming alerts
recent_alerts = {}

try:
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("[ERROR] Failed to grab frame")
            break

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations) if face_locations else []

        names = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(data["encodings"], face_encoding, tolerance=TOLERANCE)
            name = "Unknown"

            if True in matches:
                matched_idxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matched_idxs:
                    matched_name = data["names"][i]
                    counts[matched_name] = counts.get(matched_name, 0) + 1

                name = max(counts, key=counts.get)

            # Send alert only if name is known and enough cooldown has passed
            now = datetime.now()
            last_alert_time = recent_alerts.get(name)
            if name != "Unknown" and (not last_alert_time or (now - last_alert_time).seconds > ALERT_COOLDOWN):
                send_alert(name)
                recent_alerts[name] = now

            names.append(name)

        # Draw results
        for ((top, right, bottom, left), name) in zip(face_locations, names):
            top = int(top / FRAME_SCALE)
            right = int(right / FRAME_SCALE)
            bottom = int(bottom / FRAME_SCALE)
            left = int(left / FRAME_SCALE)

            # Draw rectangle
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)  # Red box for unknown
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # Draw label
            label = f"{name} - {datetime.now().strftime('%H:%M:%S')}"
            cv2.putText(frame, label, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("Criminal Detection - Live Feed", frame)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except Exception as e:
    print(f"[EXCEPTION] {e}")

finally:
    print("[INFO] Releasing camera and closing windows...")
    video_capture.release()
    cv2.destroyAllWindows()
