"""
approved_state.py - État "approuvé" pour les demandes de congé

Ce module implémente l'état "approuvé" pour les demandes de congé.
Une demande dans cet état peut uniquement être annulée.

Design Pattern : State (état concret)
- Implémente les comportements spécifiques à l'état "approuvé"
- Définit les transitions possibles à partir de cet état
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime, UTC

from app.states.leave_request.leave_state import LeaveState
from app.services.enhanced_notification_service import EnhancedNotificationService


class ApprovedState(LeaveState):
    """
    État "approuvé" pour les demandes de congé.
    Une demande approuvée ne peut plus être approuvée ni rejetée, seulement annulée.
    """
    
    def can_approve(self) -> bool:
        """
        Vérifie si la demande peut être approuvée.
        Dans l'état approuvé, une demande ne peut pas être approuvée à nouveau.
        
        Returns:
            bool: False, car l'approbation n'est pas possible dans l'état approuvé
        """
        return False
        
    def can_reject(self) -> bool:
        """
        Vérifie si la demande peut être rejetée.
        Dans l'état approuvé, une demande ne peut pas être rejetée.
        
        Returns:
            bool: False, car le rejet n'est pas possible dans l'état approuvé
        """
        return False
        
    def can_cancel(self) -> bool:
        """
        Vérifie si la demande peut être annulée.
        Dans l'état approuvé, une demande peut être annulée.
        
        Returns:
            bool: True, car l'annulation est possible dans l'état approuvé
        """
        return True
        
    def can_submit(self) -> bool:
        """
        Vérifie si la demande peut être soumise.
        Dans l'état approuvé, une demande ne peut pas être soumise à nouveau.
        
        Returns:
            bool: False, car la soumission n'est pas possible dans l'état approuvé
        """
        return False
    
    def approve(self, context, db: Session, approved_by: int, **kwargs) -> dict:
        """
        Une demande déjà approuvée ne peut pas être approuvée à nouveau.
        
        Returns:
            dict: Dictionnaire avec le résultat de l'opération
        """
        # Déjà approuvée, ne peut pas être approuvée à nouveau
        return {"success": False, "message": "Cette demande ne peut pas être approuvée car elle est déjà approuvée."}
    
    def reject(self, context, db: Session, rejected_by: int, reason: Optional[str] = None, **kwargs) -> dict:
        """
        Une demande déjà approuvée ne peut pas être rejetée.
        
        Returns:
            dict: Dictionnaire avec le résultat de l'opération
        """
        # Déjà approuvée, ne peut pas être rejetée
        return {"success": False, "message": "Cette demande ne peut pas être rejetée car elle est déjà approuvée."}
    
    def cancel(self, context, db: Session, cancelled_by: int, reason: Optional[str] = None, **kwargs) -> dict:
        """
        Annule une demande de congé approuvée.
        
        Args:
            context: Le contexte de la demande de congé
            db: Session de base de données
            cancelled_by: ID de l'employé qui a annulé
            reason: Motif de l'annulation
            
        Returns:
            dict: Dictionnaire avec le résultat de l'opération
        """
        try:
            # Obtenir l'objet leave_request du contexte
            leave_request = context.get_request()
            
            # Modification de l'état de la demande
            leave_request.status = "annulé"
            leave_request.cancellation_reason = reason or "Aucun motif fourni"
            leave_request.cancelled_by = cancelled_by
            leave_request.cancelled_date = datetime.now(UTC)
            
            # Mise à jour de la demande dans la base de données
            db.commit()
            
            # Notifications
            # Si annulé par l'administrateur ou le superviseur, notifier l'employé
            if cancelled_by != leave_request.employee_id:
                EnhancedNotificationService.send_notification(
                    db=db,
                    employee_id=leave_request.employee_id,
                    message=f"Votre congé approuvé du {leave_request.start_date} au {leave_request.end_date} a été annulé. Motif: {reason or 'Non spécifié'}",
                    channel="in-app"
                )
            # Si annulé par l'employé, notifier l'administrateur
            else:
                # Notifier le responsable ou l'admin
                admin_message = f"L'employé #{leave_request.employee_id} a annulé son congé approuvé du {leave_request.start_date} au {leave_request.end_date}."
                EnhancedNotificationService.send_notification_to_admin(
                    db=db,
                    message=admin_message,
                    channel="in-app"
                )
            
            # Transition vers l'état "annulé"
            from app.states.leave_request.cancelled_state import CancelledState
            context.change_state(CancelledState())
            
            return {"success": True, "message": "Demande annulée avec succès"}
        except Exception as e:
            db.rollback()
            print(f"Erreur lors de l'annulation de la demande approuvée: {str(e)}")
            return {"success": False, "message": f"Erreur lors de l'annulation: {str(e)}"}
    
    def submit(self, context, db: Session, **kwargs) -> dict:
        """
        Une demande approuvée ne peut pas être soumise à nouveau.
        
        Returns:
            dict: Dictionnaire avec le résultat de l'opération
        """
        # Déjà approuvée, ne peut pas être soumise à nouveau
        return {"success": False, "message": "Cette demande ne peut pas être soumise à nouveau car elle est déjà approuvée."}
    
    def get_allowed_transitions(self) -> Dict[str, str]:
        """
        Retourne les transitions autorisées à partir de l'état "approuvé".
        
        Returns:
            Dict[str, str]: Dictionnaire des transitions possibles
        """
        return {
            "cancel": "annulé"
        }
    
    def get_state_name(self) -> str:
        """
        Retourne le nom de l'état.
        
        Returns:
            str: "approuvé"
        """
        return "approuvé" 