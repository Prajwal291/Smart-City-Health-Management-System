-- =========================================================================
--               Smart City Health Management System (SHMS)
--                     SQL SCHEMA & OPERATIONS GUIDE
-- =========================================================================
-- This file contains all the DDL (Data Definition Language) and DML 
-- (Data Manipulation Language) queries used throughout the SHMS project.
-- These commands are compatible with MySQL and SQLite.

-- =========================================================================
-- 1. DATA DEFINITION LANGUAGE (DDL) - SCHEMA CREATION
-- =========================================================================

-- Drop tables if they exist (to perform a clean reset)
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS sos_alerts;
DROP TABLE IF EXISTS beds;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS hospitals;
DROP TABLE IF EXISTS users;

-- A. Users Table (Admin and Citizens)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user' -- 'user', 'admin'
);

-- B. Hospitals Table
CREATE TABLE hospitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    logo VARCHAR(255),
    role VARCHAR(50) DEFAULT 'hospital'
);

-- C. Doctors Table
CREATE TABLE doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    specialization VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
);

-- D. Patients Table
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(50) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    address TEXT NOT NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
);

-- E. Appointments Table
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    date VARCHAR(50) NOT NULL, -- Format: YYYY-MM-DD
    time VARCHAR(50) NOT NULL, -- Format: HH:MM
    status VARCHAR(50) DEFAULT 'Pending', -- 'Pending', 'Confirmed', 'Cancelled', 'Completed'
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- F. Beds Table
CREATE TABLE beds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id INTEGER NOT NULL,
    ward VARCHAR(100) NOT NULL,
    bed_number VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL, -- 'General', 'ICU', 'Private'
    status VARCHAR(50) DEFAULT 'Available', -- 'Available', 'Occupied'
    patient_id INTEGER,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL
);

-- G. SOS Alerts Table
CREATE TABLE sos_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    status VARCHAR(50) DEFAULT 'Active', -- 'Active', 'Responding', 'Dispatched'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- H. Notifications Table
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'info', 'success', 'warning', 'danger'
    is_read INTEGER DEFAULT 0, -- 0 for False, 1 for True
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- =========================================================================
-- 2. ALTER TABLE OPERATIONS (DDL EXAMPLES)
-- =========================================================================

-- Example: Adding a new column to a table
-- ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Example: Modifying table column types (Standard MySQL syntax)
-- ALTER TABLE users MODIFY COLUMN role VARCHAR(100) DEFAULT 'user';


-- =========================================================================
-- 3. DATA INSERTION OPERATIONS (DML) - DATA SEEDING
-- =========================================================================

-- Add Admin
INSERT INTO users (name, email, password, role) 
VALUES ('SHMS System Admin', 'admin@shms.com', 'admin123', 'admin');

-- Add Tumkur Hospitals
INSERT INTO hospitals (name, email, password, address, phone, role) VALUES 
('City Hospital', 'cityhospital@shms.com', 'city123', 'B.H. Road, Ashok Nagar, Tumkur, Karnataka, India', '+91-816-2278901', 'hospital'),
('Siddhartha Hospital', 'siddhartha@shms.com', 'siddha123', 'Siddhartha Medical College Campus, Heggere, Tumkur, Karnataka, India', '+91-816-2206451', 'hospital'),
('Siddaganga Hospital', 'siddaganga@shms.com', 'sidda123', 'Near Siddaganga Mutt, B.H. Road, Tumkur, Karnataka, India', '+91-816-2282411', 'hospital');

-- Add Tumkur Citizens / Users
INSERT INTO users (name, email, password, role) VALUES 
('Arun Kumar', 'arun@shms.com', 'arun123', 'user'),
('Divya Gowda', 'divya@shms.com', 'divya123', 'user'),
('Prakash Raj', 'prakash@shms.com', 'prakash123', 'user'),
('Sneha Patil', 'sneha@shms.com', 'sneha123', 'user');

-- Add Doctors
INSERT INTO doctors (hospital_id, name, specialization, email, phone) VALUES 
(1, 'Dr. Rajesh Kumar', 'Cardiology', 'doctor.rajesh.kumar@cityhospital.com', '+91-816-555010'),
(1, 'Dr. Amit Deshpande', 'Neurology', 'doctor.amit.deshpande@cityhospital.com', '+91-816-555011'),
(1, 'Dr. Kavitha Reddy', 'Pediatrics', 'doctor.kavitha.reddy@cityhospital.com', '+91-816-555012'),
(2, 'Dr. Sandeep Gowda', 'Cardiology', 'doctor.sandeep.gowda@siddhartha.com', '+91-816-555020'),
(2, 'Dr. Priya Shetty', 'Pediatrics', 'doctor.priya.shetty@siddhartha.com', '+91-816-555021'),
(2, 'Dr. Harish Naik', 'Orthopedics', 'doctor.harish.naik@siddhartha.com', '+91-816-555022'),
(3, 'Dr. Manjunath Swamy', 'Orthopedics', 'doctor.manjunath.swamy@siddaganga.com', '+91-816-555030'),
(3, 'Dr. Deepa Rao', 'General Medicine', 'doctor.deepa.rao@siddaganga.com', '+91-816-555031'),
(3, 'Dr. Vijay Prasad', 'Neurology', 'doctor.vijay.prasad@siddaganga.com', '+91-816-555032');

