"""
leave_repository.py — Accès centralisé aux opérations sur les congés (Leave).

Responsabilités :
- Encapsule toute la logique d'accès et de manipulation des congés en base.
- Fournit des méthodes spécifiques aux cas d'usage métiers (création, validation, suppression…).

Design Patterns :
- Repository Pattern : isole la persistance des données et facilite la maintenance/testabilité.

Respect des principes SOLID :
- SRP : une méthode = une responsabilité métier.
- DIP : les services utilisent cette interface pour rester découplés de SQLAlchemy.
"""

from sqlalchemy.orm import Session
from app.models.leave import Leave
from app.models.employee import Employee
from datetime import datetime, timedelta, date
from typing import List, Optional


class LeaveRepository:
    """
    Classe responsable de toutes les opérations liées aux congés.
    """

    @staticmethod
    def create(db: Session, leave_data) -> Leave:
        """
        Crée une nouvelle demande de congé à partir d'un schéma ou d'un DTO.
        """
        leave = Leave(
            employee_id=leave_data.employee_id,
            start_date=leave_data.start_date,
            end_date=leave_data.end_date,
            status="en attente",
            admin_approved=False
        )
        db.add(leave)
        db.commit()
        db.refresh(leave)
        return leave

    @staticmethod
    def get_by_id(db: Session, leave_id: int) -> Optional[Leave]:
        """
        Récupère une demande de congé par son identifiant.
        """
        return db.query(Leave).filter(Leave.id == leave_id).first()

    @staticmethod
    def get_all(db: Session) -> List[Leave]:
        """
        Retourne toutes les demandes de congé.
        """
        return db.query(Leave).all()

    @staticmethod
    def get_approved(db: Session) -> List[Leave]:
        """
        Retourne toutes les demandes approuvées.
        """
        return db.query(Leave).filter(Leave.status == "approuvé").all()

    @staticmethod
    def update_status(db: Session, leave_id: int, status: str) -> Optional[Leave]:
        """
        Met à jour le statut d'une demande.
        """
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if leave:
            leave.status = status
            db.commit()
            db.refresh(leave)
        return leave

    @staticmethod
    def delete(db: Session, leave_id: int) -> bool:
        """
        Supprime une demande de congé de la base.
        """
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if leave:
            db.delete(leave)
            db.commit()
            return True
        return False

    @staticmethod
    def delete_employee_leaves(db: Session, employee_id: int) -> bool:
        """
        Supprime toutes les demandes de congé d'un employé.
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé dont les congés doivent être supprimés
            
        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        try:
            # Récupérer toutes les demandes de congé de l'employé
            leaves = db.query(Leave).filter(Leave.employee_id == employee_id).all()
            
            # Supprimer chaque demande
            for leave in leaves:
                db.delete(leave)
            
            # Valider les changements
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"ERREUR delete_employee_leaves: {e}")
            return False

    @staticmethod
    def create_test_leave(db: Session) -> Leave:
        """
        Crée un congé de test pour développement ou démonstration.
        """
        try:
            print("Début création congé de test")

            employee = db.query(Employee).first()
            if not employee:
                raise ValueError("Aucun employé trouvé pour créer un congé de test")

            start_date = date.today() + timedelta(days=1)
            end_date = start_date + timedelta(days=2)

            leave = Leave(
                employee_id=employee.id,
                start_date=start_date,
                end_date=end_date,
                status="en attente",
                supervisor_comment="Congé de test pour débogage"
            )

            db.add(leave)
            db.commit()
            db.refresh(leave)

            print(f"Congé de test créé : ID={leave.id}")
            return leave

        except Exception as e:
            db.rollback()
            print(f"ERREUR create_test_leave: {e}")
            import traceback
            print(traceback.format_exc())
            raise e
