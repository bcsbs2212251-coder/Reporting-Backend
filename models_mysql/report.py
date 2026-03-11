from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import enum

from utils.mysql_db import Base

class ReportStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    under_review = "under_review"

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_name = Column(String(255), nullable=False)
    project_name = Column(String(500), nullable=False)
    project_code = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.pending)
    attachments = Column(JSON, default=list)
    voice_notes = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Pydantic models for API
class ReportBase(BaseModel):
    project_name: str
    project_code: Optional[str] = None
    description: str

class ReportCreate(ReportBase):
    attachments: Optional[List[str]] = []
    voice_notes: Optional[List[str]] = []

class ReportUpdate(BaseModel):
    project_name: Optional[str] = None
    project_code: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ReportResponse(ReportBase):
    id: int
    user_id: int
    user_name: str
    status: str
    attachments: List[str] = []
    voice_notes: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
