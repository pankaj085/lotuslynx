from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base


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