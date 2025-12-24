from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class MovementType(enum.Enum):
    IN = "IN"
    OUT = "OUT"

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    VIEWER = "VIEWER"

# --- NOUVEAU : Catégorie de produit ---
class ProductCategory(Base):
    __tablename__ = "product_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation avec produits
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    min_stock = Column(Integer, default=5)  # Seuil d'alerte
    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    image_url = Column(String(255), nullable=True)

    # Relations
    category = relationship("ProductCategory", back_populates="products")
    movements = relationship("StockMovement", back_populates="product")

class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)  # Raison du mouvement
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Qui a fait le mouvement
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relations
    product = relationship("Product", back_populates="movements")
    user = relationship("User", back_populates="movements")

# --- NOUVEAU : Utilisateurs (admins) ---
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MANAGER)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    movements = relationship("StockMovement", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

# --- NOUVEAU : Notifications ---
class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    message = Column(String(500))
    type = Column(String(50), default="INFO")  # info, warning, alert, success
    priority = Column(String(20), default="NORMAL")  # low, normal, high
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="notifications")

# --- NOUVEAU : Paramètres système ---
class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(500))
    description = Column(String(255))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# --- NOUVEAU : Logs d'audit ---
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # create_product, update_stock, etc.
    resource_type = Column(String(50))  # product, movement, user
    resource_id = Column(Integer, nullable=True)
    details = Column(String(500))
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)