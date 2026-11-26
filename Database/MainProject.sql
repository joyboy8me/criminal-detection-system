-- Create the database
CREATE DATABASE IF NOT EXISTS criminal_detection_db;
USE criminal_detection_db;

-- Drop tables if they exist (for clean setup — optional in development)
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS criminals;
DROP TABLE IF EXISTS users;

-- Create Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- NOTE: Use hashed passwords in production
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Criminals table
CREATE TABLE IF NOT EXISTS criminals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(10),
    crime_details TEXT,
    criminal_type VARCHAR(100),
    last_seen VARCHAR(255),
    image_path VARCHAR(255), -- Should match actual filename used in known_faces
    added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Alerts table with correct ON DELETE CASCADE
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    criminal_id INT NOT NULL,
    location VARCHAR(100) NOT NULL DEFAULT 'Camera 1',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (criminal_id) REFERENCES criminals(id) ON DELETE CASCADE
);

-- Insert initial users
INSERT INTO users (name, username, password, role) VALUES
('Ravi Kumar', 'ravi_kumar', 'ravi123', 'admin'),
('Anjali Mehta', 'anjali_mehta', 'anjali123', 'user');

-- Insert sample criminals
INSERT INTO criminals (name, age, gender, crime_details, criminal_type, last_seen, image_path) VALUES
('Pratham Maurya', 18, 'Male', 'Robbery and Assault', 'Robbery', 'Gujarat CCTV-21', 'images/Pratham.jpg'),
('Krrish Kumar', 18, 'Male', 'Fraud and Identity Theft', 'Fraud', 'Bihar CCTV-08', 'images/Krrish.jpg'),
('Mishti Gupta', 18, 'Female', 'Drug Trafficking', 'Drug Trafficking', 'Punjab CCTV-14', 'images/Mishti.jpg');

-- Insert sample alerts
INSERT INTO alerts (criminal_id, location, timestamp) VALUES
(1, 'Gujarat CCTV-21', '2025-05-02 19:05:45'),
(2, 'Bihar CCTV-08', '2025-05-02 19:05:45'),
(3, 'Punjab CCTV-14', '2025-05-02 19:05:45');

-- Optional: View contents
SELECT * FROM users;
SELECT * FROM criminals;
SELECT * FROM alerts;
