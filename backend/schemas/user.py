from pydantic import BaseModel
from datetime import datetime
from enum import Enum

# enums
class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    
    
# user schemas
class UserBase(BaseModel):
    email: str
    username: str
    
    
class UserCreate(UserBase):
    email: str
    username: str
    password: str
    
    model_config = {'from_attributes': True}
    
    
class UserLogin(BaseModel):
    username: str
    password: str
    
    
class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    
    model_config = {'from_attributes': True}