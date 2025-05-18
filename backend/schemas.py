#backend/schemas.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

# enums
class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    
class OrderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"
    
# user schemas
class UserBase(BaseModel):
    email: str
    username: str
    
class UserCreate(UserBase):
    password: str
    
class UserLogin(BaseModel):
    username: str
    password: str
    
class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    
    class Config:
        orm_mode = True
       
        
# product schemas
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    
class ProductCreate(ProductBase):
    pass
   
    
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    
class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        
        
# cart schemas
class CartItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float
    
class CartItemCreate(CartItemBase):
    pass

class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    product: ProductResponse
    
    class Config:
        orm_mode = True
        

# order schemas
class OrderItemBase(BaseModel):
    id: int
    quantity: int
    price: float
    
class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    product: ProductResponse
    
    class Config:
        orm_mode = True
        
class OrderBase(BaseModel):
    total_price: float
    
class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    
class OrderResponse(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemResponse]
    
    class Config:
        orm_mode = True