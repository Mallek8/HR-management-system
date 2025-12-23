# app/services/notification_service.py

"""
NotificationService - Service de gestion des notifications RH

Ce service permet :
- D'envoyer des notifications à un employé ou à l'admin
- De récupérer les notifications simulées (pour développement ou fallback)

Respecte les principes SOLID (SRP) et utilise le pattern "Service".
"""

from datetime import datetime, UTC, timedelta
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.employee import Employee
from app.models.leave import Leave
from app.models.evaluation import Evaluation
from typing import Optional, Dict, List
import logging
from sqlalchemy.exc import SQLAlchemyError
from app.schemas import NotificationCreate, NotificationUpdate


class NotificationService:
    @staticmethod
    def send_notification(db: Session, employee_id: int, message: str):
        """Crée et enregistre une notification pour un employé spécifique."""
        notif = Notification(
            employee_id=employee_id,
            message=message,
            created_at=datetime.now(UTC)
        )
        db.add(notif)
        db.commit()

    @staticmethod
    def send_notification_to_admin(db: Session, message: str):
        """Envoie une notification à l'administrateur (premier trouvé)."""
        admin = db.query(Employee).filter(Employee.role == "admin").first()
        if not admin:
            return
        notif = Notification(
            employee_id=admin.id,
            message=message,
            created_at=datetime.now(UTC)
        )
        db.add(notif)
        db.commit()

    @staticmethod
    def get_admin_notifications():
        """Retourne des notifications fictives pour l'admin (pour tests ou fallback)."""
        return [
            {"id": 1, "message": "Nouvelle demande de congé"},
            {"id": 2, "message": "Un employé a été ajouté"},
        ]

    @staticmethod
    def get_general_notifications():
        """Retourne des notifications fictives générales."""
        return [
            {"id": 1, "message": "New leave request"},
            {"id": 2, "message": "Employee added"},
        ]

    @staticmethod
    def create_notification(db: Session, recipient_id: int, message: str, notification_type: str = "INFO", reference_id: Optional[int] = None) -> Optional[Notification]:
        """
        Crée une nouvelle notification pour un employé.
        
        Args:
            db: Session de base de données
            recipient_id: ID de l'employé destinataire
            message: Contenu de la notification
            notification_type: Type de notification
            reference_id: ID de référence optionnel (ex: ID d'une demande de congé)
            
        Returns:
            Notification: L'objet notification créé ou None en cas d'erreur
        """
        try:
            notification = Notification(
                employee_id=recipient_id,
                message=message,
                type=notification_type,
                reference_id=reference_id,
                is_read=False,
                created_at=datetime.now(UTC)
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            return notification
        except Exception as e:
            db.rollback()
            print(f"Error creating notification: {str(e)}")
            return None

    @staticmethod
    def create_notification_for_role(db: Session, role: str, message: str, link: Optional[str] = None,
                                  title: Optional[str] = None, notification_type: str = "INFO") -> Dict:
        """
        Crée une notification pour tous les employés ayant un rôle spécifique.
        
        Args:
            db: Session de base de données
            role: Rôle des employés destinataires
            message: Contenu de la notification
            link: Lien optionnel associé à la notification
            title: Titre optionnel de la notification
            notification_type: Type de notification (INFO, WARNING, SUCCESS, ERROR)
            
        Returns:
            Dict: Dictionnaire contenant le succès de l'opération et un message
        """
        try:
            employees = db.query(Employee).filter(Employee.role == role).all()
            for employee in employees:
                notification = Notification(
                    employee_id=employee.id,
                    message=message,
                    link=link,
                    title=title,
                    type=notification_type,
                    is_read=False,
                    created_at=datetime.now(UTC)
                )
                db.add(notification)
            db.commit()
            return {"success": True, "message": f"Notifications créées pour {len(employees)} employés avec le rôle {role}"}
        except Exception as e:
            db.rollback()
            print(f"Error creating notifications for role: {str(e)}")
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_notifications_for_employee(db: Session, employee_id: int, limit: int = 10) -> List[Notification]:
        """
        Récupère toutes les notifications pour un employé donné
        """
        try:
            notifications = db.query(Notification).filter(
                Notification.employee_id == employee_id
            ).order_by(Notification.created_at.desc()).limit(limit).all()
            
            return notifications
        except Exception as e:
            db.rollback()
            logging.error(f"Erreur lors de la récupération des notifications: {e}")
            return []

    @staticmethod
    def mark_notification_as_read(db: Session, notification_id: int) -> bool:
        """
        Marque une notification comme lue
        """
        try:
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            if notification:
                notification.is_read = True
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logging.error(f"Erreur lors du marquage de la notification: {e}")
            return False

    @staticmethod
    def get_recent_activities_for_employee(db: Session, employee_id: int) -> List[Dict]:
        """
        Récupère les activités récentes d'un employé (congés, évaluations, etc.)
        
        Args:
            db: Session de base de données
            employee_id: Identifiant de l'employé
            
        Returns:
            List[Dict]: Liste des activités récentes formatées
        """
        try:
            # Définir la date limite (30 derniers jours)
            limit_date = datetime.now() - timedelta(days=30)
            activities = []
            
            # Récupérer les demandes de congé récentes
            leaves = db.query(Leave).filter(
                Leave.employee_id == employee_id,
                Leave.created_at >= limit_date
            ).order_by(Leave.created_at.desc()).limit(5).all()
            
            for leave in leaves:
                # Formatage de la date
                time_ago = NotificationService.format_time_ago(leave.created_at)
                
                # Type d'activité et couleur en fonction du statut
                if leave.status == 'approuvé':
                    activity_type = "leave_approved"
                    title = "Congé approuvé"
                    icon = "check-circle"
                    color = "success"
                elif leave.status == 'en attente':
                    activity_type = "leave_requested"
                    title = "Congé demandé"
                    icon = "hourglass-split"
                    color = "warning"
                elif leave.status == 'refusé':
                    activity_type = "leave_rejected"
                    title = "Congé refusé"
                    icon = "x-circle"
                    color = "danger"
                else:
                    activity_type = "leave_status_changed"
                    title = "Statut de congé modifié"
                    icon = "arrow-clockwise"
                    color = "info"
                
                # Formatage des dates de congé
                start_date = leave.start_date.strftime('%d/%m/%Y')
                end_date = leave.end_date.strftime('%d/%m/%Y')
                
                # Message de l'activité
                if leave.status == 'approuvé':
                    message = f"Votre demande de congé du {start_date} au {end_date} a été approuvée."
                elif leave.status == 'en attente':
                    message = f"Vous avez soumis une demande de congé du {start_date} au {end_date}."
                elif leave.status == 'refusé':
                    message = f"Votre demande de congé du {start_date} au {end_date} a été refusée."
                else:
                    message = f"Le statut de votre congé du {start_date} au {end_date} a été mis à jour."
                
                # Ajouter l'activité à la liste
                activities.append({
                    "type": activity_type,
                    "title": title,
                    "time": time_ago,
                    "message": message,
                    "icon": icon,
                    "color": color
                })
            
            # Récupérer les évaluations récentes
            evaluations = db.query(Evaluation).filter(
                Evaluation.employee_id == employee_id,
                Evaluation.created_at >= limit_date
            ).order_by(Evaluation.created_at.desc()).limit(3).all()
            
            for evaluation in evaluations:
                time_ago = NotificationService.format_time_ago(evaluation.created_at)
                activities.append({
                    "type": "evaluation_received",
                    "title": "Évaluation reçue",
                    "time": time_ago,
                    "message": f"Vous avez reçu une évaluation avec un score de {evaluation.score}/100.",
                    "icon": "clipboard-check",
                    "color": "primary"
                })
            
            # Trier les activités par date (les plus récentes en premier)
            activities.sort(key=lambda x: NotificationService.parse_time_ago(x["time"]), reverse=True)
            
            return activities[:5]  # Limiter à 5 activités maximum
            
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des activités pour l'employé {employee_id}: {str(e)}")
            return []
    
    @staticmethod
    def format_time_ago(date: datetime) -> str:
        """
        Formate une date en "il y a X temps"
        """
        now = datetime.now()
        diff = now - date
        
        if diff.days > 30:
            return f"Il y a {diff.days // 30} mois"
        elif diff.days > 0:
            return f"Il y a {diff.days} jours"
        elif diff.seconds >= 3600:
            return f"Il y a {diff.seconds // 3600} heures"
        elif diff.seconds >= 60:
            return f"Il y a {diff.seconds // 60} minutes"
        else:
            return "À l'instant"
    
    @staticmethod
    def parse_time_ago(time_ago: str) -> timedelta:
        """
        Convertit une chaîne "il y a X temps" en un objet timedelta pour le tri
        """
        if "mois" in time_ago:
            months = int(time_ago.split(" ")[2])
            return timedelta(days=months * 30)
        elif "jours" in time_ago:
            days = int(time_ago.split(" ")[2])
            return timedelta(days=days)
        elif "heures" in time_ago:
            hours = int(time_ago.split(" ")[2])
            return timedelta(hours=hours)
        elif "minutes" in time_ago:
            minutes = int(time_ago.split(" ")[2])
            return timedelta(minutes=minutes)
        else:
            return timedelta(0)

    @staticmethod
    def get_notifications(db: Session) -> List[Notification]:
        """
        Récupère toutes les notifications
        """
        try:
            return db.query(Notification).all()
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la récupération des notifications: {e}")
            return []

    @staticmethod
    def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
        """
        Récupère une notification par son ID
        """
        try:
            return db.query(Notification).filter(Notification.id == notification_id).first()
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la récupération de la notification {notification_id}: {e}")
            return None

    @staticmethod
    def update_notification(db: Session, notification_id: int, notification_data: NotificationUpdate) -> Optional[Notification]:
        """
        Met à jour une notification existante
        """
        try:
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            if not notification:
                return None
                
            data = notification_data.dict(exclude_unset=True)
            for key, value in data.items():
                setattr(notification, key, value)
                
            db.commit()
            return notification
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la mise à jour de la notification {notification_id}: {e}")
            return None

    @staticmethod
    def delete_notification(db: Session, notification_id: int) -> bool:
        """
        Supprime une notification
        """
        try:
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            if not notification:
                return False
                
            db.delete(notification)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la suppression de la notification {notification_id}: {e}")
            return False

    @staticmethod
    def mark_as_read(db: Session, notification_id: int) -> bool:
        """
        Marque une notification comme lue
        """
        try:
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            if not notification:
                return False
                
            notification.is_read = True
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors du marquage de la notification {notification_id}: {e}")
            return False

    @staticmethod
    def get_unread_count(db: Session, employee_id: int) -> int:
        """
        Récupère le nombre de notifications non lues pour un employé
        """
        try:
            return db.query(Notification).filter(
                Notification.employee_id == employee_id,
                Notification.is_read == False
            ).count()
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors du comptage des notifications non lues: {e}")
            return 0

    @staticmethod
    def get_unread_notifications_count(db: Session, employee_id: int) -> int:
        """
        Récupère le nombre de notifications non lues pour un employé
        """
        try:
            return db.query(Notification).filter(
                Notification.employee_id == employee_id,
                Notification.is_read == False
            ).count()
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors du comptage des notifications non lues: {e}")
            return 0

    @staticmethod
    def get_unread_notifications_for_employee(db: Session, employee_id: int) -> List[Notification]:
        """
        Récupère les notifications non lues pour un employé
        """
        try:
            return db.query(Notification).filter(
                Notification.employee_id == employee_id,
                Notification.is_read == False
            ).order_by(Notification.created_at.desc()).all()
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la récupération des notifications non lues: {e}")
            return []

    @staticmethod
    def mark_all_as_read(db: Session, employee_id: int) -> bool:
        """
        Marque toutes les notifications d'un employé comme lues
        """
        try:
            notifications = db.query(Notification).filter(
                Notification.employee_id == employee_id,
                Notification.is_read == False
            ).all()
            
            for notification in notifications:
                notification.is_read = True
                
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors du marquage de toutes les notifications: {e}")
            return False

    @staticmethod
    def mark_all_as_read_for_employee(db: Session, employee_id: int) -> bool:
        """
        Marque toutes les notifications d'un employé comme lues
        """
        try:
            notifications = db.query(Notification).filter(
                Notification.employee_id == employee_id
            ).all()
            
            for notification in notifications:
                notification.is_read = True
                
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors du marquage de toutes les notifications: {e}")
            return False

    @staticmethod
    def notify_leave_request(db: Session, employee_id: int, start_date: str, end_date: str) -> None:
        """
        Envoie une notification au superviseur concernant une demande de congé
        """
        try:
            # Récupérer l'employé pour obtenir son superviseur
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            if not employee or not employee.supervisor_id:
                return
                
            # Créer la notification
            NotificationService.create_notification(
                db=db,
                recipient_id=employee.supervisor_id,
                message=f"Nouvelle demande de congé de {employee.name} du {start_date} au {end_date}",
                notification_type="leave_request"
            )
        except Exception as e:
            logging.error(f"Erreur lors de l'envoi de la notification de demande de congé: {e}")

    @staticmethod
    def notify_leave_approved(db: Session, employee_id: int, start_date: str, end_date: str) -> None:
        """
        Envoie une notification à l'employé concernant l'approbation de sa demande de congé
        """
        try:
            NotificationService.create_notification(
                db=db,
                recipient_id=employee_id,
                message=f"Votre demande de congé du {start_date} au {end_date} a été approuvée",
                notification_type="leave_approved"
            )
        except Exception as e:
            logging.error(f"Erreur lors de l'envoi de la notification d'approbation de congé: {e}")

    @staticmethod
    def notify_leave_rejected(db: Session, employee_id: int, start_date: str, end_date: str, reason: str = "") -> None:
        """
        Envoie une notification à l'employé concernant le rejet de sa demande de congé
        """
        try:
            message = f"Votre demande de congé du {start_date} au {end_date} a été rejetée"
            if reason:
                message += f". Raison: {reason}"
                
            NotificationService.create_notification(
                db=db,
                recipient_id=employee_id,
                message=message,
                notification_type="leave_rejected"
            )
        except Exception as e:
            logging.error(f"Erreur lors de l'envoi de la notification de rejet de congé: {e}")
