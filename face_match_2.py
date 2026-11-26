import face_recognition
import cv2
import requests
from datetime import datetime
import os

CAMERA_INDEX = 0
TOLERANCE = 0.45
FRAME_SCALE = 0.25
ALERT_COOLDOWN = 15
BACKEND_URL = "http://localhost:5000"

def load_encodings(folder="known_faces"):
    encodings = []
    names = []
    for file in os.listdir(folder):
        if file.lower().endswith((".jpg", ".png")):
            img = face_recognition.load_image_file(os.path.join(folder, file))
            face_enc = face_recognition.face_encodings(img)
            if face_enc:
                encodings.append(face_enc[0])
                names.append(os.path.splitext(file)[0])
    return {"encodings": encodings, "names": names}

data = load_encodings()

def send_alert(name):
    try:
        normalized_name = name.replace("_", " ").title()
        print(f"[DEBUG] Sending alert for: {normalized_name}")
        response = requests.get(f"{BACKEND_URL}/get_criminal_id", params={"name": normalized_name})
        print(f"[DEBUG] Response: {response.status_code}, {response.text}")

        if response.status_code != 200:
            print(f"[ERROR] Could not fetch criminal_id for {normalized_name}")
            return

        criminal_id = response.json().get("criminal_id")
        if not criminal_id:
            print("[ERROR] No criminal_id in response")
            return

        requests.post(f"{BACKEND_URL}/receive_log", json={
            "criminal_id": criminal_id,
            "location": "Camera A"
        })
        print(f"[ALERT SENT] {normalized_name}")

    except Exception as e:
        print(f"[ERROR] {e}")

cap = cv2.VideoCapture(CAMERA_INDEX)
recent_alerts = {}

while True:
    ret, frame = cap.read()
    rgb = cv2.cvtColor(cv2.resize(frame, (0,0), fx=FRAME_SCALE, fy=FRAME_SCALE), cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, locations)
    names = []

    for encoding, loc in zip(encodings, locations):
        matches = face_recognition.compare_faces(data["encodings"], encoding, tolerance=TOLERANCE)
        name = "Unknown"
        if True in matches:
            matched_idx = matches.index(True)
            name = data["names"][matched_idx]

        if name != "Unknown":
            now = datetime.now()
            if name not in recent_alerts or (now - recent_alerts[name]).seconds > ALERT_COOLDOWN:
                send_alert(name)
                recent_alerts[name] = now

        names.append(name)

    for ((top, right, bottom, left), name) in zip(locations, names):
        top, right, bottom, left = (int(v / FRAME_SCALE) for v in (top, right, bottom, left))
        cv2.rectangle(frame, (left,top), (right, bottom), (0,255,0), 2)
        cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    cv2.imshow("Face Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
