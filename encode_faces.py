import os
import face_recognition
import pickle

# -------------------------------
# CONFIGURATION
# -------------------------------
KNOWN_FACES_DIR = "known_faces"
ENCODINGS_FILE = "encodings.pickle"
SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png")

# -------------------------------
# STORAGE
# -------------------------------
known_encodings = []
known_names = []

# -------------------------------
# ENCODING FUNCTION
# -------------------------------
def encode_known_faces():
    print(f"[INFO] Scanning directory: {KNOWN_FACES_DIR}")

    for filename in os.listdir(KNOWN_FACES_DIR):
        if not filename.lower().endswith(SUPPORTED_FORMATS):
            print(f"[SKIPPED] {filename} is not a supported image file.")
            continue

        name = os.path.splitext(filename)[0]
        image_path = os.path.join(KNOWN_FACES_DIR, filename)

        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(name)
                print(f"[ENCODED] {name} from {filename}")
            else:
                print(f"[WARNING] No faces found in {filename}")

        except Exception as e:
            print(f"[ERROR] Failed to process {filename}: {e}")

    # Save to pickle
    if known_encodings:
        data = {"encodings": known_encodings, "names": known_names}
        with open(ENCODINGS_FILE, "wb") as f:
            pickle.dump(data, f)
        print(f"[SUCCESS] Saved {len(known_encodings)} encodings to '{ENCODINGS_FILE}'")
    else:
        print("[INFO] No valid face encodings found. Nothing saved.")

# -------------------------------
# EXECUTE
# -------------------------------
if __name__ == "__main__":
    encode_known_faces()
