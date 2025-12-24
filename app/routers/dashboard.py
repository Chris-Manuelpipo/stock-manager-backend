from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models import models
from app.schemas import schemas
from app.db.database import SessionLocal
from datetime import datetime
import csv
from fastapi.responses import StreamingResponse
from io import StringIO

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1️⃣ Statistiques globales ---
@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_products = db.query(func.count(models.Product.id)).scalar()
    total_stock = db.query(func.sum(models.Product.quantity)).scalar() or 0
    total_entries = db.query(func.count(models.StockMovement.id)).filter(models.StockMovement.type == "IN").scalar()
    total_exits = db.query(func.count(models.StockMovement.id)).filter(models.StockMovement.type == "OUT").scalar()
    return {
        "total_products": total_products,
        "total_stock": total_stock,
        "total_entries": total_entries,
        "total_exits": total_exits
    }

# --- 2️⃣ Historique des mouvements ---
@router.get("/movements", response_model=List[schemas.StockMovement])
def get_movement_history(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    product_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.StockMovement)
    if start_date:
        query = query.filter(models.StockMovement.timestamp >= start_date)
    if end_date:
        query = query.filter(models.StockMovement.timestamp <= end_date)
    if product_id:
        query = query.filter(models.StockMovement.product_id == product_id)
    return query.order_by(models.StockMovement.timestamp.desc()).all()

# --- 3️⃣ Entrées/Sorties par période ---
@router.get("/movement-stats")
def movement_stats(
    period: str = Query("day", regex="^(day|week|month)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        models.StockMovement.timestamp,
        models.StockMovement.type,
        models.StockMovement.quantity
    )
    if start_date:
        query = query.filter(models.StockMovement.timestamp >= start_date)
    if end_date:
        query = query.filter(models.StockMovement.timestamp <= end_date)
    
    data = query.all()
    result = {}
    
    for m in data:
        if period == "day":
            key = m.timestamp.date()
        elif period == "week":
            key = m.timestamp.isocalendar()[1]  # numéro de semaine
        else:
            key = m.timestamp.strftime("%Y-%m")  # mois
        
        if key not in result:
            result[key] = {"entries": 0, "exits": 0}
        
        if m.type == "IN":
            result[key]["entries"] += m.quantity
        else:
            result[key]["exits"] += m.quantity
    
    # Transformer en liste triée
    final_result = [{"period": k, **v} for k, v in sorted(result.items())]
    return final_result

# --- 4️⃣ Produits avec stock bas ---
@router.get("/low-stock", response_model=List[schemas.Product])
def get_low_stock_products(threshold: int = 5, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.quantity < threshold).all()

@router.get("/export/products")
def export_products_csv(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Description", "Price", "Quantity", "Created At", "Image URL"])
    for p in products:
        writer.writerow([p.id, p.name, p.description, p.price, p.quantity, p.created_at, p.image_url])
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=products.csv"})

@router.get("/notify/low-stock")
def notify_low_stock(threshold: int = 5, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.quantity < threshold).all()
    return {"low_stock_products": [p.name for p in products]}

@router.get("/chart/movements")
def chart_data(db: Session = Depends(get_db)):
    data = db.query(models.StockMovement.timestamp, models.StockMovement.type, models.StockMovement.quantity).all()
    chart = {"labels": [], "entries": [], "exits": []}
    for m in data:
        date = m.timestamp.date()
        if date not in chart["labels"]:
            chart["labels"].append(str(date))
            chart["entries"].append(0)
            chart["exits"].append(0)
        idx = chart["labels"].index(str(date))
        if m.type == "IN":
            chart["entries"][idx] += m.quantity
        else:
            chart["exits"][idx] += m.quantity
    return chart
