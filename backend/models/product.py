# product model 
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone


class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    category = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    #relationships
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")