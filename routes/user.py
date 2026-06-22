from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import User, Hospital, Doctor, Appointment, SOSAlert, Patient, Notification, Bed
import datetime

router = APIRouter(prefix="/user", tags=["User"])
templates = Jinja2Templates(directory="templates")

def get_user_id(request: Request):
    if request.session.get("role") != "user":
        return None
    return request.session.get("user_id")

@router.get("/", response_class=HTMLResponse)
def read_user_dashboard(request: Request, db: Session = Depends(get_db)):
    u_id = get_user_id(request)
    if not u_id:
        return RedirectResponse(url="/", status_code=303)
    
    user = db.query(User).filter(User.id == u_id).first()
    # Find patient record matching user name (simplification)
    patient = db.query(Patient).filter(Patient.name == user.name).first()
    
    appointments = []
    if patient:
        appointments = db.query(Appointment).filter(Appointment.patient_id == patient.id).order_by(Appointment.id.desc()).limit(5).all()
    
    active_alerts = db.query(SOSAlert).filter(SOSAlert.user_id == u_id, SOSAlert.status == "Active").count()
    
    return templates.TemplateResponse(request=request, name="user_dashboard.html", context={
        "user": user,
        "appointments": appointments,
        "active_alerts": active_alerts
    })

@router.post("/sos")
def trigger_sos(request: Request, latitude: float = Form(...), longitude: float = Form(...), db: Session = Depends(get_db)):
    u_id = get_user_id(request)
    if not u_id: return RedirectResponse(url="/", status_code=303)
    
    new_alert = SOSAlert(user_id=u_id, latitude=latitude, longitude=longitude, status="Active")
    db.add(new_alert)
    db.commit()
    return RedirectResponse(url="/user/", status_code=303)

@router.get("/hospitals", response_class=HTMLResponse)
def browse_hospitals(request: Request, db: Session = Depends(get_db)):
    u_id = get_user_id(request)
    if not u_id: return RedirectResponse(url="/", status_code=303)
    
    hospitals = db.query(Hospital).all()
    return templates.TemplateResponse(request=request, name="user_hospitals.html", context={"hospitals": hospitals})

@router.get("/book/{hospital_id}", response_class=HTMLResponse)
def book_form(request: Request, hospital_id: int, db: Session = Depends(get_db)):
    u_id = get_user_id(request)
    if not u_id: return RedirectResponse(url="/", status_code=303)
    
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    doctors = db.query(Doctor).filter(Doctor.hospital_id == hospital_id).all()
    return templates.TemplateResponse(request=request, name="user_book.html", context={"hospital": hospital, "doctors": doctors})

@router.post("/book")
def book_appointment(request: Request, hospital_id: int = Form(...), doctor_id: int = Form(...), 
                     date: str = Form(...), time: str = Form(...), db: Session = Depends(get_db)):
    u_id = get_user_id(request)
    if not u_id: return RedirectResponse(url="/", status_code=303)
    
    user = db.query(User).filter(User.id == u_id).first()
    # Check if patient record exists for this user at this hospital
    patient = db.query(Patient).filter(Patient.name == user.name, Patient.hospital_id == hospital_id).first()
    
    if not patient:
        # Create a temporary patient record for booking if not exists
        patient = Patient(name=user.name, hospital_id=hospital_id, age=0, gender="Unknown", phone="", address="")
        db.add(patient)
        db.commit()
        db.refresh(patient)
    
    new_appt = Appointment(hospital_id=hospital_id, doctor_id=doctor_id, patient_id=patient.id, date=date, time=time, status="Pending")
    db.add(new_appt)
    db.commit()
    return RedirectResponse(url="/user/appointments", status_code=303)

@router.get("/appointments", response_class=HTMLResponse)
def my_appointments(request: Request, db: Session = Depends(get_db)):
    u_id = get_user_id(request)
    if not u_id: return RedirectResponse(url="/", status_code=303)
    
    user = db.query(User).filter(User.id == u_id).first()
    # Find all patient records associated with this name across hospitals
    patient_ids = [p.id for p in db.query(Patient).filter(Patient.name == user.name).all()]
    appointments = db.query(Appointment).filter(Appointment.patient_id.in_(patient_ids)).order_by(Appointment.id.desc()).all()
    
    return templates.TemplateResponse(request=request, name="user_appointments.html", context={"appointments": appointments})

@router.get("/notifications", response_class=HTMLResponse)
def list_notifications(request: Request, db: Session = Depends(get_db)):
    u_id = get_user_id(request)
    if not u_id: return RedirectResponse(url="/", status_code=303)
    
    notifications = db.query(Notification).filter(Notification.user_id == u_id).order_by(Notification.timestamp.desc()).all()
    # Mark as read
    db.query(Notification).filter(Notification.user_id == u_id).update({Notification.is_read: 1})
    db.commit()
    
    return templates.TemplateResponse(request=request, name="user_notifications.html", context={"notifications": notifications})

@router.get("/doctors", response_class=HTMLResponse)
def search_doctors(request: Request, query: str = None, db: Session = Depends(get_db)):
    u_id = get_user_id(request)
    if not u_id: return RedirectResponse(url="/", status_code=303)
    
    doctors_query = db.query(Doctor)
    if query:
        doctors_query = doctors_query.filter(Doctor.name.contains(query) | Doctor.specialization.contains(query))
    doctors = doctors_query.all()
    
    return templates.TemplateResponse(request=request, name="user_doctors.html", context={"doctors": doctors, "query": query})

@router.get("/beds", response_class=HTMLResponse)
def view_beds(request: Request, db: Session = Depends(get_db)):
    u_id = get_user_id(request)
    if not u_id: return RedirectResponse(url="/", status_code=303)
    
    beds = db.query(Bed).filter(Bed.status == "Available").all()
    return templates.TemplateResponse(request=request, name="user_beds.html", context={"beds": beds})
