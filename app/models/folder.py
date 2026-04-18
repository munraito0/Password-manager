import uuid

from sqlalchemy import TEXT,Column,DateTime,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone

from app.database import Base


class Folder(Base):
    __tablename__ = "folders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name_encrypted = Column(TEXT, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))