import uuid

from sqlalchemy import Column,Integer,String,Text,Boolean,DateTime,ForeignKey
from sqlalchemy.dialects.postgresql import UUID

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
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    revision_date = Column(DateTime, nullable=True)