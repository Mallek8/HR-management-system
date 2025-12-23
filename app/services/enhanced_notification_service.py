"""
enhanced_notification_service.py - Service de notification amélioré utilisant le pattern Strategy

Ce service:
- Étend les fonctionnalités du NotificationService existant
- Ajoute le support de multiples canaux de notification
- Est complètement compatible avec l'existant

Design Pattern : Strategy
- Utilise NotificationContext qui implémente le pattern Strategy
- Permet d'envoyer des notifications par différents canaux (email, SMS, in-app)

Avantages :
- Extension non invasive du service existant
- Ajout de fonctionnalités sans modifier le code existant
- Respect de Open/Closed Principle (OCP)
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional

from app.strategies.notifications.notification_context import NotificationContext
from app.services.notification_service import NotificationService


class EnhancedNotificationService:
    """
    Service de notification amélioré qui utilise le pattern Strategy
    pour gérer différents canaux de notification.
    """
    
    @staticmethod
    def send_notification(db: Session, employee_id: int, message: str, 
                          channel: str = "in-app") -> bool:
        """
        Envoie une notification à un employé en utilisant le canal spécifié.
        
        Compatible avec le NotificationService existant (par défaut: in-app)
        mais offre la possibilité d'utiliser d'autres canaux.
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé destinataire
            message: Contenu de la notification
            channel: Canal à utiliser ("email", "sms", "in-app")
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        context = NotificationContext(db)
        
        # On s'assure d'utiliser le bon canal
        context.set_strategy(channel)
        
        # On délègue l'envoi à la stratégie choisie
        return context.send_notification(employee_id, message)
    
    @staticmethod
    def send_multi_channel_notification(db: Session, employee_id: int, message: str,
                                      channels: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Envoie une notification sur plusieurs canaux.
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé destinataire
            message: Contenu de la notification
            channels: Liste des canaux à utiliser (tous si None)
            
        Returns:
            Dict[str, bool]: Résultats par canal
        """
        context = NotificationContext(db)
        return context.send_multi_channel(employee_id, message, channels)
    
    @staticmethod
    def send_notification_to_admin(db: Session, message: str, 
                                 channel: str = "in-app") -> bool:
        """
        Envoie une notification à l'administrateur.
        
        Args:
            db: Session de base de données
            message: Contenu de la notification
            channel: Canal à utiliser
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        # On récupère l'admin comme dans le service original
        from app.models.employee import Employee
        admin = db.query(Employee).filter(Employee.role == "admin").first()
        if not admin:
            return False
            
        # On utilise la nouvelle méthode d'envoi
        return EnhancedNotificationService.send_notification(
            db, admin.id, message, channel
        )
    
    @staticmethod
    def get_available_channels() -> List[str]:
        """
        Retourne la liste des canaux disponibles.
        
        Returns:
            List[str]: Liste des canaux
        """
        # Cette méthode nécessite une instance temporaire du contexte
        # Dans une implémentation réelle, on pourrait optimiser cela
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            context = NotificationContext(db)
            return context.get_available_strategies()
        finally:
            db.close() 