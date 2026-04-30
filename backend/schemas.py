from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RegionBase(BaseModel):
    name: str

class Region(RegionBase):
    id: int
    class Config:
        from_attributes = True

class CityBase(BaseModel):
    name: str
    region_id: int

class City(CityBase):
    id: int
    class Config:
        from_attributes = True

class SchoolBase(BaseModel):
    name: str
    city_id: int
    slug: str

class School(SchoolBase):
    id: int
    class Config:
        from_attributes = True

class ComplaintCreate(BaseModel):
    region_id: int
    city_id: int
    school_id: int
    category: str
    target_person: str
    description: str

class ComplaintResponse(BaseModel):
    short_id: str

class ComplaintStatus(BaseModel):
    short_id: str
    category: str
    status: str
    admin_response: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ComplaintAdminDetail(BaseModel):
    id: str
    short_id: str
    category: str
    target_person: Optional[str]
    description: str
    attachment_url: Optional[str]
    status: str
    urgency: int
    admin_response: Optional[str]
    created_at: datetime
    
    # Nested info
    region: Region
    city: City
    school: School

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class AdminResponseUpdate(BaseModel):
    status: str
    admin_response: str
