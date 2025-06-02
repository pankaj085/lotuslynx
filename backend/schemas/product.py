from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    image_url: Optional[str] = None
    
    class Config:
        orm_mode = True

class ProductWithPrice(BaseModel):
    product: ProductResponse
    client_secret: str
    amount: int