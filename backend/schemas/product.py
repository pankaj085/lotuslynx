# product schemas
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
    
    model_config = {'from_attributes': True}
    
    
class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    
    model_config = {'from_attributes': True}