from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    products, 
    movements, 
    dashboard,
   # auth,      # Nouveau
    users,     # Nouveau
    reports,   # Nouveau
    categories, # Nouveau
    settings,  # À créer
    notifications  # À créer
)
from app.authentification import auth

app = FastAPI(title=" Stock Manager API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(movements.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(categories.router)

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "Landry Store Stock Manager API"}