-- Add Patients
INSERT INTO patients (hospital_id, name, age, gender, phone, address) VALUES 
(1, 'Ramesh Gowda', 45, 'Male', '+91-9845012345', 'Saraswathipuram, Tumkur, Karnataka'),
(1, 'Lata Shastri', 38, 'Female', '+91-9886098765', 'Ashok Nagar, Tumkur, Karnataka'),
(2, 'Anil Kumble', 52, 'Male', '+91-9900112233', 'Kyathsandra, Tumkur, Karnataka'),
(2, 'Sunita Rao', 29, 'Female', '+91-9448054321', 'Someshwarapuram, Tumkur, Karnataka'),
(3, 'Suresh Murthy', 63, 'Male', '+91-9844055667', 'Siddaganga Layout, Tumkur, Karnataka'),
(3, 'Asha Shetty', 31, 'Female', '+91-9108112233', 'B.H. Road, Tumkur, Karnataka');

-- Add Beds
INSERT INTO beds (hospital_id, ward, bed_number, category, status) VALUES 
(1, 'General Ward A', 'TUM-B1-1', 'General', 'Available'),
(1, 'General Ward B', 'TUM-B1-2', 'ICU', 'Available'),
(1, 'General Ward A', 'TUM-B1-3', 'ICU', 'Available'),
(2, 'General Ward A', 'TUM-B2-1', 'General', 'Available'),
(2, 'General Ward B', 'TUM-B2-2', 'ICU', 'Available'),
(3, 'General Ward A', 'TUM-B3-1', 'General', 'Available'),
(3, 'General Ward B', 'TUM-B3-2', 'ICU', 'Available');

-- Add SOS Alerts
INSERT INTO sos_alerts (user_id, latitude, longitude, status) VALUES 
(2, 13.3398, 77.1012, 'Active'),
(3, 13.3442, 77.1121, 'Active'),
(4, 13.3312, 77.0984, 'Responding'),
(5, 13.3485, 77.1065, 'Dispatched');


-- =========================================================================
-- 4. APPLICATION QUERIES & MANIPULATIONS (DQL & DML)
-- =========================================================================

-- A. USER AUTHENTICATION / LOGIN
-- Checks if a User exists and matches password
SELECT id, name, email, role 
FROM users 
WHERE email = 'arun@shms.com' AND password = 'arun123';

-- B. FETCH HOSPITAL DASHBOARD STATS
-- Count total doctors assigned to hospital ID = 1
SELECT COUNT(*) FROM doctors WHERE hospital_id = 1;

-- Count total active patients registered under hospital ID = 1
SELECT COUNT(*) FROM patients WHERE hospital_id = 1;

-- Count pending appointments for hospital ID = 1
SELECT COUNT(*) FROM appointments WHERE hospital_id = 1 AND status = 'Pending';

-- Count available beds in hospital ID = 1
SELECT COUNT(*) FROM beds WHERE hospital_id = 1 AND status = 'Available';

-- C. INNER JOIN READ OPERATION: FETCH RECENT APPOINTMENTS WITH DETAILS
-- Obtains the appointment details alongside the patient and doctor name using JOINs
SELECT 
    a.id AS appointment_id, 
    p.name AS patient_name, 
    d.name AS doctor_name, 
    d.specialization AS doctor_specialization, 
    a.date, 
    a.time, 
    a.status
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN doctors d ON a.doctor_id = d.id
WHERE a.hospital_id = 1
ORDER BY a.id DESC
LIMIT 5;

-- D. INNER JOIN READ OPERATION: FETCH ACTIVE SOS SIGNALS WITH USER DETAILS
-- Obtains live emergency alerts alongside user details
SELECT 
    s.id AS alert_id, 
    u.name AS user_name, 
    s.latitude, 
    s.longitude, 
    s.status, 
    s.timestamp
FROM sos_alerts s
JOIN users u ON s.user_id = u.id
WHERE s.status IN ('Active', 'Responding')
ORDER BY s.timestamp DESC;

-- E. UPDATE SOS STATUS (Responding to emergency)
UPDATE sos_alerts 
SET status = 'Responding' 
WHERE id = 1 AND status = 'Active';

-- F. UPDATE SOS STATUS (Dispatched team)
UPDATE sos_alerts 
SET status = 'Dispatched' 
WHERE id = 1;

-- G. BED ASSIGNMENT OPERATION (Assign bed to patient)
UPDATE beds 
SET patient_id = 1, status = 'Occupied' 
WHERE id = 3;

-- H. BED UNASSIGNMENT OPERATION (Release bed)
UPDATE beds 
SET patient_id = NULL, status = 'Available' 
WHERE id = 3;
