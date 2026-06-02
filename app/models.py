from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, ARRAY
from .database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, nullable=False, primary_key=True)
    business_name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    account_tier = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    incidents = relationship("Tickets", back_populates="owner")
    role = Column(String, server_default="customer", default="customer", nullable=True)
     
class Tickets(Base):
    __tablename__ = "tickets"
    id = Column(Integer, nullable=False, primary_key=True)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    department = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    user_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="incidents")
    tags = Column(ARRAY(String), nullable=False)
    extracted_keywords = Column(ARRAY(String), nullable=False)
    latency = Column(Float, nullable=True)

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, server_default="Admin", default="Admin", nullable=False)