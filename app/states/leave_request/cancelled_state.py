"""
cancelled_state.py - État "annulé" pour les demandes de congé

Ce module implémente l'état "annulé" pour les demandes de congé.
Une demande dans cet état ne peut plus être modifiée.

Design Pattern : State (état concret)
- Implémente les comportements spécifiques à l'état "annulé"
- Définit les transitions possibles à partir de cet état
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict

from app.states.leave_request.leave_state import LeaveState


class CancelledState(LeaveState):
    """
    État "annulé" pour les demandes de congé.
    Une demande annulée est dans un état terminal et ne peut plus être modifiée.
    """
    
    def approve(self, context, db: Session, approved_by: int, **kwargs) -> bool:
        """
        Une demande annulée ne peut pas être approuvée.
        
        Returns:
            bool: False car inapplicable dans cet état
        """
        # Une demande annulée ne peut pas être approuvée
        return False
    
    def reject(self, context, db: Session, rejected_by: int, reason: Optional[str] = None, **kwargs) -> bool:
        """
        Une demande annulée ne peut pas être rejetée.
        
        Returns:
            bool: False car inapplicable dans cet état
        """
        # Une demande annulée ne peut pas être rejetée
        return False
    
    def cancel(self, context, db: Session, cancelled_by: int, reason: Optional[str] = None, **kwargs) -> bool:
        """
        Une demande déjà annulée ne peut pas être annulée à nouveau.
        
        Returns:
            bool: False car inapplicable dans cet état
        """
        # Déjà annulée, ne peut pas être annulée à nouveau
        return False
    
    def submit(self, context, db: Session, **kwargs) -> bool:
        """
        Une demande annulée ne peut pas être soumise à nouveau.
        L'employé doit créer une nouvelle demande.
        
        Returns:
            bool: False car inapplicable dans cet état
        """
        # Une demande annulée ne peut pas être soumise à nouveau
        return False
    
    def get_allowed_transitions(self) -> Dict[str, str]:
        """
        Retourne les transitions autorisées à partir de l'état "annulé".
        Aucune transition n'est autorisée depuis cet état.
        
        Returns:
            Dict[str, str]: Dictionnaire vide car aucune transition n'est possible
        """
        # Aucune transition n'est autorisée
        return {}
    
    def get_state_name(self) -> str:
        """
        Retourne le nom de l'état.
        
        Returns:
            str: "annulé"
        """
        return "annulé" 