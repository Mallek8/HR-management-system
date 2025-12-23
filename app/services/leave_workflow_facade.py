"""
LeaveWorkflowFacade
--------------------

Ce fichier applique le pattern Facade pour encapsuler les opérations métier
liées aux demandes de congés.

Responsabilités :
- Approbation par l'admin
- Rejet par l'admin
- Transmission au superviseur
- Approbation par le superviseur
- Rejet par le superviseur

Dépendances :
- LeaveRepository
- EmployeeRepository
- NotificationService
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.leave import Leave
from app.repositories.leave_repository import LeaveRepository
from app.repositories.employee_repository import EmployeeRepository
from app.services.notification_service import NotificationService


class LeaveWorkflowFacade:

    @staticmethod
    def approve_by_admin(db: Session, leave_id: int):
        leave = LeaveRepository.get_by_id(db, leave_id)
        if not leave:
            raise HTTPException(status_code=404, detail="Demande non trouvée")

        leave.status = "approuvé"
        db.commit()

        NotificationService.send_notification(
            db,
            leave.employee_id,
            f"Votre congé du {leave.start_date} au {leave.end_date} a été approuvé par l'administration."
        )
        return {"message": "Demande approuvée par l'administrateur."}

    @staticmethod
    def reject_by_admin(db: Session, leave_id: int):
        leave = LeaveRepository.get_by_id(db, leave_id)
        if not leave:
            raise HTTPException(status_code=404, detail="Demande non trouvée")

        leave.status = "refusé"
        db.commit()

        NotificationService.send_notification(
            db,
            leave.employee_id,
            f"Votre congé du {leave.start_date} au {leave.end_date} a été refusé par l'administration."
        )
        return {"message": "Demande refusée par l'administrateur."}

    @staticmethod
    def forward_to_supervisor(db: Session, leave_id: int):
        leave = LeaveRepository.get_by_id(db, leave_id)
        if not leave:
            raise HTTPException(status_code=404, detail="Demande non trouvée")

        employee = EmployeeRepository.get_by_id(db, leave.employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employé non trouvé")

        if not employee.supervisor_id:
            raise HTTPException(status_code=400, detail="Aucun superviseur assigné à l'employé")

        leave.status = "en attente sup"
        leave.supervisor_id = employee.supervisor_id
        leave.admin_approved = True
        db.commit()

        NotificationService.send_notification(
            db,
            employee.supervisor_id,
            f"Nouvelle demande de congé à valider pour {employee.name}."
        )
        return {"message": "Demande transmise au superviseur."}

    @staticmethod
    def approve_by_supervisor(db: Session, supervisor_email: str, leave_id: int):
        supervisor = EmployeeRepository.get_by_email(db, supervisor_email)
        if not supervisor:
            raise HTTPException(status_code=404, detail="Superviseur non trouvé")

        leave = db.query(Leave).filter(
            Leave.id == leave_id,
            Leave.supervisor_id == supervisor.id,
            Leave.status == "en attente sup"
        ).first()

        if not leave:
            raise HTTPException(status_code=404, detail="Demande non autorisée ou non trouvée")

        leave.status = "approuvé"
        db.commit()

        NotificationService.send_notification(
            db,
            leave.employee_id,
            f"Votre congé du {leave.start_date} au {leave.end_date} a été validé par votre superviseur."
        )
        
        # Notifier également l'administrateur
        NotificationService.send_notification_to_admin(
            db,
            f"Congé approuvé par le superviseur {supervisor.name} pour la période du {leave.start_date} au {leave.end_date}."
        )
        
        return {"message": "Demande approuvée par le superviseur."}

    @staticmethod
    def reject_by_supervisor(db: Session, supervisor_email: str, leave_id: int):
        supervisor = EmployeeRepository.get_by_email(db, supervisor_email)
        if not supervisor:
            raise HTTPException(status_code=404, detail="Superviseur non trouvé")

        leave = db.query(Leave).filter(
            Leave.id == leave_id,
            Leave.supervisor_id == supervisor.id,
            Leave.status == "en attente sup"
        ).first()

        if not leave:
            raise HTTPException(status_code=404, detail="Demande non autorisée ou non trouvée")

        leave.status = "refusé"
        db.commit()

        NotificationService.send_notification(
            db,
            leave.employee_id,
            f"Votre congé du {leave.start_date} au {leave.end_date} a été refusé par votre superviseur."
        )
        
        # Notifier également l'administrateur
        NotificationService.send_notification_to_admin(
            db,
            f"Congé refusé par le superviseur {supervisor.name} pour la période du {leave.start_date} au {leave.end_date}."
        )
        
        return {"message": "Demande refusée par le superviseur."}
