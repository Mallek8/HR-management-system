"""
leave_context.py - Contexte pour le pattern State des demandes de congé

Ce module définit la classe contexte qui gère les différents états d'une demande de congé
et les transitions entre ces états. C'est le point d'entrée principal pour utiliser
le pattern State.

Design Pattern : State (composant "Context")
- Maintient une référence à l'état courant
- Délègue la gestion des comportements spécifiques à l'état actuel
- Gère les transitions entre les états
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, Type

from app.models.leave import Leave
from app.states.leave_request.leave_state import LeaveState
from app.states.leave_request.pending_state import PendingState
from app.states.leave_request.approved_state import ApprovedState
from app.states.leave_request.rejected_state import RejectedState
from app.states.leave_request.cancelled_state import CancelledState


class LeaveContext:
    """
    Contexte pour les demandes de congé, gère les transitions d'état.
    C'est la classe principale à utiliser pour manipuler une demande de congé
    selon le pattern State.
    """
    
    def __init__(self, leave_request: Leave):
        """
        Initialise le contexte avec une demande de congé et détermine son état initial.
        
        Args:
            leave_request: La demande de congé à gérer
        """
        self.leave_request = leave_request
        
        # Déterminer l'état initial en fonction du statut de la demande
        self._state = self._get_state_from_status(leave_request.status)
    
    def _get_state_from_status(self, status: str) -> LeaveState:
        """
        Retourne l'état correspondant au statut de la demande.
        
        Args:
            status: Le statut de la demande ("en attente", "approuvé", "refusé", "annulé")
            
        Returns:
            LeaveState: L'état correspondant
        """
        status_map = {
            "en attente": PendingState,
            "approuvé": ApprovedState,
            "refusé": RejectedState,
            "annulé": CancelledState
        }
        
        # Si le statut n'est pas reconnu, on considère que la demande est en attente
        state_class = status_map.get(status, PendingState)
        return state_class()
    
    def transition_to(self, state: LeaveState) -> None:
        """
        Change l'état courant.
        
        Args:
            state: Le nouvel état
        """
        self._state = state
    
    def change_state(self, state: LeaveState) -> None:
        """
        Change l'état courant de la demande de congé.
        Méthode alternative à transition_to pour compatibilité avec l'API existante.
        
        Args:
            state: Le nouvel état
        """
        self._state = state
    
    def get_current_state(self) -> LeaveState:
        """
        Retourne l'état courant.
        
        Returns:
            LeaveState: L'état courant
        """
        return self._state
    
    def get_current_state_name(self) -> str:
        """
        Retourne le nom de l'état courant.
        
        Returns:
            str: Le nom de l'état courant
        """
        return self._state.get_state_name()
    
    def approve(self, db: Session, approved_by: int, **kwargs) -> bool:
        """
        Tente d'approuver la demande de congé.
        Délègue l'action à l'état courant.
        
        Args:
            db: Session de base de données
            approved_by: ID de l'employé qui a approuvé
            kwargs: Paramètres supplémentaires
            
        Returns:
            bool: True si l'approbation a réussi, False sinon
        """
        return self._state.approve(self, db, approved_by, **kwargs)
    
    def reject(self, db: Session, rejected_by: int, reason: Optional[str] = None, **kwargs) -> bool:
        """
        Tente de rejeter la demande de congé.
        Délègue l'action à l'état courant.
        
        Args:
            db: Session de base de données
            rejected_by: ID de l'employé qui a rejeté
            reason: Motif du rejet
            kwargs: Paramètres supplémentaires
            
        Returns:
            bool: True si le rejet a réussi, False sinon
        """
        return self._state.reject(self, db, rejected_by, reason, **kwargs)
    
    def cancel(self, db: Session, cancelled_by: int, reason: Optional[str] = None, **kwargs) -> bool:
        """
        Tente d'annuler la demande de congé.
        Délègue l'action à l'état courant.
        
        Args:
            db: Session de base de données
            cancelled_by: ID de l'employé qui a annulé
            reason: Motif de l'annulation
            kwargs: Paramètres supplémentaires
            
        Returns:
            bool: True si l'annulation a réussi, False sinon
        """
        return self._state.cancel(self, db, cancelled_by, reason, **kwargs)
    
    def submit(self, db: Session, **kwargs) -> bool:
        """
        Tente de soumettre la demande de congé.
        Délègue l'action à l'état courant.
        
        Args:
            db: Session de base de données
            kwargs: Paramètres supplémentaires
            
        Returns:
            bool: True si la soumission a réussi, False sinon
        """
        return self._state.submit(self, db, **kwargs)
    
    def get_allowed_transitions(self) -> Dict[str, str]:
        """
        Retourne les transitions autorisées à partir de l'état courant.
        
        Returns:
            Dict[str, str]: Dictionnaire des transitions possibles
        """
        return self._state.get_allowed_transitions()
        
    def get_request(self) -> Leave:
        """
        Retourne la demande de congé associée à ce contexte.
        
        Returns:
            Leave: L'objet de demande de congé
        """
        return self.leave_request 