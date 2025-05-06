#models
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base
from pydantic import BaseModel, Field
from typing import List, Optional
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class ResumeData(BaseModel):
    name: str
    email: str
    phone: str
    skills: List[str]
    education: List[dict] = Field(..., alias="Education")
    experience: List[dict]
    projects: List[dict]
    certifications: List[str] = Field(..., alias="Certifications")
    achievements: List[str] = Field(..., alias="Achievements")
    hobbies: Optional[str] = None