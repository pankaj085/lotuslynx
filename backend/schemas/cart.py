from pydantic import BaseModel
from .product import ProductResponse

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
    
    model_config = {'from_attributes': True}