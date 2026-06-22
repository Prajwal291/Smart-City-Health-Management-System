from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import User, Hospital, SOSAlert

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")

def get_admin(request: Request):
    if request.session.get("role") != "admin":
        return None
    return request.session.get("user_id")

@router.get("/", response_class=HTMLResponse)
def read_admin_dashboard(request: Request, db: Session = Depends(get_db)):
    if not get_admin(request):
        return RedirectResponse(url="/", status_code=303)
    
    stats = {
        "hospitals": db.query(Hospital).count(),
        "users": db.query(User).count(),
        "alerts": db.query(SOSAlert).filter(SOSAlert.status == "Active").count()
    }
    recent_alerts = db.query(SOSAlert).order_by(SOSAlert.timestamp.desc()).limit(5).all()
    
    return templates.TemplateResponse(request=request, name="admin_dashboard.html", context={
        "stats": stats,
        "recent_alerts": recent_alerts
    })

@router.get("/hospitals", response_class=HTMLResponse)
def list_hospitals(request: Request, db: Session = Depends(get_db)):
    if not get_admin(request):
        return RedirectResponse(url="/", status_code=303)
    
    hospitals = db.query(Hospital).all()
    return templates.TemplateResponse(request=request, name="admin_hospitals.html", context={
        "hospitals": hospitals
    })

@router.post("/hospitals/add")
def add_hospital(request: Request, name: str = Form(...), email: str = Form(...), 
                 password: str = Form(...), phone: str = Form(...), address: str = Form(...), 
                 db: Session = Depends(get_db)):
    if not get_admin(request):
        return RedirectResponse(url="/", status_code=303)
    
    new_hospital = Hospital(
        name=name,
        email=email,
        password=password,
        phone=phone,
        address=address,
        role="hospital"
    )
    db.add(new_hospital)
    db.commit()
    return RedirectResponse(url="/admin/hospitals", status_code=303)

@router.get("/hospitals/delete/{hospital_id}")
def delete_hospital(request: Request, hospital_id: int, db: Session = Depends(get_db)):
    if not get_admin(request):
        return RedirectResponse(url="/", status_code=303)
    
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if hospital:
        db.delete(hospital)
        db.commit()
    return RedirectResponse(url="/admin/hospitals", status_code=303)

@router.get("/users", response_class=HTMLResponse)
def list_users(request: Request, db: Session = Depends(get_db)):
    if not get_admin(request):
        return RedirectResponse(url="/", status_code=303)
    
    users = db.query(User).filter(User.role == "user").all()
    return templates.TemplateResponse(request=request, name="admin_users.html", context={
        "users": users
    })

@router.get("/users/delete/{user_id}")
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    if not get_admin(request):
        return RedirectResponse(url="/", status_code=303)
    
    user = db.query(User).filter(User.id == user_id, User.role == "user").first()
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)
