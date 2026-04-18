from sqlalchemy import Column,Text,JSON,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class CipherLogin(Base):
    __tablename__ = "cipher_logins"
    cipher_id = Column(UUID(as_uuid=True), ForeignKey('ciphers.id'), primary_key=True)
    username_encrypted = Column(Text, nullable=False)
    password_encrypted = Column(Text, nullable=False)
    totp_encrypted = Column(Text, nullable=True)
    uris_encrypted = Column(JSON, nullable=False)
    password_history_encrypted = Column(JSON, nullable=True)
