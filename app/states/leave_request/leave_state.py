"""
leave_state.py - Interface abstraite pour les états de demande de congé

Ce module définit l'interface que tous les états de demande de congé doivent implémenter.
Chaque état concret (en attente, approuvé, refusé, annulé) implémentera cette interface.

Design Pattern : State (composant "State")
- Définit l'interface commune à tous les états concrets
- Déclare les méthodes pour les différentes actions possibles
- Permet d'encapsuler les comportements spécifiques à chaque état
"""

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any


class LeaveState(ABC):
    """
    Interface abstraite pour les états de demande de congé.
    Tous les états concrets doivent hériter de cette classe et implémenter ses méthodes.
    """
    
    @abstractmethod
    def approve(self, context, db: Session, approved_by: int, **kwargs) -> bool:
        """
        Approuve une demande de congé.
        
        Args:
            context: Le contexte de la demande de congé
            db: Session de base de données
            approved_by: ID de l'employé qui a approuvé
            kwargs: Paramètres supplémentaires
            
        Returns:
            bool: True si l'action a réussi, False sinon
        """
        pass
    
    @abstractmethod
    def reject(self, context, db: Session, rejected_by: int, reason: Optional[str] = None, **kwargs) -> bool:
        """
        Rejette une demande de congé.
        
        Args:
            context: Le contexte de la demande de congé
            db: Session de base de données
            rejected_by: ID de l'employé qui a rejeté
            reason: Motif du rejet
            kwargs: Paramètres supplémentaires
            
        Returns:
            bool: True si l'action a réussi, False sinon
        """
        pass
    
    @abstractmethod
    def cancel(self, context, db: Session, cancelled_by: int, reason: Optional[str] = None, **kwargs) -> bool:
        """
        Annule une demande de congé.
        
        Args:
            context: Le contexte de la demande de congé
            db: Session de base de données
            cancelled_by: ID de l'employé qui a annulé
            reason: Motif de l'annulation
            kwargs: Paramètres supplémentaires
            
        Returns:
            bool: True si l'action a réussi, False sinon
        """
        pass
    
    @abstractmethod
    def submit(self, context, db: Session, **kwargs) -> bool:
        """
        Soumet une demande de congé.
        
        Args:
            context: Le contexte de la demande de congé
            db: Session de base de données
            kwargs: Paramètres supplémentaires
            
        Returns:
            bool: True si l'action a réussi, False sinon
        """
        pass
    
    @abstractmethod
    def get_allowed_transitions(self) -> Dict[str, str]:
        """
        Retourne les transitions autorisées à partir de cet état.
        
        Returns:
            Dict[str, str]: Dictionnaire des transitions possibles
                            {nom_action: nom_état_cible}
        """
        pass
    
    @abstractmethod
    def get_state_name(self) -> str:
        """
        Retourne le nom de l'état.
        
        Returns:
            str: Nom de l'état (ex: "en attente", "approuvé", etc.)
        """
        pass 