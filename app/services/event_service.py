"""
event_service.py - Service pour gérer les événements avec le pattern Observer

Ce service centralise la gestion des événements de l'application. Il fournit
des méthodes pour émettre des événements et initialiser le système d'événements.

Design Pattern : Observer (client)
- Utilise EventSubject pour émettre des événements
- Facilite l'utilisation du pattern Observer par les autres services
- Initialise et configure les observateurs au démarrage de l'application
"""

from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.observers.event_subject import EventSubject, Observer
from app.observers.event_types import EventType
from app.observers.notification_observer import NotificationObserver
from app.models.event import Event
from app.schemas import EventCreate, EventUpdate


class EventService:
    """
    Service qui centralise la gestion des événements de l'application.
    """
    
    @staticmethod
    def emit_event(event_type: EventType, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Émet un événement qui sera transmis à tous les observateurs concernés.
        
        Args:
            event_type: Le type d'événement à émettre
            data: Les données associées à l'événement
        """
        subject = EventSubject()
        subject.notify(event_type, data)
    
    @staticmethod
    def register_observer(observer: Observer, event_types: Optional[List[EventType]] = None) -> None:
        """
        Enregistre un observateur pour les types d'événements spécifiés.
        
        Args:
            observer: L'observateur à enregistrer
            event_types: Les types d'événements à observer (tous si None)
        """
        subject = EventSubject()
        subject.attach(observer, event_types)
    
    @staticmethod
    def unregister_observer(observer: Observer, event_types: Optional[List[EventType]] = None) -> None:
        """
        Désenregistre un observateur pour les types d'événements spécifiés.
        
        Args:
            observer: L'observateur à désenregistrer
            event_types: Les types d'événements à ne plus observer (tous si None)
        """
        subject = EventSubject()
        subject.detach(observer, event_types)
    
    @staticmethod
    def register_callback(event_type: EventType, callback: Callable) -> None:
        """
        Enregistre une fonction de rappel pour un type d'événement.
        
        Args:
            event_type: Le type d'événement
            callback: La fonction à appeler lorsque l'événement se produit
        """
        subject = EventSubject()
        subject.register_callback(event_type, callback)
    
    @staticmethod
    def unregister_callback(event_type: EventType, callback: Callable) -> None:
        """
        Désenregistre une fonction de rappel pour un type d'événement.
        
        Args:
            event_type: Le type d'événement
            callback: La fonction à désenregistrer
        """
        subject = EventSubject()
        subject.unregister_callback(event_type, callback)
    
    @staticmethod
    def initialize() -> None:
        """
        Initialise le système d'événements en enregistrant les observateurs par défaut.
        Cette méthode doit être appelée au démarrage de l'application.
        """
        # Créer et enregistrer l'observateur de notification
        notification_observer = NotificationObserver()
        EventService.register_observer(notification_observer)
        
        print("Système d'événements initialisé avec succès")
        
    @staticmethod
    def emit_leave_requested(employee_id: int, supervisor_id: int, start_date: str, end_date: str) -> None:
        """
        Émet un événement de demande de congé.
        
        Args:
            employee_id: ID de l'employé qui demande le congé
            supervisor_id: ID du superviseur
            start_date: Date de début du congé
            end_date: Date de fin du congé
        """
        data = {
            "employee_id": employee_id,
            "supervisor_id": supervisor_id,
            "start_date": start_date,
            "end_date": end_date
        }
        EventService.emit_event(EventType.LEAVE_REQUESTED, data)
    
    @staticmethod
    def emit_leave_approved(employee_id: int, start_date: str, end_date: str) -> None:
        """
        Émet un événement d'approbation de congé.
        
        Args:
            employee_id: ID de l'employé concerné
            start_date: Date de début du congé
            end_date: Date de fin du congé
        """
        data = {
            "employee_id": employee_id,
            "start_date": start_date,
            "end_date": end_date
        }
        EventService.emit_event(EventType.LEAVE_APPROVED, data)
    
    @staticmethod
    def emit_leave_rejected(employee_id: int, start_date: str, end_date: str, reason: Optional[str] = None) -> None:
        """
        Émet un événement de rejet de congé.
        
        Args:
            employee_id: ID de l'employé concerné
            start_date: Date de début du congé
            end_date: Date de fin du congé
            reason: Motif du rejet
        """
        data = {
            "employee_id": employee_id,
            "start_date": start_date,
            "end_date": end_date,
            "reason": reason
        }
        EventService.emit_event(EventType.LEAVE_REJECTED, data)
    
    @staticmethod
    def emit_leave_cancelled(employee_id: int, cancelled_by: int, start_date: str, end_date: str) -> None:
        """
        Émet un événement d'annulation de congé.
        
        Args:
            employee_id: ID de l'employé concerné
            cancelled_by: ID de l'employé qui a annulé le congé
            start_date: Date de début du congé
            end_date: Date de fin du congé
        """
        data = {
            "employee_id": employee_id,
            "cancelled_by": cancelled_by,
            "start_date": start_date,
            "end_date": end_date
        }
        EventService.emit_event(EventType.LEAVE_CANCELLED, data)
    
    @staticmethod
    def emit_employee_created(employee_id: int, employee_name: str) -> None:
        """
        Émet un événement de création d'employé.
        
        Args:
            employee_id: ID de l'employé créé
            employee_name: Nom de l'employé
        """
        data = {
            "employee_id": employee_id,
            "employee_name": employee_name
        }
        EventService.emit_event(EventType.EMPLOYEE_CREATED, data)
    
    @staticmethod
    def emit_training_assigned(employee_id: int, training_id: int, training_name: str) -> None:
        """
        Émet un événement d'attribution de formation.
        
        Args:
            employee_id: ID de l'employé concerné
            training_id: ID de la formation
            training_name: Nom de la formation
        """
        data = {
            "employee_id": employee_id,
            "training_id": training_id,
            "training_name": training_name
        }
        EventService.emit_event(EventType.TRAINING_ASSIGNED, data)
    
    @staticmethod
    def emit_system_alert(message: str) -> None:
        """
        Émet un événement d'alerte système.
        
        Args:
            message: Message d'alerte
        """
        data = {
            "message": message
        }
        EventService.emit_event(EventType.SYSTEM_ALERT, data)
        
    @staticmethod
    def get_events(db: Session) -> List[Event]:
        """
        Récupère tous les événements.
        
        Args:
            db: Session de base de données
        
        Returns:
            List[Event]: Liste des événements
        """
        try:
            return db.query(Event).all()
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la récupération des événements: {e}")
            return []
            
    @staticmethod
    def get_event(db: Session, event_id: int) -> Optional[Event]:
        """
        Récupère un événement par son ID.
        
        Args:
            db: Session de base de données
            event_id: ID de l'événement
            
        Returns:
            Optional[Event]: Événement trouvé ou None
        """
        try:
            return db.query(Event).filter(Event.id == event_id).first()
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la récupération de l'événement {event_id}: {e}")
            return None
            
    @staticmethod
    def create_event(db: Session, event_data: EventCreate) -> Optional[Event]:
        """
        Crée un nouvel événement.
        
        Args:
            db: Session de base de données
            event_data: Données de l'événement
            
        Returns:
            Optional[Event]: Événement créé ou None en cas d'erreur
        """
        try:
            event = Event(**event_data.dict())
            db.add(event)
            db.commit()
            db.refresh(event)
            return event
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la création de l'événement: {e}")
            return None
            
    @staticmethod
    def update_event(db: Session, event_id: int, event_data: EventUpdate) -> Optional[Event]:
        """
        Met à jour un événement existant.
        
        Args:
            db: Session de base de données
            event_id: ID de l'événement
            event_data: Données mises à jour
            
        Returns:
            Optional[Event]: Événement mis à jour ou None
        """
        try:
            event = db.query(Event).filter(Event.id == event_id).first()
            if not event:
                return None
                
            update_data = event_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(event, key, value)
                
            db.commit()
            db.refresh(event)
            return event
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la mise à jour de l'événement {event_id}: {e}")
            return None
            
    @staticmethod
    def delete_event(db: Session, event_id: int) -> bool:
        """
        Supprime un événement.
        
        Args:
            db: Session de base de données
            event_id: ID de l'événement
            
        Returns:
            bool: True si suppression réussie, False sinon
        """
        try:
            event = db.query(Event).filter(Event.id == event_id).first()
            if not event:
                return False
                
            db.delete(event)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la suppression de l'événement {event_id}: {e}")
            return False
            
    @staticmethod
    def get_events_for_employee(db: Session, employee_id: int) -> List[Event]:
        """
        Récupère les événements associés à un employé.
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé
            
        Returns:
            List[Event]: Liste des événements
        """
        try:
            return db.query(Event).filter(Event.employee_id == employee_id).all()
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la récupération des événements pour l'employé {employee_id}: {e}")
            return []
            
    @staticmethod
    def get_events_by_date_range(db: Session, start_date: Union[str, date], end_date: Union[str, date]) -> List[Event]:
        """
        Récupère les événements dans une plage de dates.
        
        Args:
            db: Session de base de données
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            List[Event]: Liste des événements
        """
        try:
            # Convertir les chaînes en objets date si nécessaire
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                
            return db.query(Event).filter(
                Event.start_date >= start_date,
                Event.start_date <= end_date
            ).all()
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la récupération des événements par plage de dates: {e}")
            return []
            
    @staticmethod
    def get_events_by_type(db: Session, event_type: str) -> List[Event]:
        """
        Récupère les événements d'un type spécifique.
        
        Args:
            db: Session de base de données
            event_type: Type d'événement
            
        Returns:
            List[Event]: Liste des événements
        """
        try:
            return db.query(Event).filter(Event.event_type == event_type).all()
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la récupération des événements de type {event_type}: {e}")
            return [] 