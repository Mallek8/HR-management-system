"""
DashboardController - Gère la logique métier pour l'affichage du tableau de bord employé.

Responsabilités :
- Récupérer les données nécessaires à l'affichage du dashboard
- Gérer les erreurs (employé introuvable)
- Centraliser la logique d'accès aux données liées à l'employé

Design Pattern : 
- Controller (pattern MVC) : cette classe agit comme un contrôleur entre l'API et les services métiers.

Respect des principes SOLID :
- SRP (Single Responsibility Principle) : Une seule responsabilité : fournir les infos du dashboard.
- DIP (Dependency Inversion Principle) : Ne dépend que d’abstractions (services).
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.employee_service import EmployeeService


class DashboardController:
    @staticmethod
    def get_employee_dashboard(db: Session, email: str):
        """
        Retourne les informations d'un employé à partir de son email.

        Paramètres :
            db (Session) : Session SQLAlchemy pour la base de données.
            email (str)  : Adresse email de l'utilisateur (provenant du cookie de session).

        Retour :
            Employee : Instance de l'employé récupérée via le service métier.

        Exceptions :
            HTTPException 404 si l'employé n'est pas trouvé.
        """
        user = EmployeeService.get_employee_by_email(db, email)

        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable")

        return user
