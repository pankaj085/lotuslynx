from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone
import enum


# enums
class UserRole(str, enum.Enum):
    user = "user"
    editor = "editor"
    admin = "admin"

# user models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.user)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # relationships
    carts = relationship("CartItem", back_populates="user")
    orders = relationship("Order", back_populates="user")