from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import User, Hospital, Doctor, Patient, Appointment, Bed, SOSAlert, Notification

from routes import admin, hospital, user

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SHMS Python")

# Session middleware (a secret key would typically be in an environment variable)
app.add_middleware(SessionMiddleware, secret_key="super-secret-shms-key")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include Routers
app.include_router(admin.router)
app.include_router(hospital.router)
app.include_router(user.router)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse(request=request, name="about.html")

@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Check for basic login constraints
    if len(password) < 6:
        return templates.TemplateResponse(request=request, name="index.html", context={"error": "Invalid email or password"})

    # Check for User
    db_user = db.query(User).filter(User.email == email).first()
    if db_user and db_user.password == password:
        request.session["user_id"] = db_user.id
        request.session["role"] = db_user.role
        
        if db_user.role == "admin":
            return RedirectResponse(url="/admin/", status_code=303)
        return RedirectResponse(url="/user/", status_code=303)
    
    # Check for Hospital
    db_hospital = db.query(Hospital).filter(Hospital.email == email).first()
    if db_hospital and db_hospital.password == password:
        request.session["user_id"] = db_hospital.id
        request.session["role"] = db_hospital.role
        return RedirectResponse(url="/hospital/", status_code=303)
    
    return templates.TemplateResponse(request=request, name="index.html", context={"error": "Invalid email or password"})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.post("/register")
def register(
    request: Request, 
    name: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...), 
    confirm_password: str = Form(...), 
    db: Session = Depends(get_db)
):
    # Server-side constraints validation
    import re
    
    if len(name.strip()) < 3:
        return templates.TemplateResponse(request=request, name="register.html", context={"error": "Full Name must be at least 3 characters long"})
        
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return templates.TemplateResponse(request=request, name="register.html", context={"error": "Invalid email address format"})

    # Check password constraints (minimum length 6 and complex rules)
    if len(password) < 6:
        return templates.TemplateResponse(request=request, name="register.html", context={"error": "Password must be at least 6 characters long"})
        
    if not any(c.isupper() for c in password):
        return templates.TemplateResponse(request=request, name="register.html", context={"error": "Password must contain at least one uppercase letter"})
        
    if not any(c.islower() for c in password):
        return templates.TemplateResponse(request=request, name="register.html", context={"error": "Password must contain at least one lowercase letter"})
        
    if not any(c.isdigit() for c in password):
        return templates.TemplateResponse(request=request, name="register.html", context={"error": "Password must contain at least one number"})

    if password != confirm_password:
        return templates.TemplateResponse(request=request, name="register.html", context={"error": "Passwords do not match"})

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(request=request, name="register.html", context={"error": "Email already registered"})
    
    # Create new user
    new_user = User(
        name=name.strip(),
        email=email.strip().lower(),
        password=password,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Auto-login after registration
    request.session["user_id"] = new_user.id
    request.session["role"] = new_user.role
    return RedirectResponse(url="/user/", status_code=303)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")
