from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import datetime
import logging

from app.database import get_db
from app.services.dashboard_controller import DashboardController  # ⬅ Nouveau controller
from app.services.leave_service import LeaveService
from app.services.notification_service import NotificationService
from app.services.employee_service import EmployeeService
from app.services.training_service import TrainingService
from app.models.employee import Employee

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")
logger = logging.getLogger(__name__)

"""
dashboard_employee.py

Ce module contient la route du tableau de bord employé.
Il s'appuie sur DashboardController pour encapsuler la logique métier.

Responsabilités :
- Vérifie l'authentification via cookie
- Délègue la logique métier à un controller
- Affiche le dashboard avec les données employé
"""

@router.get("/dashboard_employee", response_class=HTMLResponse)
async def get_dashboard_employee(request: Request):
    """
    Route pour afficher le tableau de bord de l'employé.
    """
    return templates.TemplateResponse("dashboard_employee.html", {"request": request})

@router.get("/api/employee/dashboard/{email}")
async def get_employee_dashboard_stats(email: str, db: Session = Depends(get_db)):
    """
    Route API pour récupérer toutes les statistiques du tableau de bord d'un employé.
    Retourne les données de congés, formations, taux de présence, etc.
    """
    try:
        # Récupérer l'employé par email
        employee = db.query(Employee).filter(Employee.email == email).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
        
        # Récupérer les statistiques de congés
        leave_stats = LeaveService.get_leave_stats_for_employee(db, employee.id)
        
        # Récupérer le solde de congés
        leave_balance = LeaveService.get_leave_balance(db, employee.id)
        
        # Récupérer les statistiques de formations
        training_stats = TrainingService.get_training_stats_for_employee(db, employee.id)
        
        # Calculer le taux de présence (sur les 30 derniers jours)
        # Note: Ceci est un exemple simplifié, à adapter selon votre logique métier
        attendance_rate = 95  # Valeur par défaut en pourcentage
        
        # Récupérer les données pour le graphique d'évolution des congés
        current_year = datetime.now().year
        leave_evolution = LeaveService.get_leave_evolution_for_employee(db, employee.id, current_year)
        
        # Récupérer les activités récentes
        recent_activities = NotificationService.get_recent_activities_for_employee(db, employee.id)
        
        return {
            "employee": {
                "id": employee.id,
                "name": employee.name,
                "email": employee.email,
                "department": employee.department or "Non assigné",
                "position": employee.role or "Non assigné"
            },
            "leave_stats": leave_stats,
            "leave_balance": leave_balance,
            "training_stats": training_stats,
            "attendance_rate": attendance_rate,
            "leave_evolution": leave_evolution,
            "recent_activities": recent_activities
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques pour {email}: {str(e)}")
        # Renvoyer des données par défaut en cas d'erreur
        return {
            "employee": {
                "name": "Non disponible",
                "email": email,
                "department": "Non disponible",
                "position": "Non disponible"
            },
            "leave_stats": {"total": 0, "approved": 0, "pending": 0, "rejected": 0},
            "leave_balance": 0,
            "training_stats": {"total": 0, "sent": 0, "approved": 0, "rejected": 0},
            "attendance_rate": 0,
            "leave_evolution": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # Valeurs pour 12 mois
            "recent_activities": []
        }

@router.get("/api/employee/notifications/{email}")
async def get_employee_notifications(email: str, db: Session = Depends(get_db)):
    """
    Route API pour récupérer les notifications d'un employé.
    """
    try:
        # Utiliser la méthode du service pour récupérer les notifications
        return LeaveService.get_notifications(db, email)
    except Exception as e:
        # En cas d'erreur, retourner une liste vide
        print(f"Erreur lors de la récupération des notifications: {str(e)}")
        return []

@router.get("/api/employee/profile/{email}")
async def get_employee_profile(email: str, db: Session = Depends(get_db)):
    """
    Route API pour récupérer le profil d'un employé.
    """
    try:
        # Requête à la base de données
        employee = db.query(Employee).filter(Employee.email == email).first()
        
        if employee:
            return {
                "id": employee.id,
                "name": employee.name,
                "email": employee.email,
                "department": employee.department or "Non affecté",
                "role": employee.role or "Non défini"
            }
        return {"error": "Employé non trouvé"}
    except Exception as e:
        # En cas d'erreur, retourner un message d'erreur
        print(f"Erreur lors de la récupération du profil: {str(e)}")
        return {"error": f"Erreur de base de données: {str(e)}"}

@router.get("/employee-evaluations", response_class=HTMLResponse, name="employee_evaluations")
async def employee_evaluations_page(request: Request):
    """
    Route pour afficher la page des évaluations pour un employé.
    """
    return templates.TemplateResponse("employee_evaluations.html", {"request": request})

# Export du routeur pour intégration dans main.py
dashboard_employee_router = router
