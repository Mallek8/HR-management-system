"""
notification_strategy.py - Implémentation du Pattern Strategy pour les notifications

Ce module définit :
- Une interface abstraite pour les stratégies de notification
- Des implémentations concrètes pour différents canaux (email, SMS, in-app)

Design Pattern : Strategy
- Permet de définir une famille d'algorithmes encapsulés et interchangeables
- Les stratégies peuvent être changées indépendamment des clients qui les utilisent

Avantages :
- Extension facile (ajout de nouveaux canaux de notification)
- Séparation des responsabilités
- Code ouvert à l'extension, fermé à la modification (OCP)
"""

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import Dict, Any


class NotificationStrategy(ABC):
    """
    Interface abstraite définissant les méthodes que toute stratégie
    de notification doit implémenter.
    """
    
    @abstractmethod
    def send(self, recipient_id: int, message: str, **kwargs) -> bool:
        """
        Envoie une notification à un destinataire spécifique.
        
        Args:
            recipient_id: L'identifiant du destinataire
            message: Le contenu de la notification
            kwargs: Paramètres supplémentaires spécifiques à la stratégie
            
        Returns:
            bool: True si l'envoi est réussi, False sinon
        """
        pass
    
    @abstractmethod
    def get_channel_name(self) -> str:
        """
        Retourne le nom du canal de notification.
        
        Returns:
            str: Le nom du canal (ex: "email", "sms", "in-app")
        """
        pass


class EmailNotificationStrategy(NotificationStrategy):
    """
    Stratégie pour envoyer des notifications par email.
    """
    
    def send(self, recipient_id: int, message: str, **kwargs) -> bool:
        # Dans une implémentation réelle, on enverrait un email
        print(f"[EMAIL] Envoi d'un email à l'employé #{recipient_id}: {message}")
        return True
    
    def get_channel_name(self) -> str:
        return "email"


class SMSNotificationStrategy(NotificationStrategy):
    """
    Stratégie pour envoyer des notifications par SMS.
    """
    
    def send(self, recipient_id: int, message: str, **kwargs) -> bool:
        # Dans une implémentation réelle, on enverrait un SMS
        print(f"[SMS] Envoi d'un SMS à l'employé #{recipient_id}: {message}")
        return True
    
    def get_channel_name(self) -> str:
        return "sms"


class DatabaseNotificationStrategy(NotificationStrategy):
    """
    Stratégie pour envoyer des notifications en base de données (in-app).
    Cette stratégie correspond au comportement actuel du système.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def send(self, recipient_id: int, message: str, **kwargs) -> bool:
        """
        Enregistre une notification dans la base de données.
        
        Cette méthode est compatible avec le code existant mais utilise
        l'interface du pattern Strategy.
        """
        from app.services.notification_service import NotificationService
        
        try:
            NotificationService.send_notification(self.db, recipient_id, message)
            return True
        except Exception:
            return False
    
    def get_channel_name(self) -> str:
        return "in-app"


class InAppNotificationStrategy(DatabaseNotificationStrategy):
    """
    Alias pour DatabaseNotificationStrategy pour maintenir la compatibilité avec les tests.
    Cette classe utilise le même comportement que DatabaseNotificationStrategy.
    """
    pass 