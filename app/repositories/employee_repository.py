"""
employee_repository.py — Accès centralisé aux données liées aux employés.

Responsabilités :
- Fournit une couche d'abstraction entre la base de données et les services métier.
- Encapsule toutes les opérations CRUD sur le modèle Employee.

Design Patterns :
- Repository Pattern : isole la logique de persistance pour les entités Employee.

Respect des principes SOLID :
- SRP : Chaque méthode a une seule responsabilité (ex : récupérer, créer, supprimer).
- OCP : La classe peut être étendue sans être modifiée (ajout de nouvelles méthodes).
- DIP : Les services métiers dépendent de l’interface (Repository), pas de la base directement.
"""

from sqlalchemy.orm import Session
from app.models.employee import Employee
from typing import List, Optional


class EmployeeRepository:
    """
    Repository pour les opérations liées à la table des employés.
    Fournit une interface propre pour interagir avec les employés dans la base.
    """

    @staticmethod
    def get_all(db: Session) -> List[Employee]:
        """
        Récupère la liste de tous les employés.
        """
        return db.query(Employee).all()

    @staticmethod
    def get_by_id(db: Session, employee_id: int) -> Optional[Employee]:
        """
        Recherche un employé par son identifiant.
        """
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Employee]:
        """
        Recherche un employé à partir de son adresse e-mail.
        """
        return db.query(Employee).filter(Employee.email == email).first()

    @staticmethod
    def get_managers(db: Session) -> List[Employee]:
        """
        Récupère tous les employés ayant le rôle de 'superviseur'.
        """
        return db.query(Employee).filter(Employee.role == "superviseur").all()

    @staticmethod
    def get_team_by_department(db: Session, department: str) -> List[Employee]:
        """
        Récupère les employés travaillant dans un département donné.
        """
        return db.query(Employee).filter(Employee.department == department).all()

    @staticmethod
    def create(db: Session, employee: Employee) -> Employee:
        """
        Enregistre un nouvel employé dans la base.
        """
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee

    @staticmethod
    def update(db: Session, employee: Employee, data: dict) -> Employee:
        """
        Met à jour les champs d’un employé avec un dictionnaire de données.
        """
        for key, value in data.items():
            setattr(employee, key, value)
        db.commit()
        db.refresh(employee)
        return employee

    @staticmethod
    def delete(db: Session, employee: Employee) -> None:
        """
        Supprime définitivement un employé de la base de données.
        """
        db.delete(employee)
        db.commit()
