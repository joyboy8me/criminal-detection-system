# AI Criminal Detection & Alert System

An intelligent web application that detects and identifies criminals in real-time or from static uploads using facial recognition technology. Built with Python, Flask, and OpenCV.

## Features
- **Facial Recognition:** Extracts face encodings and matches suspected faces using `encode_faces.py` and `face_match.py`.
- **Criminal Management:** Add, edit, and view records of criminals including their personal details and photos.
- **User Management:** Secure access to the system for admins and authorized personnel.
- **Alert System:** Tracks and logs when a criminal is detected (`alert_log.csv` and `alerts` view).
- **Web Dashboard:** Interactive frontend built with HTML/CSS, integrated via Flask.

## Project Structure
- `app.py`: Main Flask application handling routing and backend logic.
- `encode_faces.py` / `encode_faces_2.py`: Scripts to process images and generate facial encodings.
- `face_match.py` / `face_match_2.py`: Scripts to compare input faces against the database of known criminals.
- `Templates/`: HTML templates for the frontend (Home, Login, Manage Criminals, Alerts, etc.).
- `Static/`: CSS styles, images, and uploaded files.
- `Database/MainProject.sql`: MySQL database schema and initial dump.
- `known_faces/`: Directory storing facial images of criminals for recognition.
- `requirements.txt`: Python dependencies required to run the project.

## Prerequisites
- Python 3.8+
- MySQL Server
- C++ Build Tools (required for installing some facial recognition dependencies)

## Setup & Installation

**1. Clone or Download the project**
Navigate into the project directory in your terminal.

**2. Setup the Database**
- Create a MySQL database (e.g., `criminal_detection_db`).
- Import `Database/MainProject.sql` into your MySQL server to set up the necessary tables (users, criminals, alerts).
- Update the database credentials (`user`, `password`, `database`) in `app.py` as needed.

**3. Install Python Dependencies**
It is recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**4. Run the Application**
Start the main Flask application:
```bash
python app.py
```
The web app should now be running at `http://127.0.0.1:5000`.

## Face Recognition Usage
To properly detect criminals, you must first encode their faces:

1. Add images of known criminals to the `known_faces/` directory.
2. Run the encoding script to generate the models:
   ```bash
   python encode_faces.py
   ```
3. Run the matching script (or use the web dashboard) to detect matches:
   ```bash
   python face_match.py
   ```

## Notes
- **Security:** Do not upload `.env`, virtual environments (`venv/`), `__pycache__`, or sensitive `known_faces/` directories to public versions control (these are listed in `.gitignore`).
- **Default Login:** Check your `users` table after SQL import for default administrative credentials.
