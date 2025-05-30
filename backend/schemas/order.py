from pydantic import BaseModel
from typing import List
from .product import ProductResponse
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"
    

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
    
    model_config = {'from_attributes': True}
    
        
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
    
    model_config = {'from_attributes': True}