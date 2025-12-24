from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# --- ENUMS ---
class MovementType(str, Enum):
    IN = "IN"
    OUT = "OUT"

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    VIEWER = "VIEWER"

class NotificationType(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ALERT = "ALERT"
    SUCCESS = "SUCCESS"

class Priority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"

# --- PRODUITS AVEC CATÉGORIE ---
class ProductCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategory(ProductCategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int = 0
    min_stock: int = 5
    category_id: Optional[int] = 1

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    image_url: Optional[str] = None
    category: Optional[ProductCategory] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# --- MOUVEMENTS ---
class StockMovementBase(BaseModel):
    product_id: int
    type: MovementType
    quantity: int
    reason: Optional[str] = None

class StockMovementCreate(StockMovementBase):
    pass

class StockMovement(StockMovementBase):
    id: int
    user_id: Optional[int] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

# --- NOUVEAU : AUTHENTIFICATION ---
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: UserRole = UserRole.MANAGER

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None

# --- NOUVEAU : NOTIFICATIONS ---
class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType = NotificationType.INFO
    priority: Priority = Priority.NORMAL

class NotificationCreate(NotificationBase):
    user_id: int

class Notification(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- NOUVEAU : PARAMÈTRES ---
class SettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class SettingUpdate(BaseModel):
    value: str

class Setting(SettingBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

# --- NOUVEAU : RAPPORTS ---
class DashboardStats(BaseModel):
    total_products: int
    total_stock: int
    total_stock_value: float
    total_entries: int
    total_exits: int
    low_stock_count: int

class StockValueReport(BaseModel):
    total_value: float
    by_category: List[dict]
    by_metal: List[dict]  # Si vous avez le champ métal

class MovementTrend(BaseModel):
    period: str
    entries: int
    exits: int
    net_change: int