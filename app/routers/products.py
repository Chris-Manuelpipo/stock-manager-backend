from fastapi import APIRouter, Depends, HTTPException, Query,  UploadFile, File
from sqlalchemy.orm import Session 
from sqlalchemy import func
from typing import List, Optional 
from app.models import models
from app.schemas import schemas
from app.db.database import SessionLocal
import shutil
import os
import uuid


UPLOAD_DIR = "uploads/"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

router = APIRouter(prefix="/products", tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Filtrage, recherche et pagination
@router.get("/", response_model=List[schemas.Product])
def get_products(
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(models.Product)
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
    return query.offset(offset).limit(limit).all()


# Ajouter un produit
@router.post("/create", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Si category_id est fourni, vérifier qu'il existe
    if product.category_id:
        category = db.query(models.ProductCategory).filter(
            models.ProductCategory.id == product.category_id
        ).first()
        if not category:
            raise HTTPException(
                status_code=400, 
                detail=f"Category with ID {product.category_id} does not exist"
            )
    
    db_product = models.Product(**product.dict())
    
    # Si pas d'image_url, laisser null
    if not hasattr(db_product, "image_url"):
        db_product.image_url = None
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Récupérer un produit par ID
@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Mettre à jour un produit
@router.put("/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, updated_product: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in updated_product.dict().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

# Supprimer un produit
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"detail": "Product deleted"}

# Upload image pour un produit
@router.post("/upload-image/{product_id}")
def upload_image(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid image type")

    extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    product.image_url = f"/uploads/{filename}"

    db.commit()
    db.refresh(product)
    return {
        "original_filename": file.filename,
        "image_url": product.image_url
    }

# --- 4️⃣ Produits avec stock bas ---
@router.get("/stock/low-stock", response_model=List[schemas.Product])
def get_low_stock_products(threshold: int = 5, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.quantity < threshold).all()

