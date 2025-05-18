# backend/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone
import enum

# enums
class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class OrderStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"


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
    

# product model 
class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    category = Column(String, index=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    #relationships
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    
    
# cart models 
class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    
    # relationships
    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="cart_items")
    
    
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