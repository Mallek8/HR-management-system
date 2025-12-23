from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.leave import Leave
from app.models.employee import Employee


class LeaveRequestService:
    """
    Service pour la gestion des demandes de congés.
    """
    
    @staticmethod
    def get_all_leave_requests(db: Session) -> List[Leave]:
        """
        Récupère toutes les demandes de congés.
        
        Args:
            db: Session de base de données
            
        Returns:
            Liste de toutes les demandes de congés
        """
        return db.query(Leave).all()
    
    @staticmethod
    def get_leave_request_by_id(db: Session, leave_id: int) -> Optional[Leave]:
        """
        Récupère une demande de congé par son ID.
        
        Args:
            db: Session de base de données
            leave_id: ID de la demande de congé
            
        Returns:
            La demande de congé si elle existe, sinon None
        """
        return db.query(Leave).filter(Leave.id == leave_id).first()
    
    @staticmethod
    def get_leave_requests_by_employee(db: Session, employee_id: int) -> List[Leave]:
        """
        Récupère toutes les demandes de congés d'un employé.
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé
            
        Returns:
            Liste des demandes de congés de l'employé
        """
        return db.query(Leave).filter(Leave.employee_id == employee_id).all()
    
    @staticmethod
    def get_pending_leave_requests(db: Session) -> List[Leave]:
        """
        Récupère toutes les demandes de congés en attente.
        
        Args:
            db: Session de base de données
            
        Returns:
            Liste des demandes de congés en attente
        """
        return db.query(Leave).filter(Leave.status == "en attente").all()
    
    @staticmethod
    def create_leave_request(
        db: Session, 
        employee_id: int, 
        start_date: datetime, 
        end_date: datetime, 
        leave_type: str
    ) -> Leave:
        """
        Crée une nouvelle demande de congé.
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé
            start_date: Date de début du congé
            end_date: Date de fin du congé
            leave_type: Type de congé
            
        Returns:
            La demande de congé créée
        """
        leave_request = Leave(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            type=leave_type,
            status="en attente",
            created_at=datetime.now()
        )
        db.add(leave_request)
        db.commit()
        db.refresh(leave_request)
        return leave_request
    
    @staticmethod
    def update_leave_request_status(db: Session, leave_id: int, status: str) -> Optional[Leave]:
        """
        Met à jour le statut d'une demande de congé.
        
        Args:
            db: Session de base de données
            leave_id: ID de la demande de congé
            status: Nouveau statut
            
        Returns:
            La demande de congé mise à jour si elle existe, sinon None
        """
        leave_request = LeaveRequestService.get_leave_request_by_id(db, leave_id)
        if not leave_request:
            return None
        
        leave_request.status = status
        db.commit()
        db.refresh(leave_request)
        return leave_request
    
    @staticmethod
    def get_notifications(db: Session, email: str) -> List[dict]:
        """
        Récupère les notifications d'un employé.
        
        Args:
            db: Session de base de données
            email: Email de l'employé
            
        Returns:
            Liste des notifications
        """
        employee = db.query(Employee).filter(Employee.email == email).first()
        if not employee:
            return []
        
        leave_requests = LeaveRequestService.get_leave_requests_by_employee(db, employee.id)
        notifications = []
        
        for leave in leave_requests:
            notification = {
                "id": leave.id,
                "created_at": leave.created_at.isoformat() if leave.created_at else None,
                "message": f"Votre demande de congé du {leave.start_date} au {leave.end_date} est {leave.status}.",
                "status": leave.status
            }
            notifications.append(notification)
        
        return notifications
        
    @staticmethod
    def get_team_leave_requests(db: Session, manager_id: int) -> List[Leave]:
        """
        Récupère toutes les demandes de congés des membres de l'équipe d'un manager.
        
        Args:
            db: Session de base de données
            manager_id: ID du manager
            
        Returns:
            Liste des demandes de congés des membres de l'équipe
        """
        # Récupérer le département du manager
        manager = db.query(Employee).filter(Employee.id == manager_id).first()
        if not manager or not manager.department_id:
            return []
        
        # Récupérer tous les employés du département
        team_members = db.query(Employee).filter(
            Employee.department_id == manager.department_id,
            Employee.id != manager_id  # Exclure le manager lui-même
        ).all()
        
        # Récupérer toutes les demandes de congés des membres de l'équipe
        team_members_ids = [member.id for member in team_members]
        if not team_members_ids:
            return []
            
        return db.query(Leave).filter(Leave.employee_id.in_(team_members_ids)).all()
    
    @staticmethod
    def get_employee_leave_requests(db: Session, employee_id: int) -> List[Leave]:
        """
        Récupère toutes les demandes de congés d'un employé.
        Alias pour get_leave_requests_by_employee pour une meilleure cohérence des noms.
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé
            
        Returns:
            Liste des demandes de congés de l'employé
        """
        return LeaveRequestService.get_leave_requests_by_employee(db, employee_id) 