import sys
import os

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.db.database import engine, SessionLocal
from app.models import models
import hashlib  # Alternative si bcrypt ne marche pas

# Alternative simple au hashage si bcrypt pose problème
def get_password_hash_simple(password: str) -> str:
    """Hash simple si bcrypt ne fonctionne pas"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    try:
        print("Creating database tables...")
        print(f"Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./stock.db')}")
        
        # Créer toutes les tables
        models.Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        
        try:
            # Vérifier si l'admin existe déjà
            admin = db.query(models.User).filter(models.User.username == "admin").first()
            if not admin:
                print("Creating default admin user...")
                
                # Essayer bcrypt d'abord, sinon utiliser SHA256
                try:
                    from passlib.context import CryptContext
                    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                    hashed_password = pwd_context.hash("admin123")
                    print("✓ Using bcrypt for password hashing")
                except Exception as e:
                    print(f"⚠️  Bcrypt error: {e}")
                    print("⚠️  Falling back to SHA256 (less secure)")
                    hashed_password = get_password_hash_simple("admin123")
                
                admin_user = models.User(
                    email="admin@landrystore.com",
                    username="admin",
                    full_name="Administrator",
                    hashed_password=hashed_password,
                    role=models.UserRole.ADMIN,
                    is_active=True
                )
                db.add(admin_user)
            
            # Vérifier si les catégories existent déjà
            categories = [
                "Colliers",
                "Bracelets", 
                "Boucles d'oreilles",
                "Bagues",
                "Montres",
                "Broches",
                "Autres"
            ]
            
            for cat_name in categories:
                existing = db.query(models.ProductCategory).filter(
                    models.ProductCategory.name == cat_name
                ).first()
                if not existing:
                    print(f"Creating category: {cat_name}")
                    category = models.ProductCategory(name=cat_name)
                    db.add(category)
            
            # Créer un manager de test (avec le même mécanisme de hash)
            manager = db.query(models.User).filter(models.User.username == "manager").first()
            if not manager:
                print("Creating test manager user...")
                
                try:
                    from passlib.context import CryptContext
                    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                    hashed_password = pwd_context.hash("manager123")
                except:
                    hashed_password = get_password_hash_simple("manager123")
                
                manager_user = models.User(
                    email="manager@landrystore.com",
                    username="manager",
                    full_name="Test Manager",
                    hashed_password=hashed_password,
                    role=models.UserRole.MANAGER,
                    is_active=True
                )
                db.add(manager_user)
            
            # Créer un viewer de test
            viewer = db.query(models.User).filter(models.User.username == "viewer").first()
            if not viewer:
                print("Creating test viewer user...")
                
                try:
                    from passlib.context import CryptContext
                    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                    hashed_password = pwd_context.hash("viewer123")
                except:
                    hashed_password = get_password_hash_simple("viewer123")
                
                viewer_user = models.User(
                    email="viewer@landrystore.com",
                    username="viewer",
                    full_name="Test Viewer",
                    hashed_password=hashed_password,
                    role=models.UserRole.VIEWER,
                    is_active=True
                )
                db.add(viewer_user)
            
            db.commit()
            print("\n" + "="*50)
            print("✅ Database initialized successfully!")
            print("="*50)
            print("\nDefault users created:")
            print("-" * 30)
            print("  Admin:     username='admin', password='admin123'")
            print("  Manager:   username='manager', password='manager123'")
            print("  Viewer:    username='viewer', password='viewer123'")
            print("\nDefault categories created:")
            print("-" * 30)
            for cat in categories:
                print(f"  • {cat}")
            print("\n⚠️  Note: Using SHA256 hashing instead of bcrypt")
            print("   Run: pip install bcrypt==4.0.1 for better security")
            print("\n")
            
        except Exception as e:
            print(f"❌ Error during data initialization: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    init_db()