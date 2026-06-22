from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user") # 'user', 'admin'
    
    alerts = relationship("SOSAlert", back_populates="user")

class Hospital(Base):
    __tablename__ = "hospitals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(Text)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password = Column(String)
    logo = Column(String, nullable=True)
    role = Column(String, default="hospital")
    
    doctors = relationship("Doctor", back_populates="hospital")
    patients = relationship("Patient", back_populates="hospital")
    appointments = relationship("Appointment", back_populates="hospital")
    beds = relationship("Bed", back_populates="hospital")

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    name = Column(String)
    specialization = Column(String)
    email = Column(String)
    phone = Column(String)

    hospital = relationship("Hospital", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    phone = Column(String)
    address = Column(Text)

    hospital = relationship("Hospital", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient")
    beds = relationship("Bed", back_populates="patient")

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    date = Column(String) # YYYY-MM-DD
    time = Column(String) # HH:MM
    status = Column(String, default="Pending")

    hospital = relationship("Hospital", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")

class Bed(Base):
    __tablename__ = "beds"
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    ward = Column(String)
    bed_number = Column(String)
    category = Column(String)
    status = Column(String, default="Available")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)

    hospital = relationship("Hospital", back_populates="beds")
    patient = relationship("Patient", back_populates="beds")

class SOSAlert(Base):
    __tablename__ = "sos_alerts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String, default="Active")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="alerts")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    type = Column(String) # 'info', 'success', 'warning', 'danger'
    is_read = Column(Integer, default=0) # 0 for False, 1 for True
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")

# Update User model to include notifications relationship
User.notifications = relationship("Notification", back_populates="user")
