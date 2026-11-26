from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session
import uuid
from werkzeug.utils import secure_filename
import mysql.connector
import os
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', default='dev-secret')

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'criminal_detection_db')
    )

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['user'] = user['username']
            session['name'] = user['name']
            return redirect(url_for('home'))
        else:
            error = "Invalid credentials"
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', name=session.get('name'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add_criminal', methods=['GET', 'POST'])
def add_criminal():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('add_criminal.html')

    name = request.form['name']
    age = request.form.get('age', type=int)
    criminal_type = request.form['criminalType']
    last_seen = request.form['lastSeen']
    image = request.files['image']

    if image:
        filename = secure_filename(image.filename)

        # Save to uploads folder (for web display)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(upload_path)

        # Save a copy to known_faces folder (for face recognition)
        known_faces_path = os.path.join("known_faces", filename)
        image.seek(0)  # Reset file pointer to beginning
        with open(known_faces_path, 'wb') as f:
            f.write(image.read())

        # Save criminal record to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO criminals (name, age, criminal_type, last_seen, image_path)
            VALUES (%s, %s, %s, %s, %s)
        ''', (name, age, criminal_type, last_seen, filename))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('add_criminal'))

    return 'Image not uploaded', 400

@app.route('/manage_criminals')
def manage_criminals():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            id, 
            name, 
            age, 
            criminal_type AS criminalType, 
            last_seen AS lastSeen, 
            image_path AS image 
        FROM criminals
    """)
    criminals = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('manage_criminals.html', criminals=criminals)

@app.route('/edit_criminal/<int:criminal_id>', methods=['GET', 'POST'])
def edit_criminal(criminal_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        age = request.form.get('age', type=int)
        criminal_type = request.form['criminalType']
        last_seen = request.form['lastSeen']
        image = request.form['image']

        cursor.execute("""
            UPDATE criminals 
            SET name = %s, age = %s, criminal_type = %s, last_seen = %s, image_path = %s 
            WHERE id = %s
        """, (name, age, criminal_type, last_seen, image, criminal_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('manage_criminals'))

    cursor.execute("SELECT * FROM criminals WHERE id = %s", (criminal_id,))
    criminal = cursor.fetchone()
    cursor.close()
    conn.close()

    if not criminal:
        return "Criminal not found", 404

    return render_template('edit_criminal.html', criminal=criminal)

@app.route('/remove_criminal/<int:criminal_id>', methods=['POST'])
def remove_criminal(criminal_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Get image path before deletion
    cur.execute("SELECT image_path FROM criminals WHERE id = %s", (criminal_id,))
    result = cur.fetchone()

    # Delete the criminal from the database
    cur.execute("DELETE FROM criminals WHERE id = %s", (criminal_id,))
    conn.commit()
    cur.close()
    conn.close()

    if result and result[0]:
        image_filename = os.path.basename(os.path.normpath(result[0]))

        uploads_path = os.path.join(app.root_path, 'static', 'uploads', image_filename)
        known_faces_path = os.path.join(app.root_path, 'known_faces', image_filename)

        try:
            if os.path.exists(uploads_path):
                os.remove(uploads_path)
            if os.path.exists(known_faces_path):
                os.remove(known_faces_path)
        except Exception as e:
            print(f"Error deleting image files: {e}")

    return redirect(url_for('manage_criminals'))

@app.route('/recent_alerts')
def recent_alerts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            c.name, 
            a.location, 
            DATE_FORMAT(a.timestamp, '%a, %d %b %Y %H:%i:%s GMT') AS time,
            'Notified Authorities' AS action
        FROM alerts a
        JOIN criminals c ON a.criminal_id = c.id
        ORDER BY a.timestamp DESC
    """)
    alerts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('recent_alerts.html', alerts=alerts)

@app.route('/creators')
def creators():
    return render_template('creators.html')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- USER MANAGEMENT ROUTES ---
@app.route('/manage_users')
def manage_users():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, username, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('manage_users.html', users=users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        role = request.form['role']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return render_template('add_user.html', error="Username already exists.")

        cursor.execute("""
            INSERT INTO users (name, username, password, role)
            VALUES (%s, %s, %s, %s)
        """, (name, username, "password", role))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('manage_users'))

    return render_template('add_user.html')

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s AND role != 'admin'", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('manage_users'))

# --- RECEIVE LOG FROM DEVICE ---
@app.route('/receive_log', methods=['POST'])
def receive_log():
    try:
        data = request.get_json()
        print("Received alert log from Device A:", data)

        if not data:
            return jsonify({'error': 'Invalid or missing JSON data'}), 400

        if 'criminal_id' not in data or 'location' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (criminal_id, location, timestamp)
            VALUES (%s, %s, NOW())
        """, (data['criminal_id'], data['location']))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'status': 'received'}), 200

    except Exception as e:
        print("Error receiving log:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/get_criminal_id')
def get_criminal_id():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Missing name"}), 400

    name = name.strip().lower()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM criminals WHERE LOWER(name) = %s", (name,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return jsonify({"criminal_id": result[0]})
    else:
        return jsonify({"error": "Criminal not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
