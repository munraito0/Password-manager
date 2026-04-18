import uuid

from sqlalchemy import Column,Integer,Text,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class CipherField(Base):
    __tablename__ = "cipher_fields"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cipher_id = Column(UUID(as_uuid=True), ForeignKey('ciphers.id'), nullable=False)
    type = Column(Integer, nullable=False)
    name_encrypted = Column(Text, nullable=False)
    value_encrypted = Column(Text, nullable=False)
