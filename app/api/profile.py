# app/api/profile.py
"""
profile.py – API de gestion du profil employé

Responsabilités :
- Affichage de la page de profil utilisateur
- Mise à jour du profil de l'utilisateur

Design Patterns utilisés :
- Service Layer : La logique métier est dans `EmployeeService`

"""

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.schemas import ProfileUpdate
from app.services.employee_service import EmployeeService

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/profile")
def profile_page(request: Request, db: Session = Depends(get_db)):
    """
    Affiche la page de profil de l'utilisateur courant.
    """
    user_email = request.cookies.get("user_email")
    if not user_email:
        raise HTTPException(status_code=403, detail="Non authentifié")

    user = EmployeeService.get_employee_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    supervisor = EmployeeService.get_supervisor(db, user.supervisor_id)
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "supervisor": supervisor
    })

@router.put("/api/profile/update")
def update_profile(profile: ProfileUpdate, db: Session = Depends(get_db)):
    """
    Met à jour le profil de l'utilisateur courant.
    """
    return EmployeeService.update_employee_profile(db, profile)

profile_router = router