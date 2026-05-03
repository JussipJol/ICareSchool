import uuid
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cities = relationship("City", back_populates="region")

class City(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    name = Column(String, nullable=False)
    region = relationship("Region", back_populates="cities")
    schools = relationship("School", back_populates="city")

class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False) # e.g. school-42
    city = relationship("City", back_populates="schools")
    complaints = relationship("Complaint", back_populates="school")

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(String, primary_key=True, default=generate_uuid)
    short_id = Column(String, unique=True, index=True, nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"))
    city_id = Column(Integer, ForeignKey("cities.id"))
    school_id = Column(Integer, ForeignKey("schools.id"))
    
    category = Column(String, nullable=False)
    target_person = Column(String)
    description = Column(Text, nullable=False)
    attachment_url = Column(String)
    
    status = Column(String, default="Принято")  # Принято, На рассмотрении, Направлено по компетентности, Завершено
    urgency = Column(Integer, default=1)
    admin_response = Column(Text, nullable=True)

    decision_type = Column(String, nullable=True)    # territorial | law_enforcement | no_action
    referred_to = Column(String, nullable=True)
    decision_grounds = Column(Text, nullable=True)
    decision_evidence = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    school = relationship("School", back_populates="complaints")
    region = relationship("Region")
    city = relationship("City")

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
