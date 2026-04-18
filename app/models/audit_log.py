import uuid

from sqlalchemy import Column,Integer,String,DateTime,JSON,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    event_type = Column(Integer, nullable=False)
    ip_address = Column(String(255), nullable=False)
    device_info = Column(String(255), nullable=False)
    event_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    meta = Column("metadata", JSON, nullable=True)
