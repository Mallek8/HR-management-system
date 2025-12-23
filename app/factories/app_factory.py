"""
app_factory.py - Usine de création de l'application FastAPI

Utilise le pattern Factory pour créer et configurer l'application FastAPI
avec tous ses routeurs, middlewares et autres composants.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os

# Routeurs API
from app.api.auth import auth_router
from app.api.employees import employee_router
from app.api.leave_api import router as leave_router
from app.api.profile import profile_router
from app.api.dashboard_employee import dashboard_employee_router
from app.api.dashboard_admin import router as dashboard_admin_router
from app.api.dashboard_supervisor import router as dashboard_supervisor_router
from app.api.leave_requests import notification_router, leave_requests_router
from app.api.trainings import router as trainings_router
from app.api.training_requests import training_request_router, training_request_page_router
from app.api.evaluations import router as evaluation_router
from app.api.objectives import router as objective_router
from app.api.reports import report_router
from app.api.notification_api import router as notification_api_router
from app.api.leave_state_api import router as leave_state_api_router


# Services de démarrage
from app.services.auth_service import AuthService
from app.services.leave_service import LeaveService
from app.services.event_service import EventService


def create_app() -> FastAPI:
    """
    Crée et configure l'application FastAPI avec tous ses composants
    
    Returns:
        L'instance FastAPI configurée
    """
    # ----------------------------------------------------
    # Création de l'instance FastAPI
    # ----------------------------------------------------
    app = FastAPI(
        title="HannaWork System API",
        description="API pour le système de gestion des ressources humaines",
        version="1.0.0"
    )
    
    # ----------------------------------------------------
    # Configuration des fichiers statiques
    # ----------------------------------------------------
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/static"))
    if not os.path.exists(static_dir):
        raise FileNotFoundError(f"Static directory not found: {static_dir}")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # ----------------------------------------------------
    # Configuration du moteur de template (Jinja2)
    # ----------------------------------------------------
    templates = Jinja2Templates(directory="frontend/templates")

    # ----------------------------------------------------
    # Configuration du middleware CORS
    # ----------------------------------------------------
    origins = [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # ----------------------------------------------------
    # Inclusion des routeurs API
    # ----------------------------------------------------
    app.include_router(auth_router)
    app.include_router(employee_router)
    app.include_router(leave_router)
    app.include_router(profile_router)
    app.include_router(dashboard_employee_router)
    app.include_router(dashboard_admin_router)
    app.include_router(dashboard_supervisor_router)
    app.include_router(trainings_router)
    app.include_router(training_request_router)
    app.include_router(training_request_page_router)
    app.include_router(leave_requests_router)
    app.include_router(notification_router)
    app.include_router(evaluation_router)
    app.include_router(objective_router)
    app.include_router(report_router)
    app.include_router(notification_api_router)
    app.include_router(leave_state_api_router)
   
    
    # ----------------------------------------------------
    # Tâches d'initialisation au démarrage
    # ----------------------------------------------------
    @app.on_event("startup")
    def startup_tasks():
        """
        Tâches d'initialisation au démarrage.
        
        Toutes les tâches sont NON-BLOQUANTES : elles ne peuvent pas faire planter
        l'application au démarrage. Les erreurs sont loggées mais ignorées.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("Initialisation de l'application RH")
        
        # Initialisation admin (non-bloquante)
        try:
            AuthService.ensure_admin_exists()
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation admin (ignorée): {e}")
        
        # Initialisation des balances de congés (non-bloquante)
        try:
            LeaveService.initialize_balances()
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des balances (ignorée): {e}")
        
        # Initialisation du système d'événements (pattern Observer) (non-bloquante)
        try:
            EventService.initialize()
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des événements (ignorée): {e}")
        
        logger.info("Démarrage terminé.")

    # ----------------------------------------------------
    # Vérification des fichiers statiques (utile en dev)
    # ----------------------------------------------------
    @app.get("/static/{path:path}")
    async def static_files(path: str):
        return {"message": f"Static file requested: {path}"}

    return app
