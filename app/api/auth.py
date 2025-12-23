"""
auth.py - Gestion des routes d'authentification

Ce module gère les routes FastAPI liées à l'authentification :
- Affichage de la page de connexion
- Soumission du formulaire de login
- Déconnexion

La logique métier est déléguée à AuthService.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.database import get_db

auth_router = APIRouter()

# -----------------------------------------------------
# Route : page de connexion
# -----------------------------------------------------
@auth_router.get("/")
def login_page(request: Request):
    """Affiche la page de connexion."""
    return AuthService.render_login_page(request)


# -----------------------------------------------------
# Route : traitement du login
# -----------------------------------------------------
@auth_router.post("/login")
def handle_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Traite les données du formulaire de connexion."""
    return AuthService.login_user(request, db, username, password)


# -----------------------------------------------------
# Route : déconnexion
# -----------------------------------------------------
@auth_router.get("/logout")
def logout():
    """Déconnecte l'utilisateur."""
    return AuthService.logout_user()
