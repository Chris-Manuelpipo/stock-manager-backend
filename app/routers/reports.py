from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from app.models import models
from app.schemas import schemas
from app.db.database import SessionLocal
from app.authentification.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    total_products = db.query(func.count(models.Product.id)).scalar()
    total_stock = db.query(func.sum(models.Product.quantity)).scalar() or 0
    
    # Valeur totale du stock
    total_stock_value = db.query(
        func.sum(models.Product.price * models.Product.quantity)
    ).scalar() or 0.0
    
    total_entries = db.query(func.count(models.StockMovement.id)).filter(
        models.StockMovement.type == models.MovementType.IN
    ).scalar()
    
    total_exits = db.query(func.count(models.StockMovement.id)).filter(
        models.StockMovement.type == models.MovementType.OUT
    ).scalar()
    
    low_stock_count = db.query(func.count(models.Product.id)).filter(
        models.Product.quantity < models.Product.min_stock
    ).scalar()
    
    return {
        "total_products": total_products,
        "total_stock": total_stock,
        "total_stock_value": total_stock_value,
        "total_entries": total_entries,
        "total_exits": total_exits,
        "low_stock_count": low_stock_count
    }

@router.get("/stock-value")
def get_stock_value_report(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Valeur totale
    total_value = db.query(
        func.sum(models.Product.price * models.Product.quantity)
    ).scalar() or 0.0
    
    # Valeur par catégorie
    by_category = db.query(
        models.ProductCategory.name,
        func.sum(models.Product.price * models.Product.quantity).label("value")
    ).join(
        models.Product, models.Product.category_id == models.ProductCategory.id
    ).group_by(models.ProductCategory.id).all()
    
    # Convertir en dict
    category_data = [{"category": cat, "value": val} for cat, val in by_category]
    
    return {
        "total_value": total_value,
        "by_category": category_data
    }

@router.get("/movements/daily")
def get_daily_movements(
    date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if not date:
        date = datetime.utcnow().date()
    
    start_date = datetime.combine(date, datetime.min.time())
    end_date = datetime.combine(date, datetime.max.time())
    
    movements = db.query(models.StockMovement).filter(
        models.StockMovement.timestamp >= start_date,
        models.StockMovement.timestamp <= end_date
    ).all()
    
    entries = sum(m.quantity for m in movements if m.type == models.MovementType.IN)
    exits = sum(m.quantity for m in movements if m.type == models.MovementType.OUT)
    
    return {
        "date": date.isoformat(),
        "total_movements": len(movements),
        "entries": entries,
        "exits": exits,
        "net_change": entries - exits,
        "movements": movements
    }

@router.get("/alerts/low-stock")
def get_low_stock_alerts(
    threshold: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    query = db.query(models.Product)
    if threshold:
        query = query.filter(models.Product.quantity < threshold)
    else:
        query = query.filter(models.Product.quantity < models.Product.min_stock)
    
    low_stock_products = query.all()
    
    return {
        "count": len(low_stock_products),
        "products": low_stock_products
    }

@router.get("/performance")
def get_stock_performance(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Mouvements sur la période
    movements = db.query(models.StockMovement).filter(
        models.StockMovement.timestamp >= start_date
    ).all()
    
    # Calculer les métriques
    total_entries = sum(m.quantity for m in movements if m.type == models.MovementType.IN)
    total_exits = sum(m.quantity for m in movements if m.type == models.MovementType.OUT)
    
    # Produits avec rotation
    products = db.query(models.Product).all()
    performance_data = []
    
    for product in products:
        product_movements = [
            m for m in movements if m.product_id == product.id
        ]
        product_entries = sum(m.quantity for m in product_movements if m.type == models.MovementType.IN)
        product_exits = sum(m.quantity for m in product_movements if m.type == models.MovementType.OUT)
        
        performance_data.append({
            "product_id": product.id,
            "product_name": product.name,
            "current_stock": product.quantity,
            "entries": product_entries,
            "exits": product_exits,
            "turnover_rate": product_exits / product.quantity if product.quantity > 0 else 0
        })
    
    return {
        "period_days": days,
        "total_entries": total_entries,
        "total_exits": total_exits,
        "net_change": total_entries - total_exits,
        "product_performance": sorted(performance_data, key=lambda x: x["turnover_rate"], reverse=True)[:10]
    }