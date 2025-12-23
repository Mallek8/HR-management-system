"""
rejected_state.py - État "refusé" pour les demandes de congé

Ce module implémente l'état "refusé" pour les demandes de congé.
Une demande dans cet état ne peut plus être modifiée.

Design Pattern : State (état concret)
- Implémente les comportements spécifiques à l'état "refusé"
- Définit les transitions possibles à partir de cet état
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict

from app.states.leave_request.leave_state import LeaveState


class RejectedState(LeaveState):
    """
    État "refusé" pour les demandes de congé.
    Une demande refusée est dans un état terminal et ne peut plus être modifiée.
    """
    
    def approve(self, context, db: Session, approved_by: int, **kwargs) -> bool:
        """
        Une demande refusée ne peut pas être approuvée.
        
        Returns:
            bool: False car inapplicable dans cet état
        """
        # Une demande refusée ne peut pas être approuvée
        return False
    
    def reject(self, context, db: Session, rejected_by: int, reason: Optional[str] = None, **kwargs) -> bool:
        """
        Une demande déjà refusée ne peut pas être refusée à nouveau.
        
        Returns:
            bool: False car inapplicable dans cet état
        """
        # Déjà refusée, ne peut pas être refusée à nouveau
        return False
    
    def cancel(self, context, db: Session, cancelled_by: int, reason: Optional[str] = None, **kwargs) -> bool:
        """
        Une demande refusée ne peut pas être annulée.
        
        Returns:
            bool: False car inapplicable dans cet état
        """
        # Une demande refusée ne peut pas être annulée
        return False
    
    def submit(self, context, db: Session, **kwargs) -> bool:
        """
        Une demande refusée ne peut pas être soumise à nouveau.
        L'employé doit créer une nouvelle demande.
        
        Returns:
            bool: False car inapplicable dans cet état
        """
        # Une demande refusée ne peut pas être soumise à nouveau
        return False
    
    def get_allowed_transitions(self) -> Dict[str, str]:
        """
        Retourne les transitions autorisées à partir de l'état "refusé".
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
            str: "refusé"
        """
        return "refusé" 