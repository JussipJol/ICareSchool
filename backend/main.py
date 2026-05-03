import os
import random
import string
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

import models, schemas, database, auth

from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

app = FastAPI(title="ICareSchool API")

# Mount parent directory for static files (frontend)
import pathlib
parent_dir = pathlib.Path(__file__).parent.parent.absolute()
app.mount("/app", StaticFiles(directory=str(parent_dir), html=True), name="static")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database and seed if empty
models.Base.metadata.create_all(bind=database.engine)

def generate_short_id():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    random_str = "".join(random.choice(chars) for _ in range(4))
    return f"CARE-{random_str}"

@app.on_event("startup")
def seed_database():
    with database.engine.connect() as conn:
        new_cols = [
            ("decision_type", "TEXT"),
            ("referred_to", "TEXT"),
            ("decision_grounds", "TEXT"),
            ("decision_evidence", "TEXT"),
        ]
        for col, col_type in new_cols:
            try:
                conn.execute(text(f"ALTER TABLE complaints ADD COLUMN {col} {col_type}"))
                conn.commit()
            except Exception:
                pass

    db = database.SessionLocal()
    # Check admin
    if not db.query(models.AdminUser).first():
        admin = models.AdminUser(
            username="admin", 
            hashed_password=auth.get_password_hash("admin123")
        )
        db.add(admin)
        db.commit()

    # Check regions
    if not db.query(models.Region).first():
        regions = ["г. Астана", "г. Алматы", "Акмолинская область"]
        for r_name in regions:
            db.add(models.Region(name=r_name))
        db.commit()

        # Add cities
        astana = db.query(models.Region).filter_by(name="г. Астана").first()
        almaty = db.query(models.Region).filter_by(name="г. Алматы").first()
        
        cities_astana = ["Район Есиль", "Район Алматы"]
        for c in cities_astana:
            db.add(models.City(name=c, region_id=astana.id))
            
        cities_almaty = ["Алмалинский район", "Бостандыкский район"]
        for c in cities_almaty:
            db.add(models.City(name=c, region_id=almaty.id))
        db.commit()

        # Add schools
        esil = db.query(models.City).filter_by(name="Район Есиль").first()
        db.add(models.School(name="Школа-лицей №1", city_id=esil.id, slug="school-lyceum-1"))
        db.add(models.School(name="Школа-гимназия №3", city_id=esil.id, slug="school-gymnasium-3"))
        
        almalinsky = db.query(models.City).filter_by(name="Алмалинский район").first()
        db.add(models.School(name="Гимназия №15", city_id=almalinsky.id, slug="gymnasium-15"))
        
        db.commit()
    db.close()


# --- PUBLIC ENDPOINTS ---

@app.get("/api/locations")
def get_locations(db: Session = Depends(database.get_db)):
    regions = db.query(models.Region).all()
    cities = db.query(models.City).all()
    schools = db.query(models.School).all()
    return {
        "regions": [schemas.Region.model_validate(r) for r in regions],
        "cities": [schemas.City.model_validate(c) for c in cities],
        "schools": [schemas.School.model_validate(s) for s in schools]
    }

@app.post("/api/complaints", response_model=schemas.ComplaintResponse)
def create_complaint(
    region_id: int = Form(...),
    city_id: int = Form(...),
    school_id: int = Form(...),
    category: str = Form(...),
    target_person: str = Form(""),
    description: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(database.get_db)
):
    short_id = generate_short_id()
    while db.query(models.Complaint).filter(models.Complaint.short_id == short_id).first():
        short_id = generate_short_id()
        
    attachment_url = None
    if file:
        os.makedirs("../uploads", exist_ok=True)
        file_path = f"../uploads/{short_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        attachment_url = file_path

    urgency = 3 if category in ["Коррупция", "Превышение должностных полномочий"] else 1

    db_complaint = models.Complaint(
        short_id=short_id,
        region_id=region_id,
        city_id=city_id,
        school_id=school_id,
        category=category,
        target_person=target_person,
        description=description,
        attachment_url=attachment_url,
        urgency=urgency
    )
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    
    return {"short_id": db_complaint.short_id}

@app.get("/api/complaints/status/{short_id}", response_model=schemas.ComplaintStatus)
def check_complaint_status(short_id: str, db: Session = Depends(database.get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.short_id == short_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    return complaint


# --- ADMIN ENDPOINTS ---

@app.post("/api/admin/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.AdminUser).filter(models.AdminUser.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/admin/complaints", response_model=List[schemas.ComplaintAdminDetail])
def read_all_complaints(db: Session = Depends(database.get_db), current_user: models.AdminUser = Depends(auth.get_current_admin)):
    complaints = db.query(models.Complaint).order_by(models.Complaint.created_at.desc()).all()
    return complaints

@app.put("/api/admin/complaints/{complaint_id}")
def update_complaint_status(
    complaint_id: str, 
    update_data: schemas.AdminResponseUpdate,
    db: Session = Depends(database.get_db), 
    current_user: models.AdminUser = Depends(auth.get_current_admin)
):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = update_data.status
    if update_data.admin_response is not None:
        complaint.admin_response = update_data.admin_response
    if update_data.decision_type is not None:
        complaint.decision_type = update_data.decision_type
    if update_data.referred_to is not None:
        complaint.referred_to = update_data.referred_to
    if update_data.decision_grounds is not None:
        complaint.decision_grounds = update_data.decision_grounds
    if update_data.decision_evidence is not None:
        complaint.decision_evidence = update_data.decision_evidence

    db.commit()
    return {"message": "Updated successfully"}
