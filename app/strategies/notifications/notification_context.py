"""
notification_context.py - Contexte pour le pattern Strategy des notifications

Ce module définit :
- Le contexte qui utilise les différentes stratégies de notification
- La gestion du choix de la stratégie à utiliser

Design Pattern : Strategy (composant "Context")
- Le contexte maintient une référence à une stratégie
- Délègue l'envoi des notifications à la stratégie choisie

Avantages :
- Découplage entre l'utilisation et l'implémentation
- Flexibilité pour changer de stratégie à runtime
- Extension sans modification du code existant
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from .notification_strategy import (
    NotificationStrategy,
    EmailNotificationStrategy,
    SMSNotificationStrategy,
    InAppNotificationStrategy
)


class NotificationContext:
    """
    Contexte qui utilise les stratégies de notification.
    Cette classe agit comme une façade pour utiliser les différentes
    stratégies de notification.
    """
    
    def __init__(self, db: Session):
        """
        Initialise le contexte avec les stratégies disponibles.
        
        Args:
            db: Session de base de données SQLAlchemy
        """
        self.db = db
        self._strategies: Dict[str, NotificationStrategy] = {
            "email": EmailNotificationStrategy(),
            "sms": SMSNotificationStrategy(),
            "in-app": InAppNotificationStrategy(db)
        }
        # La stratégie par défaut est celle qui correspond au comportement actuel
        self._current_strategy: NotificationStrategy = self._strategies["in-app"]
    
    def set_strategy(self, strategy_name: str) -> bool:
        """
        Change la stratégie utilisée pour l'envoi des notifications.
        
        Args:
            strategy_name: Le nom de la stratégie à utiliser
            
        Returns:
            bool: True si le changement a réussi, False sinon
        """
        if strategy_name in self._strategies:
            self._current_strategy = self._strategies[strategy_name]
            return True
        return False
    
    def send_notification(self, recipient_id: int, message: str, **kwargs) -> bool:
        """
        Envoie une notification en utilisant la stratégie courante.
        
        Args:
            recipient_id: L'identifiant du destinataire
            message: Le contenu de la notification
            kwargs: Paramètres supplémentaires pour la stratégie
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        return self._current_strategy.send(recipient_id, message, **kwargs)
    
    def send_multi_channel(self, recipient_id: int, message: str, 
                          channels: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Envoie une notification sur plusieurs canaux.
        
        Args:
            recipient_id: L'identifiant du destinataire
            message: Le contenu de la notification
            channels: Liste des canaux à utiliser (tous si None)
            
        Returns:
            Dict[str, bool]: Résultats par canal
        """
        results = {}
        
        if channels is None:
            channels = list(self._strategies.keys())
            
        for channel in channels:
            if channel in self._strategies:
                strategy = self._strategies[channel]
                results[channel] = strategy.send(recipient_id, message)
            else:
                results[channel] = False
                
        return results
    
    def get_current_strategy_name(self) -> str:
        """
        Retourne le nom de la stratégie courante.
        
        Returns:
            str: Le nom de la stratégie
        """
        return self._current_strategy.get_channel_name()
    
    def get_available_strategies(self) -> List[str]:
        """
        Retourne la liste des stratégies disponibles.
        
        Returns:
            List[str]: Liste des noms de stratégies
        """
        return list(self._strategies.keys()) 