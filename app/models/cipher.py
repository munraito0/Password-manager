import uuid

from sqlalchemy import Column,Integer,String,Text,Boolean,DateTime,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from app.database import Base


class Cipher(Base):
    __tablename__ = "ciphers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey('folders.id'), nullable=True)
    type = Column(Integer, nullable=False)
    name_encrypted = Column(Text, nullable=False)
    notes_encrypted = Column(Text, nullable=False)
    favorite = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True, default=lambda: datetime.now(timezone.utc))
    revision_date = Column(DateTime(timezone=True), nullable=True, default=lambda: datetime.now(timezone.utc))