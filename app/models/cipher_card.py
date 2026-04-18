from sqlalchemy import Column,Text,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class CipherCard(Base):
    __tablename__ = "cipher_cards"
    cipher_id = Column(UUID(as_uuid=True), ForeignKey('ciphers.id'), primary_key=True)
    cardholder_name_encrypted = Column(Text, nullable=False)
    brand_encrypted = Column(Text, nullable=False)
    number_encrypted = Column(Text, nullable=False)
    exp_month_encrypted = Column(Text, nullable=False)
    exp_year_encrypted = Column(Text, nullable=False)
    code_encrypted = Column(Text, nullable=False)
