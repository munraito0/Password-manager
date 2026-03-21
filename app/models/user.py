import uuid

from sqlalchemy import Column, String, Boolean,Integer,DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    master_password_hash = Column(String(255), nullable=False)
    master_password_hint = Column(String(255), nullable=False)
    kdf_type = Column(Integer, nullable=False)
    kdf_iterations = Column(Integer, nullable=False)
    two_factor_enabled = Column(Boolean, nullable=False, default=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    security_stamp = Column(String(255), nullable=True)
    premium = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)