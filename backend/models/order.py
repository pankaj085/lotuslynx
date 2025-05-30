from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone
import enum


# enums
class OrderStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

# order model 
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    total_price = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # relationships 
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    

# orderitem model 
class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    price = Column(Float)
    
    # relationships 
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")