from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models import models
from app.schemas import schemas
from app.db.database import SessionLocal
from typing import List, Optional
from datetime import datetime


router = APIRouter(prefix="/movements", tags=["Stock Movements"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Liste tous les mouvements
@router.get("/", response_model=List[schemas.StockMovement])
def get_movements(db: Session = Depends(get_db)):
    return db.query(models.StockMovement).all()

# Ajouter un mouvement
@router.post("/", response_model=schemas.StockMovement)
def create_movement(movement: schemas.StockMovementCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == movement.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Mettre à jour la quantité du produit
    if movement.type == schemas.MovementType.IN:
        product.quantity += movement.quantity
    elif movement.type == schemas.MovementType.OUT:
        if movement.quantity > product.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")
        product.quantity -= movement.quantity

    db_movement = models.StockMovement(**movement.dict())  # ⚡ Convertir Pydantic -> SQLAlchemy
    if isinstance(movement.type, str):
        db_movement.type = movement.type.upper() 
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
     # Convertissez la réponse
    response = schemas.StockMovement.from_orm(db_movement)
    response.type = db_movement.type.value  # Force la valeur correcte
    
    return response

# Historique des mouvements
@router.get("/history", response_model=List[schemas.StockMovement])
def get_movement_history(start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         db: Session = Depends(get_db)):
    query = db.query(models.StockMovement)
    if start_date:
        query = query.filter(models.StockMovement.timestamp >= start_date)
    if end_date:
        query = query.filter(models.StockMovement.timestamp <= end_date)
    return query.order_by(models.StockMovement.timestamp.desc()).all()

# Statistiques (entrées / sorties)
from sqlalchemy import func

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_entries = db.query(func.sum(models.StockMovement.quantity))\
                      .filter(models.StockMovement.type == "IN").scalar() or 0
    total_exits = db.query(func.sum(models.StockMovement.quantity))\
                    .filter(models.StockMovement.type == "OUT").scalar() or 0
    total_products = db.query(func.count(models.Product.id)).scalar()
    total_stock = db.query(func.sum(models.Product.quantity)).scalar() or 0
    return {
        "total_products": total_products,
        "total_stock": total_stock,
        "total_entries": total_entries,
        "total_exits": total_exits
    }

# Filtrage, recherche et pagination
@router.get("/movements/", response_model=List[schemas.StockMovement])
def get_movements(
    type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.StockMovement)
    if type:
        query = query.filter(models.StockMovement.type == type)
    if start_date:
        query = query.filter(models.StockMovement.timestamp >= start_date)
    if end_date:
        query = query.filter(models.StockMovement.timestamp <= end_date)
    return query.all()

