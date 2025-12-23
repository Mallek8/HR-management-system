"""
notification_observer.py - Observateur concret pour les notifications

Ce module définit un observateur concret qui écoute les événements et envoie
des notifications aux utilisateurs concernés. Il utilise le pattern Observer
pour réagir aux événements sans être fortement couplé au code qui les génère.

Design Pattern : Observer (composant "Concrete Observer")
- Implémente l'interface Observer
- Réagit aux événements en fonction de leur type
- Utilise le service de notification existant pour envoyer des notifications
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from app.observers.event_subject import Observer
from app.observers.event_types import EventType
from app.services.enhanced_notification_service import EnhancedNotificationService
from app.database import SessionLocal


class NotificationObserver(Observer):
    """
    Observateur qui envoie des notifications en réponse aux événements.
    """
    
    def update(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """
        Réagit à un événement en envoyant une notification appropriée.
        
        Args:
            event_type: Le type d'événement qui s'est produit
            data: Les données associées à l'événement
        """
        # Créer une nouvelle session de base de données
        # C'est important car l'observateur peut être notifié dans un contexte
        # où il n'a pas accès à la session originale
        db = SessionLocal()
        
        try:
            # Traiter l'événement selon son type
            if event_type == EventType.LEAVE_REQUESTED:
                self._handle_leave_requested(db, data)
            elif event_type == EventType.LEAVE_APPROVED:
                self._handle_leave_approved(db, data)
            elif event_type == EventType.LEAVE_REJECTED:
                self._handle_leave_rejected(db, data)
            elif event_type == EventType.LEAVE_CANCELLED:
                self._handle_leave_cancelled(db, data)
            elif event_type == EventType.EMPLOYEE_CREATED:
                self._handle_employee_created(db, data)
            elif event_type == EventType.TRAINING_ASSIGNED:
                self._handle_training_assigned(db, data)
            elif event_type == EventType.OBJECTIVE_CREATED:
                self._handle_objective_created(db, data)
            elif event_type == EventType.SYSTEM_ALERT:
                self._handle_system_alert(db, data)
        finally:
            # Fermer la session quoi qu'il arrive
            db.close()
    
    def _handle_leave_requested(self, db: Session, data: Dict[str, Any]) -> None:
        """
        Traite un événement de demande de congé.
        
        Args:
            db: Session de base de données
            data: Données de l'événement
        """
        employee_id = data.get("employee_id")
        supervisor_id = data.get("supervisor_id")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        if not all([employee_id, supervisor_id, start_date, end_date]):
            return
        
        # Notification au superviseur
        message = f"Nouvelle demande de congé du {start_date} au {end_date}"
        EnhancedNotificationService.send_notification(
            db=db,
            employee_id=supervisor_id,
            message=message,
            channel="in-app"
        )
    
    def _handle_leave_approved(self, db: Session, data: Dict[str, Any]) -> None:
        """
        Traite un événement d'approbation de congé.
        
        Args:
            db: Session de base de données
            data: Données de l'événement
        """
        employee_id = data.get("employee_id")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        if not all([employee_id, start_date, end_date]):
            return
        
        # Notification à l'employé (multi-canal pour s'assurer qu'il est informé)
        message = f"Votre demande de congé du {start_date} au {end_date} a été approuvée."
        EnhancedNotificationService.send_multi_channel_notification(
            db=db,
            employee_id=employee_id,
            message=message,
            channels=["in-app", "email"]
        )
        
        # Notification à l'administrateur
        EnhancedNotificationService.send_notification_to_admin(
            db=db,
            message=f"Congé approuvé pour l'employé #{employee_id} du {start_date} au {end_date}",
            channel="in-app"
        )
    
    def _handle_leave_rejected(self, db: Session, data: Dict[str, Any]) -> None:
        """
        Traite un événement de rejet de congé.
        
        Args:
            db: Session de base de données
            data: Données de l'événement
        """
        employee_id = data.get("employee_id")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        reason = data.get("reason", "Non spécifié")
        
        if not all([employee_id, start_date, end_date]):
            return
        
        # Notification à l'employé
        message = f"Votre demande de congé du {start_date} au {end_date} a été refusée. Motif: {reason}"
        EnhancedNotificationService.send_multi_channel_notification(
            db=db,
            employee_id=employee_id,
            message=message,
            channels=["in-app", "email"]
        )
    
    def _handle_leave_cancelled(self, db: Session, data: Dict[str, Any]) -> None:
        """
        Traite un événement d'annulation de congé.
        
        Args:
            db: Session de base de données
            data: Données de l'événement
        """
        employee_id = data.get("employee_id")
        cancelled_by = data.get("cancelled_by")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        if not all([employee_id, cancelled_by, start_date, end_date]):
            return
        
        # Si annulé par quelqu'un d'autre, notifier l'employé
        if cancelled_by != employee_id:
            message = f"Votre congé du {start_date} au {end_date} a été annulé."
            EnhancedNotificationService.send_notification(
                db=db,
                employee_id=employee_id,
                message=message,
                channel="in-app"
            )
        
        # Notifier l'administrateur
        EnhancedNotificationService.send_notification_to_admin(
            db=db,
            message=f"Congé annulé pour l'employé #{employee_id} du {start_date} au {end_date}",
            channel="in-app"
        )
    
    def _handle_employee_created(self, db: Session, data: Dict[str, Any]) -> None:
        """
        Traite un événement de création d'employé.
        
        Args:
            db: Session de base de données
            data: Données de l'événement
        """
        employee_id = data.get("employee_id")
        employee_name = data.get("employee_name")
        
        if not all([employee_id, employee_name]):
            return
        
        # Notification à l'administrateur
        EnhancedNotificationService.send_notification_to_admin(
            db=db,
            message=f"Nouvel employé créé: {employee_name}",
            channel="in-app"
        )
    
    def _handle_training_assigned(self, db: Session, data: Dict[str, Any]) -> None:
        """
        Traite un événement d'attribution de formation.
        
        Args:
            db: Session de base de données
            data: Données de l'événement
        """
        employee_id = data.get("employee_id")
        training_name = data.get("training_name")
        
        if not all([employee_id, training_name]):
            return
        
        # Notification à l'employé
        message = f"Vous avez été inscrit à la formation '{training_name}'."
        EnhancedNotificationService.send_multi_channel_notification(
            db=db,
            employee_id=employee_id,
            message=message,
            channels=["in-app", "email"]
        )
    
    def _handle_objective_created(self, db: Session, data: Dict[str, Any]) -> None:
        """
        Traite un événement de création d'objectif.
        
        Args:
            db: Session de base de données
            data: Données de l'événement
        """
        employee_id = data.get("employee_id")
        objective_title = data.get("objective_title")
        
        if not all([employee_id, objective_title]):
            return
        
        # Notification à l'employé
        message = f"Un nouvel objectif a été défini pour vous: '{objective_title}'."
        EnhancedNotificationService.send_notification(
            db=db,
            employee_id=employee_id,
            message=message,
            channel="in-app"
        )
    
    def _handle_system_alert(self, db: Session, data: Dict[str, Any]) -> None:
        """
        Traite un événement d'alerte système.
        
        Args:
            db: Session de base de données
            data: Données de l'événement
        """
        message = data.get("message")
        if not message:
            return
        
        # Notification à l'administrateur
        EnhancedNotificationService.send_notification_to_admin(
            db=db,
            message=f"ALERTE SYSTÈME: {message}",
            channel="in-app"
        ) 