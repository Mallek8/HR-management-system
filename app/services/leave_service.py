# app/services/leave_service.py
"""
    Service métier pour la gestion des demandes de congés.

    Applique les principes SRP et délègue la persistance aux repositories.
    
    """
from datetime import datetime, timedelta
from typing import List
from app.database import get_db

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.leave import Leave
from app.models.leave_balance import LeaveBalance
from app.models.employee import Employee
from app.models.notification import Notification

from app.repositories.leave_repository import LeaveRepository
from app.repositories.employee_repository import EmployeeRepository

from app.services.notification_service import NotificationService



class LeaveService:
    

    @staticmethod
    def request_leave(db: Session, employee_id: int, start_date: datetime, end_date: datetime) -> Leave:
        # Vérifier si l'employé existe
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employé non trouvé")

        # Vérifier si les dates sont valides
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="La date de début doit être antérieure à la date de fin")

        # Calculer le nombre de jours demandés
        days_requested = (end_date - start_date).days + 1
        if days_requested <= 0:
            raise HTTPException(status_code=400, detail="La durée du congé doit être positive")
            
        # Vérifier le solde
        balance = db.query(LeaveBalance).filter_by(employee_id=employee_id).first()
        
        # Si l'employé n'a pas de solde, créer un solde initial
        if not balance:
            balance = LeaveBalance(employee_id=employee_id, balance=20)  # Solde initial par défaut
            db.add(balance)
            db.commit()
        
        # Vérifier si le solde est suffisant
        if balance.balance < days_requested:
            raise HTTPException(status_code=400, detail=f"Solde insuffisant: {balance.balance} jours disponibles, {days_requested} demandés")

        # Vérifier le nombre de personnes déjà en congé pour ce département
        overlapping = db.query(Leave).join(Employee).filter(
            Employee.department == employee.department,
            Leave.status == "approuvé",
            Leave.start_date <= end_date,
            Leave.end_date >= start_date
        ).count()

        if overlapping >= 3:
            raise HTTPException(status_code=400, detail="Trop d'absences dans l'équipe")

        # Créer la demande de congé
        leave = Leave(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            status="en attente"
        )
        db.add(leave)
        db.commit()
        db.refresh(leave)

        # Envoyer une notification au superviseur si nécessaire
        if employee.supervisor_id:
            NotificationService.send_notification(
                db,
                employee.supervisor_id,
                f"Nouvelle demande de congé de {employee.name} du {start_date.date()} au {end_date.date()}"
            )

        return leave

    
    @staticmethod
    def approve_leave(db: Session, leave_id: int):
        """
        Approuver une demande de congé en utilisant le pattern State.
        """
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if not leave:
            raise HTTPException(status_code=404, detail="Demande introuvable")

        from app.states.leave_request.leave_context import LeaveContext
        
        # Créer le contexte avec la demande
        context = LeaveContext(leave)
        
        # Récupérer l'employé qui approuve (par simplicité, utilisons l'ID 1 comme administrateur)
        approver_id = 1
        
        # Approuver la demande via le pattern State
        result = context.approve(db, approver_id)
        
        # Si l'approbation a échoué, lever une exception
        if isinstance(result, dict) and not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Erreur lors de l'approbation"))
        
        # Recharger la demande depuis la BD (elle a été modifiée par l'état)
        db.refresh(leave)
        
        return leave

    @staticmethod
    def reject_leave(db: Session, leave_id: int, reason: str = None):
        """
        Rejeter une demande de congé en utilisant le pattern State.
        """
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if not leave:
            raise HTTPException(status_code=404, detail="Demande introuvable")

        from app.states.leave_request.leave_context import LeaveContext
        
        # Créer le contexte avec la demande
        context = LeaveContext(leave)
        
        # Récupérer l'employé qui rejette (par simplicité, utilisons l'ID 1 comme administrateur)
        rejecter_id = 1
        
        # Rejeter la demande via le pattern State
        result = context.reject(db, rejecter_id, reason)
        
        # Si le rejet a échoué, lever une exception
        if isinstance(result, dict) and not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Erreur lors du rejet"))
        
        # Recharger la demande depuis la BD (elle a été modifiée par l'état)
        db.refresh(leave)
        
        return leave

    @staticmethod
    def get_team_absences(db: Session, employee_id: int) -> List[dict]:
        employee = EmployeeRepository.get_by_id(db, employee_id)
        if not employee:
            return []

        leaves = db.query(Leave).join(Employee).filter(
            Employee.department == employee.department,
            Leave.status == "approuvé"
        ).all()

        return [
            {
                "employee_name": l.employee.name,
                "role": l.employee.role,
                "start_date": l.start_date.strftime("%Y-%m-%d"),
                "end_date": l.end_date.strftime("%Y-%m-%d")
            }
            for l in leaves
        ]

    @staticmethod
    def get_all_leaves_with_employee_info(db: Session) -> List[dict]:
        leaves = db.query(Leave).all()
        result = []
        for leave in leaves:
            employee = db.query(Employee).filter(Employee.id == leave.employee_id).first()
            result.append({
                "id": leave.id,
                "employee_name": employee.name,
                "start_date": leave.start_date,
                "end_date": leave.end_date,
                "status": leave.status,
                "leave_balance": getattr(employee, "leave_balance", 0)
            })
        return result

    

    @staticmethod
    def initialize_balances(db: Session = next(get_db())):
        """
        Initialise les soldes de congé pour les employés ne disposant pas encore de solde.
        """
        employees = db.query(Employee).all()
        for emp in employees:
            existing = db.query(LeaveBalance).filter_by(employee_id=emp.id).first()
            if not existing:
                db.add(LeaveBalance(employee_id=emp.id, balance=20))  # ou 30 selon ton besoin
        db.commit()

    @staticmethod
    def get_notifications(db: Session, user_email: str):
        """
        Récupère les notifications pour un utilisateur donné basées sur ses congés approuvés ou refusés.
        """
        try:
            # Récupérer l'employé par son email
            employee = db.query(Employee).filter(Employee.email == user_email).first()
            if not employee:
                return []

            # Récupérer les congés approuvés ou refusés de l'employé
            leaves = db.query(Leave).filter(
                Leave.employee_id == employee.id,
                Leave.status.in_(["approuvé", "refusé"])  # Filtrer par statut
            ).order_by(Leave.start_date.desc()).all()

            notifications = []
            for leave in leaves:
                message = ""
                if leave.status == "approuvé":
                    message = f"Votre demande de congé du {leave.start_date.strftime('%Y-%m-%d')} au {leave.end_date.strftime('%Y-%m-%d')} a été approuvée."
                else:
                    message = f"Votre demande de congé du {leave.start_date.strftime('%Y-%m-%d')} au {leave.end_date.strftime('%Y-%m-%d')} a été refusée."

                notifications.append({
                    "id": leave.id,
                    "message": message,
                    "created_at": leave.start_date.isoformat(),
                    "status": leave.status,
                    "type": leave.type
                })

            return notifications

        except Exception as e:
            print(f"Erreur lors de la récupération des notifications: {str(e)}")
            return []
    
    @staticmethod
    def get_leave_requests_for_supervisor(db: Session, user_email: str):
        """
        Récupère toutes les demandes de congé envoyées à un superviseur par l'administrateur.
        Les demandes doivent être en statut "en attente" et sont filtrées par le superviseur.
        """
        supervisor = db.query(Employee).filter(Employee.email == user_email).first()
        if not supervisor:
            raise HTTPException(status_code=404, detail="Superviseur non trouvé")

        # Filtrer les demandes de congé envoyées par l'administrateur pour le superviseur.
        leave_requests = db.query(Leave).filter(
            Leave.status == "en attente", 
            Leave.admin_approved == True,  # La demande a été envoyée à l'administrateur.
            Leave.supervisor_id == supervisor.id  # Filtrer par superviseur si nécessaire.
        ).all()

        return leave_requests
    @staticmethod
    def get_employees_on_leave(db: Session, supervisor_email: str):
     """
     Récupère les employés actuellement en congé sous la supervision d'un superviseur.
     """
     # Récupérer le superviseur à partir de son email
     supervisor = db.query(Employee).filter(Employee.email == supervisor_email).first()
     if not supervisor:
        raise HTTPException(status_code=404, detail="Superviseur non trouvé")

     # Récupérer les employés en congé supervisés par ce superviseur
     employees_on_leave = db.query(Leave).join(
        Employee, Leave.employee_id == Employee.id  # Clause explicite pour la jointure
     ).filter(
        Leave.status == "approuvé",
        Employee.supervisor_id == supervisor.id
     ).all()

     # Retourner les informations des employés en congé
     return [
        {
            "employee_name": leave.employee.name,
            "start_date": leave.start_date.strftime("%Y-%m-%d"),
            "end_date": leave.end_date.strftime("%Y-%m-%d"),
            "status": leave.status
        }
        for leave in employees_on_leave
     ]
    def delete_employee(db: Session, employee_id: int):
     try:
        # Réattribuer employee_id à NULL dans leave_balances avant la suppression
        leave_balances = db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee_id).all()
        
        for leave_balance in leave_balances:
            leave_balance.employee_id = None  # Réattribuer l'ID à NULL
            db.add(leave_balance)  # Ajout des changements à la session
        
        # Supprimer l'employé après avoir réattribué les valeurs à NULL
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            db.delete(employee)
            db.commit()
            return {"detail": f"Employee with ID {employee_id} deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail="Employee not found")
     except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting employee: {str(e)}")

    @staticmethod
    def send_to_supervisor(db: Session, leave_id: int):
        """
        Transférer une demande de congé au superviseur en utilisant le pattern State.
        """
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if not leave:
            raise HTTPException(status_code=404, detail="Demande introuvable")

        from app.states.leave_request.leave_context import LeaveContext
        
        # Créer le contexte avec la demande
        context = LeaveContext(leave)
        
        # Utiliser une méthode plus générique qui pourrait exister dans le contexte
        # Dans un cas réel, on utiliserait une méthode spécifique du contexte
        try:
            # Simuler le transfert
            leave.supervisor_id = db.query(Employee).filter(Employee.id == leave.employee_id).first().supervisor_id
            leave.admin_approved = True
            db.commit()
            
            return {"success": True, "message": "Demande transférée au superviseur"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_leave_stats_for_employee(db: Session, employee_id: int) -> dict:
        """
        Récupère les statistiques de congé pour un employé
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé
            
        Returns:
            dict: Statistiques de congé (total, approuvé, en attente, refusé)
        """
        try:
            leaves = db.query(Leave).filter(Leave.employee_id == employee_id).all()
            
            # Initialisation des compteurs
            total = len(leaves)
            approved = 0
            pending = 0
            rejected = 0
            
            # Comptage par statut
            for leave in leaves:
                if leave.status == "approuvé":
                    approved += 1
                elif leave.status == "en attente":
                    pending += 1
                elif leave.status == "refusé":
                    rejected += 1
            
            return {
                "total": total,
                "approved": approved,
                "pending": pending,
                "rejected": rejected
            }
            
        except Exception as e:
            db.rollback()
            import logging
            logging.error(f"Erreur lors de la récupération des statistiques de congé: {str(e)}")
            
            return {
                "total": 0,
                "approved": 0,
                "pending": 0,
                "rejected": 0
            }
    
    @staticmethod
    def get_leave_balance(db: Session, employee_id: int) -> dict:
        """
        Récupère le solde de congé d'un employé
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé
            
        Returns:
            dict: Soldes de congés (payé, maladie)
        """
        try:
            balance = db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee_id).first()
            
            if not balance:
                # Créer un solde par défaut si aucun n'existe
                balance = LeaveBalance(employee_id=employee_id, balance=20, sick_leave_balance=10)
                db.add(balance)
                db.commit()
                db.refresh(balance)
            
            return {
                "paid_leave_balance": balance.balance,
                "sick_leave_balance": getattr(balance, "sick_leave_balance", 10)
            }
            
        except Exception as e:
            db.rollback()
            import logging
            logging.error(f"Erreur lors de la récupération du solde de congé: {str(e)}")
            
            return {
                "paid_leave_balance": 0,
                "sick_leave_balance": 0
            }
    
    @staticmethod
    def get_leave_evolution_for_employee(db: Session, employee_id: int, year: int = None) -> list:
        """
        Récupère l'évolution des congés d'un employé sur une année
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé
            year: Année concernée (année courante par défaut)
            
        Returns:
            list: Nombre de jours de congé par mois [jan, fév, ..., déc]
        """
        if year is None:
            year = datetime.now().year
        
        try:
            # Récupérer tous les congés approuvés pour l'employé dans l'année spécifiée
            leaves = db.query(Leave).filter(
                Leave.employee_id == employee_id,
                Leave.status == "approuvé"
            ).all()
            
            # Initialiser le tableau de résultats: un élément par mois (0-indexé)
            months = [0] * 12
            
            for leave in leaves:
                # Pour chaque congé approuvé, compter les jours par mois
                if leave.start_date.year <= year <= leave.end_date.year:
                    current_date = max(leave.start_date, datetime(year, 1, 1))
                    end_date = min(leave.end_date, datetime(year, 12, 31))
                    
                    # Parcourir tous les jours du congé
                    while current_date <= end_date:
                        # Incrémenter le compteur pour le mois correspondant (0-indexé)
                        month_index = current_date.month - 1
                        months[month_index] += 1
                        current_date += timedelta(days=1)
            
            return months
            
        except Exception as e:
            db.rollback()
            import logging
            logging.error(f"Erreur lors de la récupération de l'évolution des congés: {str(e)}")
            
            return [0] * 12

    @staticmethod
    def cancel_leave(db: Session, leave_id: int, employee_id: int = None, reason: str = None):
        """
        Annuler une demande de congé en utilisant le pattern State.
        """
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if not leave:
            raise HTTPException(status_code=404, detail="Demande introuvable")

        from app.states.leave_request.leave_context import LeaveContext
        
        # Créer le contexte avec la demande
        context = LeaveContext(leave)
        
        # Si employee_id n'est pas spécifié, utiliser l'ID de l'employé qui a fait la demande
        canceller_id = employee_id or leave.employee_id
        
        # Annuler la demande via le pattern State
        result = context.cancel(db, canceller_id, reason)
        
        # Si l'annulation a échoué, lever une exception
        if isinstance(result, dict) and not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Erreur lors de l'annulation"))
        
        # Recharger la demande depuis la BD (elle a été modifiée par l'état)
        db.refresh(leave)
        
        return leave

class LeaveWorkflowFacade:
    """
    Façade pour gérer les workflows liés aux demandes de congés.
    
    Cette classe simplifie les interactions entre les différents acteurs
    (employés, superviseurs, administrateurs) et les demandes de congés.
    
    Design Pattern: Façade (Facade)
    Masque la complexité des interactions entre les services et simplifie
    l'interface pour les controlleurs.
    """
    
    @staticmethod
    def approve_by_admin(db: Session, leave_id: int) -> dict:
        """
        Approuve une demande de congé par l'administrateur.
        
        Args:
            db: Session de base de données
            leave_id: ID de la demande de congé à approuver
            
        Returns:
            Un dictionnaire avec le message de confirmation
        """
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if not leave:
            raise HTTPException(status_code=404, detail="Demande de congé introuvable")
            
        employee = db.query(Employee).filter(Employee.id == leave.employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
            
        leave.status = "approuvé"
        db.commit()
        db.refresh(leave)
        
        # Notification à l'employé
        NotificationService.send_notification(
            db, 
            employee.id, 
            f"Votre demande de congé du {leave.start_date} au {leave.end_date} a été approuvée par l'administrateur."
        )
        
        return {"message": "Demande approuvée par l'administrateur.", "leave_id": leave.id}
        
    @staticmethod
    def reject_by_admin(db: Session, leave_id: int) -> dict:
        """
        Rejette une demande de congé par l'administrateur.
        
        Args:
            db: Session de base de données
            leave_id: ID de la demande de congé à rejeter
            
        Returns:
            Un dictionnaire avec le message de confirmation
        """
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if not leave:
            raise HTTPException(status_code=404, detail="Demande de congé introuvable")
            
        employee = db.query(Employee).filter(Employee.id == leave.employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
            
        leave.status = "refusé"
        db.commit()
        db.refresh(leave)
        
        # Notification à l'employé
        NotificationService.send_notification(
            db, 
            employee.id, 
            f"Votre demande de congé du {leave.start_date} au {leave.end_date} a été refusée par l'administrateur."
        )
        
        return {"message": "Demande refusée par l'administrateur.", "leave_id": leave.id}
        
    @staticmethod
    def forward_to_supervisor(db: Session, leave_id: int) -> dict:
        """
        Transmets une demande de congé au superviseur pour approbation.
        
        Args:
            db: Session de base de données
            leave_id: ID de la demande de congé à transmettre
            
        Returns:
            Un dictionnaire avec le message de confirmation
        """
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if not leave:
            raise HTTPException(status_code=404, detail="Demande de congé introuvable")
            
        employee = db.query(Employee).filter(Employee.id == leave.employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
            
        if not employee.supervisor_id:
            raise HTTPException(status_code=400, detail="Cet employé n'a pas de superviseur assigné")
            
        leave.status = "en attente sup"
        leave.supervisor_id = employee.supervisor_id
        db.commit()
        db.refresh(leave)
        
        # Notification au superviseur
        NotificationService.send_notification(
            db, 
            employee.supervisor_id, 
            f"Une demande de congé de {employee.name} du {leave.start_date} au {leave.end_date} nécessite votre approbation."
        )
        
        return {"message": "Demande transmise au superviseur.", "leave_id": leave.id}
        
    @staticmethod
    def approve_by_supervisor(db: Session, supervisor_email: str, leave_id: int) -> dict:
        """
        Approuve une demande de congé par le superviseur.
        
        Args:
            db: Session de base de données
            supervisor_email: Email du superviseur
            leave_id: ID de la demande de congé à approuver
            
        Returns:
            Un dictionnaire avec le message de confirmation
        """
        # Vérifier le superviseur
        supervisor = db.query(Employee).filter(Employee.email == supervisor_email).first()
        if not supervisor:
            raise HTTPException(status_code=404, detail="Superviseur non trouvé")
            
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if not leave:
            raise HTTPException(status_code=404, detail="Demande de congé introuvable")
            
        # Vérifier que le superviseur est bien le superviseur assigné à cette demande
        if leave.supervisor_id != supervisor.id:
            raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à approuver cette demande")
            
        employee = db.query(Employee).filter(Employee.id == leave.employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
            
        leave.status = "approuvé"
        db.commit()
        db.refresh(leave)
        
        # Notification à l'employé
        NotificationService.send_notification(
            db, 
            employee.id, 
            f"Votre demande de congé du {leave.start_date} au {leave.end_date} a été approuvée par votre superviseur."
        )
        
        # Notification à l'administrateur
        NotificationService.send_notification_to_admin(
            db,
            f"Demande de congé de {employee.name} approuvée par {supervisor.name}"
        )
        
        return {"message": "Demande approuvée par le superviseur.", "leave_id": leave.id}
        
    @staticmethod
    def reject_by_supervisor(db: Session, supervisor_email: str, leave_id: int) -> dict:
        """
        Rejette une demande de congé par le superviseur.
        
        Args:
            db: Session de base de données
            supervisor_email: Email du superviseur
            leave_id: ID de la demande de congé à rejeter
            
        Returns:
            Un dictionnaire avec le message de confirmation
        """
        # Vérifier le superviseur
        supervisor = db.query(Employee).filter(Employee.email == supervisor_email).first()
        if not supervisor:
            raise HTTPException(status_code=404, detail="Superviseur non trouvé")
            
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if not leave:
            raise HTTPException(status_code=404, detail="Demande de congé introuvable")
            
        # Vérifier que le superviseur est bien le superviseur assigné à cette demande
        if leave.supervisor_id != supervisor.id:
            raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à rejeter cette demande")
            
        employee = db.query(Employee).filter(Employee.id == leave.employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
            
        leave.status = "refusé"
        db.commit()
        db.refresh(leave)
        
        # Notification à l'employé
        NotificationService.send_notification(
            db, 
            employee.id, 
            f"Votre demande de congé du {leave.start_date} au {leave.end_date} a été refusée par votre superviseur."
        )
        
        # Notification à l'administrateur
        NotificationService.send_notification_to_admin(
            db,
            f"Demande de congé de {employee.name} refusée par {supervisor.name}"
        )
        
        return {"message": "Demande refusée par le superviseur.", "leave_id": leave.id}