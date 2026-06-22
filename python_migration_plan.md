# Implementation Plan - Python Migration of SHMS

This plan outlines the migration of the Smart City Health Management System (SHMS) from PHP to Python.

## Architecture Overview
- **Backend**: FastAPI (Python 3.10+)
- **Database**: SQLAlchemy (SQLite for easy setup, compatible with MySQL)
- **Frontend**: Modern HTML5, CSS3 (Vanilla), and JavaScript.
- **Authentication**: JWT-based or Session-based (we'll use Session for simplicity matching the current PHP logic).

## Database Schema (SQLAlchemy Models)
We will replicate the current schema in Python:
- `User`: id, name, email, password, role ('user', 'admin')
- `Hospital`: id, name, address, email, phone, password, logo, role ('hospital')
- `Doctor`: id, hospital_id, name, specialization, email, phone
- `Patient`: id, hospital_id, name, age, gender, phone, address
- `Appointment`: id, hospital_id, doctor_id, patient_id, date, time, status
- `Bed`: id, hospital_id, ward, bed_number, category, status, patient_id
- `SOSAlert`: id, user_id, latitude, longitude, status, timestamp

## Proposed Structure
```
/python_shms
├── main.py              # Entry point and FastAPI app
├── models.py            # SQLAlchemy Database models
├── database.py          # Database connection setup
├── schemas.py           # Pydantic schemas for validation
├── auth.py              # Authentication logic (login/logout/session)
├── routes/
│   ├── admin.py         # Admin-specific routes
│   ├── hospital.py      # Hospital management routes
│   └── user.py          # User/Patient routes
├── static/              # CSS, JS, Images
└── templates/           # HTML Jinja2 templates
```

### [NEW] [Frontend Components]
- Create a unified dashboard template with a premium look (Glassmorphism, Poppins font, FontAwesome).
- Responsive sidebars and stat cards.

## Verification Plan
- Run the app using `uvicorn main:app --reload` and verify functionality in the browser.
