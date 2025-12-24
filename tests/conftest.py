import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db, SessionLocal
import os

# Base de données de test en mémoire
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer les tables une fois
@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db):
    # Override la dépendance get_db
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    # Créer un utilisateur de test d'abord
    from app.models import models
    from passlib.context import CryptContext
    import hashlib
    
    db = TestingSessionLocal()
    
    # Supprimer l'admin existant
    db.query(models.User).delete()
    
    # Créer nouvel admin
    hashed = hashlib.sha256("admin123".encode()).hexdigest()
    admin = models.User(
        email="admin@test.com",
        username="admin",
        full_name="Test Admin",
        hashed_password=hashed,
        role=models.UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    
    # Login
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    
    db.close()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_product(client, auth_headers):
    # Crée un produit pour les tests
    product_data = {
        "name": "Test Product",
        "description": "For testing",
        "price": 99.99,
        "quantity": 10,
        "min_stock": 5,
        "category_id": None
    }
    response = client.post("/products/", json=product_data, headers=auth_headers)
    return response.json()["id"]
