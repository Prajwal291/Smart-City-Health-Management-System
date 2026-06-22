from database import SessionLocal
from models import User, Hospital

db = SessionLocal()
print("Users:")
for user in db.query(User).all():
    print(f"ID: {user.id}, Email: {user.email}, Password Hash: {user.password}")

print("\nHospitals:")
for hospital in db.query(Hospital).all():
    print(f"ID: {hospital.id}, Email: {hospital.email}, Password Hash: {hospital.password}")

db.close()
