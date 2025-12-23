"""
main.py - Point d'entrée principal de l'application FastAPI

Projet : Système de gestion des ressources humaines
Auteur : Mallek Hannachi
Année : Mars 2025
Type : Projet personnel académique

Responsabilités :
- Démarrer l'application via l'usine (factory) `create_app`
- Configurer les fichiers statiques et templates Jinja2
- Servir le favicon
- Lancer les initialisations au démarrage (départements, etc.)

Design Patterns :
- Factory Method : `create_app()` pour instancier l'app FastAPI
- Dependency Injection : `SessionLocal` utilisé pour init DB au démarrage
- Strategy : Utilisé pour les notifications (via notification_api, intégré dans app_factory)
"""

import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.factories.app_factory import create_app
from app.database import SessionLocal
from app.api.leave_api import initialize_departments  # Si utilisé ici uniquement pour init

logger = logging.getLogger(__name__)
from app.api.dashboard_employee import dashboard_employee_router
from app.api.leave_api import router as leave_router
from app.api.employees import router as employee_router
from app.api.trainings import router as training_router
from app.api.evaluations import router as evaluation_router
from app.api.routes import router as api_router
from app.api.leave_requests import leave_requests_router, notification_router

# ============================================================
# Création de l'application via la factory
# ============================================================

app: FastAPI = create_app()

# ============================================================
# Configuration des fichiers statiques (CSS, JS, images)
# ============================================================

static_dir = os.path.join(os.path.dirname(__file__), "../frontend/static")

if not os.path.exists(static_dir):
    raise FileNotFoundError(f"Le répertoire des fichiers statiques est introuvable : {static_dir}")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ============================================================
# Configuration du moteur de templates Jinja2
# ============================================================

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../frontend/templates"))

# ============================================================
# Route spéciale pour le favicon (favicon.ico)
# ============================================================

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Sert l'icône favicon.ico si elle est présente dans les fichiers statiques.
    """
    favicon_path = os.path.join(static_dir, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    return JSONResponse(content={"error": "favicon.ico not found"}, status_code=404)

# ============================================================
# Événement de démarrage : initialiser les données statiques
# ============================================================

@app.on_event("startup")
def startup_event():
    """
    Tâches exécutées au démarrage :
    - Test de la connexion à la base de données
    - Initialisation des départements (si non présents)
    
    Cette fonction ne bloque pas le démarrage de l'application si la base de données
    n'est pas disponible. Les erreurs sont loggées mais l'application continue.
    """
    from app.database import test_connection, SessionLocal
    
    # Tester la connexion au démarrage (non bloquant)
    if test_connection():
        if SessionLocal is not None:
            try:
                db = SessionLocal()
                try:
                    initialize_departments(db)
                except Exception as e:
                    logger.error(f"Erreur lors de l'initialisation des départements: {e}")
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"Erreur lors de l'accès à la base de données: {e}")
        else:
            logger.warning("SessionLocal non disponible - initialisation des départements ignorée")
    else:
        logger.warning("Impossible de se connecter à la base de données au démarrage. L'application continuera mais certaines fonctionnalités ne seront pas disponibles.")

# ============================================================
# Routes de base pour les templates HTML
# Les routes API sont définies dans app_factory.py
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard_admin", response_class=HTMLResponse)
async def dashboard_admin(request: Request):
    # La vérification de l'authentification est gérée par les dépendances dans app_factory
    return templates.TemplateResponse("dashboard_admin.html", {"request": request})

@app.get("/employees", response_class=HTMLResponse)
async def employees_page(request: Request):
    return templates.TemplateResponse("employees.html", {"request": request})

@app.get("/dashboard_supervisor", response_class=HTMLResponse)
async def dashboard_supervisor_page(request: Request):
    return templates.TemplateResponse("dashboard_supervisor.html", {"request": request})

@app.get("/leaves", response_class=HTMLResponse)
async def leaves_page(request: Request):
    return templates.TemplateResponse("leaves.html", {"request": request})

@app.get("/trainings", response_class=HTMLResponse)
async def trainings_page(request: Request):
    return templates.TemplateResponse("trainings.html", {"request": request})

@app.get("/evaluations", response_class=HTMLResponse)
async def evaluations_page(request: Request):
    return templates.TemplateResponse("evaluations.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/logout")
async def logout():
    return {"message": "Déconnexion réussie"}

# Enregistrer les routers
app.include_router(employee_router, prefix="/api/employees", tags=["employees"])
app.include_router(leave_router, prefix="/api/leaves", tags=["leaves"])
app.include_router(evaluation_router, prefix="/api/evaluations", tags=["evaluations"])
app.include_router(training_router, prefix="/api/trainings", tags=["trainings"])
app.include_router(dashboard_employee_router, tags=["dashboard_employee"])
app.include_router(api_router, prefix="/api", tags=["api"])
app.include_router(leave_requests_router, tags=["leave_requests"])
app.include_router(notification_router, tags=["notifications"])
