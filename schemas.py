from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True

# --- Hospital Schemas ---
class HospitalBase(BaseModel):
    name: str
    address: str
    email: str
    phone: str
    logo: Optional[str] = None

class HospitalCreate(HospitalBase):
    password: str

class Hospital(HospitalBase):
    id: int
    role: str

    class Config:
        orm_mode = True

# --- Doctor Schemas ---
class DoctorBase(BaseModel):
    name: str
    specialization: str
    email: str
    phone: str

class DoctorCreate(DoctorBase):
    hospital_id: int

class Doctor(DoctorBase):
    id: int
    hospital_id: int

    class Config:
        orm_mode = True

# --- Patient Schemas ---
class PatientBase(BaseModel):
    name: str
    age: int
    gender: str
    phone: str
    address: str

class PatientCreate(PatientBase):
    hospital_id: int

class Patient(PatientBase):
    id: int
    hospital_id: int

    class Config:
        orm_mode = True

# --- Appointment Schemas ---
class AppointmentBase(BaseModel):
    date: str
    time: str
    status: Optional[str] = "Pending"

class AppointmentCreate(AppointmentBase):
    hospital_id: int
    doctor_id: int
    patient_id: int

class Appointment(AppointmentBase):
    id: int
    hospital_id: int
    doctor_id: int
    patient_id: int

    class Config:
        orm_mode = True

# --- Bed Schemas ---
class BedBase(BaseModel):
    ward: str
    bed_number: str
    category: str
    status: Optional[str] = "Available"

class BedCreate(BedBase):
    hospital_id: int

class Bed(BedBase):
    id: int
    hospital_id: int
    patient_id: Optional[int] = None

    class Config:
        orm_mode = True

# --- SOSAlert Schemas ---
class SOSAlertBase(BaseModel):
    latitude: float
    longitude: float

class SOSAlertCreate(SOSAlertBase):
    user_id: int

class SOSAlert(SOSAlertBase):
    id: int
    user_id: int
    status: str
    timestamp: datetime

    class Config:
        orm_mode = True

# --- Notification Schemas ---
class NotificationBase(BaseModel):
    title: str
    message: str

class NotificationCreate(NotificationBase):
    user_id: int

class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: int
    timestamp: datetime

    class Config:
        orm_mode = True
