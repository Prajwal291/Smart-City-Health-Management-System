from database import SessionLocal, engine, Base
from models import User, Hospital, Notification, Doctor, Bed, Patient, SOSAlert
import datetime

# Drop all tables first to clean up existing data
Base.metadata.drop_all(bind=engine)
# Recreate all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Add Admin
admin = User(name="SHMS System Admin", email="admin@shms.com", password="admin123", role="admin")
db.add(admin)

# Add Tumkur Hospitals
hospitals_data = [
    {
        "name": "City Hospital", 
        "email": "cityhospital@shms.com", 
        "pass": "city123", 
        "addr": "B.H. Road, Ashok Nagar, Tumkur, Karnataka, India", 
        "phone": "+91-816-2278901"
    },
    {
        "name": "Siddhartha Hospital", 
        "email": "siddhartha@shms.com", 
        "pass": "siddha123", 
        "addr": "Siddhartha Medical College Campus, Heggere, Tumkur, Karnataka, India", 
        "phone": "+91-816-2206451"
    },
    {
        "name": "Siddaganga Hospital", 
        "email": "siddaganga@shms.com", 
        "pass": "sidda123", 
        "addr": "Near Siddaganga Mutt, B.H. Road, Tumkur, Karnataka, India", 
        "phone": "+91-816-2282411"
    }
]

for h in hospitals_data:
    hosp = Hospital(name=h["name"], email=h["email"], password=h["pass"], address=h["addr"], phone=h["phone"], role="hospital")
    db.add(hosp)
db.commit()

# Add Indian Citizens / Users (Tumkur Residents)
users_data = [
    {"name": "Arun Kumar", "email": "arun@shms.com", "pass": "arun123"},
    {"name": "Divya Gowda", "email": "divya@shms.com", "pass": "divya123"},
    {"name": "Prakash Raj", "email": "prakash@shms.com", "pass": "prakash123"},
    {"name": "Sneha Patil", "email": "sneha@shms.com", "pass": "sneha123"}
]

for u in users_data:
    user = User(name=u["name"], email=u["email"], password=u["pass"], role="user")
    db.add(user)
db.commit()

# Retrieve loaded data
hospitals = db.query(Hospital).all()
users = db.query(User).filter(User.role == "user").all()

# Seed Doctors, Patients, Beds for each hospital
specializations = ["Cardiology", "Neurology", "Pediatrics", "Orthopedics", "General Medicine"]

doctor_names = [
    # City Hospital
    ["Dr. Rajesh Kumar", "Dr. Amit Deshpande", "Dr. Kavitha Reddy"],
    # Siddhartha Hospital
    ["Dr. Sandeep Gowda", "Dr. Priya Shetty", "Dr. Harish Naik"],
    # Siddaganga Hospital
    ["Dr. Manjunath Swamy", "Dr. Deepa Rao", "Dr. Vijay Prasad"]
]

patient_names = [
    # City Hospital Patients
    [
        {"name": "Ramesh Gowda", "age": 45, "gender": "Male", "phone": "+91-9845012345", "addr": "Saraswathipuram, Tumkur, Karnataka"},
        {"name": "Lata Shastri", "age": 38, "gender": "Female", "phone": "+91-9886098765", "addr": "Ashok Nagar, Tumkur, Karnataka"}
    ],
    # Siddhartha Hospital Patients
    [
        {"name": "Anil Kumble", "age": 52, "gender": "Male", "phone": "+91-9900112233", "addr": "Kyathsandra, Tumkur, Karnataka"},
        {"name": "Sunita Rao", "age": 29, "gender": "Female", "phone": "+91-9448054321", "addr": "Someshwarapuram, Tumkur, Karnataka"}
    ],
    # Siddaganga Hospital Patients
    [
        {"name": "Suresh Murthy", "age": 63, "gender": "Male", "phone": "+91-9844055667", "addr": "Siddaganga Layout, Tumkur, Karnataka"},
        {"name": "Asha Shetty", "age": 31, "gender": "Female", "phone": "+91-9108112233", "addr": "B.H. Road, Tumkur, Karnataka"}
    ]
]

for idx, hosp in enumerate(hospitals):
    # Add Doctors
    for d_idx, doc_name in enumerate(doctor_names[idx]):
        doc = Doctor(
            hospital_id=hosp.id,
            name=doc_name,
            specialization=specializations[(idx + d_idx) % len(specializations)],
            email=f"doctor.{doc_name.lower().replace(' ', '.').replace('dr.', '')}@{hosp.email.split('@')[1]}",
            phone=f"+91-816-5550{hosp.id}{d_idx}"
        )
        db.add(doc)
    
    # Add Patients
    for pat in patient_names[idx]:
        patient = Patient(
            hospital_id=hosp.id,
            name=pat["name"],
            age=pat["age"],
            gender=pat["gender"],
            phone=pat["phone"],
            address=pat["addr"]
        )
        db.add(patient)
        
    # Add 5 Beds per hospital
    for i in range(5):
        bed = Bed(
            hospital_id=hosp.id,
            ward=f"General Ward {['A', 'B'][i % 2]}",
            bed_number=f"TUM-B{hosp.id}-{i+1}",
            category=["General", "ICU", "ICU", "Private", "General"][i],
            status="Available"
        )
        db.add(bed)

db.commit()

# Add a few default Notifications for our seeded Users
for u in users:
    notes = [
        Notification(user_id=u.id, message=f"Welcome {u.name} to Smart City Health Management System (Tumkur).", type="success"),
        Notification(user_id=u.id, message="Emergency contact list updated with local Tumkur hospital numbers.", type="info")
    ]
    db.add_all(notes)

# Add active emergency SOS alerts located in Tumkur, Karnataka, India
# Tumkur centre is around Lat: 13.3392, Lng: 77.1015
sos_alerts_data = [
    {"user_id": users[0].id, "lat": 13.3398, "lng": 77.1012, "status": "Active"},
    {"user_id": users[1].id, "lat": 13.3442, "lng": 77.1121, "status": "Active"},
    {"user_id": users[2].id, "lat": 13.3312, "lng": 77.0984, "status": "Responding"},
    {"user_id": users[3].id, "lat": 13.3485, "lng": 77.1065, "status": "Dispatched"}
]

for s in sos_alerts_data:
    sos = SOSAlert(user_id=s["user_id"], latitude=s["lat"], longitude=s["lng"], status=s["status"])
    db.add(sos)

db.commit()
db.close()

print("Database completely reset and seeded with Tumkur, Karnataka data successfully.")

