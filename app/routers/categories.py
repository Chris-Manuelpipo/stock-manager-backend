from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models import models
from app.schemas import schemas
from app.db.database import SessionLocal
from app.authentification.auth import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.ProductCategory])
def get_categories(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    categories = db.query(models.ProductCategory).all()
    return categories

@router.post("/", response_model=schemas.ProductCategory)
def create_category(
    category: schemas.ProductCategoryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Vérifier si la catégorie existe déjà
    existing = db.query(models.ProductCategory).filter(
        models.ProductCategory.name == category.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    db_category = models.ProductCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/{category_id}", response_model=schemas.ProductCategory)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    category = db.query(models.ProductCategory).filter(
        models.ProductCategory.id == category_id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category

@router.put("/{category_id}", response_model=schemas.ProductCategory)
def update_category(
    category_id: int,
    category_update: schemas.ProductCategoryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    category = db.query(models.ProductCategory).filter(
        models.ProductCategory.id == category_id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Vérifier si le nouveau nom existe déjà
    if category_update.name != category.name:
        existing = db.query(models.ProductCategory).filter(
            models.ProductCategory.name == category_update.name
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category name already exists")
    
    category.name = category_update.name
    category.description = category_update.description
    
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    category = db.query(models.ProductCategory).filter(
        models.ProductCategory.id == category_id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Vérifier si des produits utilisent cette catégorie
    products_count = db.query(models.Product).filter(
        models.Product.category_id == category_id
    ).count()
    
    if products_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category with {products_count} associated products"
        )
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}