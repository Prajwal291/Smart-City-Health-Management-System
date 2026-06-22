from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db
from models import Hospital, Doctor, Patient, Appointment, Bed, SOSAlert
from datetime import datetime

router = APIRouter(prefix="/hospital", tags=["Hospital"])
templates = Jinja2Templates(directory="templates")

def parse_db_timestamp(ts):
    if not ts:
        return datetime.utcnow()
    if isinstance(ts, str):
        try:
            return datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                return datetime.fromisoformat(ts)
            except Exception:
                return datetime.utcnow()
    return ts

def get_hospital_id(request: Request):
    if request.session.get("role") != "hospital":
        return None
    return request.session.get("user_id")

@router.get("/", response_class=HTMLResponse)
def read_hospital_dashboard(request: Request, db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id:
        return RedirectResponse(url="/", status_code=303)
    
    # Raw SQL Queries for stats
    doctors_count = db.execute(
        text("SELECT COUNT(*) FROM doctors WHERE hospital_id = :h_id"),
        {"h_id": h_id}
    ).scalar()
    
    patients_count = db.execute(
        text("SELECT COUNT(*) FROM patients WHERE hospital_id = :h_id"),
        {"h_id": h_id}
    ).scalar()
    
    appointments_count = db.execute(
        text("SELECT COUNT(*) FROM appointments WHERE hospital_id = :h_id AND status = 'Pending'"),
        {"h_id": h_id}
    ).scalar()
    
    beds_count = db.execute(
        text("SELECT COUNT(*) FROM beds WHERE hospital_id = :h_id AND status = 'Available'"),
        {"h_id": h_id}
    ).scalar()
    
    stats = {
        "doctors": doctors_count,
        "patients": patients_count,
        "appointments": appointments_count,
        "beds": beds_count
    }
    
    # Raw SQL JOIN Query for recent appointments
    recent_appointments = db.execute(
        text("""
            SELECT a.id, p.name AS patient_name, d.name AS doctor_name, d.specialization AS doctor_specialization, a.date, a.time, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.hospital_id = :h_id
            ORDER BY a.id DESC
            LIMIT 5
        """),
        {"h_id": h_id}
    ).fetchall()
    
    # Raw SQL JOIN Query for active SOS alerts
    active_sos_raw = db.execute(
        text("""
            SELECT s.id, u.name AS user_name, s.latitude, s.longitude, s.status, s.timestamp
            FROM sos_alerts s
            JOIN users u ON s.user_id = u.id
            WHERE s.status IN ('Active', 'Responding')
            ORDER BY s.timestamp DESC
            LIMIT 5
        """)
    ).fetchall()
    
    active_sos = []
    for r in active_sos_raw:
        active_sos.append({
            "id": r.id,
            "user_name": r.user_name,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "status": r.status,
            "timestamp": parse_db_timestamp(r.timestamp)
        })
    
    return templates.TemplateResponse(request=request, name="hospital_dashboard.html", context={
        "stats": stats,
        "recent_appointments": recent_appointments,
        "active_sos": active_sos
    })

# Doctor Management
@router.get("/doctors", response_class=HTMLResponse)
def list_doctors(request: Request, db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    doctors = db.query(Doctor).filter(Doctor.hospital_id == h_id).all()
    return templates.TemplateResponse(request=request, name="hospital_doctors.html", context={"doctors": doctors})

@router.post("/doctors/add")
def add_doctor(request: Request, name: str = Form(...), specialization: str = Form(...), 
               email: str = Form(...), phone: str = Form(...), db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    new_doctor = Doctor(hospital_id=h_id, name=name, specialization=specialization, email=email, phone=phone)
    db.add(new_doctor)
    db.commit()
    return RedirectResponse(url="/hospital/doctors", status_code=303)

@router.get("/doctors/delete/{doctor_id}")
def delete_doctor(request: Request, doctor_id: int, db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    
    # Set doctor_id to NULL for any appointments associated with this doctor
    db.execute(
        text("UPDATE appointments SET doctor_id = NULL WHERE doctor_id = :doctor_id"),
        {"doctor_id": doctor_id}
    )
    
    # Delete the doctor
    db.execute(
        text("DELETE FROM doctors WHERE id = :doctor_id AND hospital_id = :h_id"),
        {"doctor_id": doctor_id, "h_id": h_id}
    )
    db.commit()
    return RedirectResponse(url="/hospital/doctors", status_code=303)

# Patient Management
@router.get("/patients", response_class=HTMLResponse)
def list_patients(request: Request, db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    patients = db.query(Patient).filter(Patient.hospital_id == h_id).all()
    return templates.TemplateResponse(request=request, name="hospital_patients.html", context={"patients": patients})

@router.post("/patients/add")
def add_patient(request: Request, name: str = Form(...), age: int = Form(...), 
                gender: str = Form(...), phone: str = Form(...), address: str = Form(...), 
                db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    new_patient = Patient(hospital_id=h_id, name=name, age=age, gender=gender, phone=phone, address=address)
    db.add(new_patient)
    db.commit()
    return RedirectResponse(url="/hospital/patients", status_code=303)

@router.get("/patients/delete/{patient_id}")
def delete_patient(request: Request, patient_id: int, db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.hospital_id == h_id).first()
    if patient:
        db.delete(patient)
        db.commit()
    return RedirectResponse(url="/hospital/patients", status_code=303)

# Appointment Management
@router.get("/appointments", response_class=HTMLResponse)
def list_appointments(request: Request, db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    appointments = db.query(Appointment).filter(Appointment.hospital_id == h_id).all()
    return templates.TemplateResponse(request=request, name="hospital_appointments.html", context={"appointments": appointments})

@router.post("/appointments/update/{appointment_id}")
def update_appointment(request: Request, appointment_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id, Appointment.hospital_id == h_id).first()
    if appointment:
        appointment.status = status
        db.commit()
    return RedirectResponse(url="/hospital/appointments", status_code=303)

# Bed Management
@router.get("/beds", response_class=HTMLResponse)
def list_beds(request: Request, db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    beds = db.query(Bed).filter(Bed.hospital_id == h_id).all()
    patients = db.query(Patient).filter(Patient.hospital_id == h_id).all()
    return templates.TemplateResponse(request=request, name="hospital_beds.html", context={"beds": beds, "patients": patients})

@router.post("/beds/add")
def add_bed(request: Request, ward: str = Form(...), bed_number: str = Form(...), 
            category: str = Form(...), db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    new_bed = Bed(hospital_id=h_id, ward=ward, bed_number=bed_number, category=category)
    db.add(new_bed)
    db.commit()
    return RedirectResponse(url="/hospital/beds", status_code=303)

@router.post("/beds/assign/{bed_id}")
def assign_bed(request: Request, bed_id: int, patient_id: int = Form(...), db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    bed = db.query(Bed).filter(Bed.id == bed_id, Bed.hospital_id == h_id).first()
    if bed:
        if patient_id == 0: # Representing Unassign
            bed.patient_id = None
            bed.status = "Available"
        else:
            bed.patient_id = patient_id
            bed.status = "Occupied"
        db.commit()
    return RedirectResponse(url="/hospital/beds", status_code=303)

@router.get("/sos", response_class=HTMLResponse)
def view_sos_alerts(request: Request, db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    
    active_alerts_raw = db.execute(
        text("""
            SELECT s.id, u.name AS user_name, s.latitude, s.longitude, s.status, s.timestamp
            FROM sos_alerts s
            JOIN users u ON s.user_id = u.id
            WHERE s.status IN ('Active', 'Responding')
            ORDER BY s.timestamp DESC
        """)
    ).fetchall()
    
    dispatched_alerts_raw = db.execute(
        text("""
            SELECT s.id, u.name AS user_name, s.latitude, s.longitude, s.status, s.timestamp
            FROM sos_alerts s
            JOIN users u ON s.user_id = u.id
            WHERE s.status = 'Dispatched'
            ORDER BY s.timestamp DESC
            LIMIT 10
        """)
    ).fetchall()
    
    active_alerts = []
    for r in active_alerts_raw:
        active_alerts.append({
            "id": r.id,
            "user_name": r.user_name,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "status": r.status,
            "timestamp": parse_db_timestamp(r.timestamp)
        })
        
    dispatched_alerts = []
    for r in dispatched_alerts_raw:
        dispatched_alerts.append({
            "id": r.id,
            "user_name": r.user_name,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "status": r.status,
            "timestamp": parse_db_timestamp(r.timestamp)
        })
    
    return templates.TemplateResponse(request=request, name="hospital_sos.html", context={
        "active_alerts": active_alerts,
        "dispatched_alerts": dispatched_alerts
    })

@router.get("/sos/view/{alert_id}")
def view_sos_alert(request: Request, alert_id: int, db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    
    alert = db.execute(
        text("SELECT id, latitude, longitude, status FROM sos_alerts WHERE id = :alert_id"),
        {"alert_id": alert_id}
    ).fetchone()
    
    if alert:
        if alert.status == "Active":
            db.execute(
                text("UPDATE sos_alerts SET status = 'Responding' WHERE id = :alert_id"),
                {"alert_id": alert_id}
            )
            db.commit()
        return RedirectResponse(url=f"https://www.google.com/maps?q={alert.latitude},{alert.longitude}", status_code=303)
    return RedirectResponse(url="/hospital/sos", status_code=303)

@router.get("/sos/dispatch/{alert_id}")
def dispatch_sos_alert(request: Request, alert_id: int, db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    
    db.execute(
        text("UPDATE sos_alerts SET status = 'Dispatched' WHERE id = :alert_id"),
        {"alert_id": alert_id}
    )
    db.commit()
    return RedirectResponse(url="/hospital/sos", status_code=303)

@router.get("/reports", response_class=HTMLResponse)
def view_reports(request: Request, db: Session = Depends(get_db)):
    h_id = get_hospital_id(request)
    if not h_id: return RedirectResponse(url="/", status_code=303)
    
    # Simple report data
    total_appointments = db.query(Appointment).filter(Appointment.hospital_id == h_id).count()
    completed_appointments = db.query(Appointment).filter(Appointment.hospital_id == h_id, Appointment.status == "Completed").count()
    total_doctors = db.query(Doctor).filter(Doctor.hospital_id == h_id).count()
    total_patients = db.query(Patient).filter(Patient.hospital_id == h_id).count()
    
    report_data = {
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "success_rate": round((completed_appointments / total_appointments * 100), 2) if total_appointments > 0 else 0
    }
    
    return templates.TemplateResponse(request=request, name="hospital_reports.html", context={"report": report_data})
