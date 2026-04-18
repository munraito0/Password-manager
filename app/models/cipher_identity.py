from sqlalchemy import Column,Text,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class CipherIdentity(Base):
    __tablename__ = "cipher_identities"
    cipher_id = Column(UUID(as_uuid=True), ForeignKey('ciphers.id'), primary_key=True)
    title_encrypted = Column(Text, nullable=False)
    first_name_encrypted = Column(Text, nullable=False)
    last_name_encrypted = Column(Text, nullable=False)
    email_encrypted = Column(Text, nullable=False)
    phone_encrypted = Column(Text, nullable=False)
    address_encrypted = Column(Text, nullable=False)
    ssn_encrypted = Column(Text, nullable=False)
