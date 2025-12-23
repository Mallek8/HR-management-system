"""
pending_state.py - État "en attente" pour les demandes de congé

Ce module implémente l'état "en attente" pour les demandes de congé.
Une demande dans cet état peut être approuvée, rejetée ou annulée.

Design Pattern : State (état concret)
- Implémente les comportements spécifiques à l'état "en attente"
- Définit les transitions possibles à partir de cet état
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime, UTC

from app.states.leave_request.leave_state import LeaveState
from app.services.enhanced_notification_service import EnhancedNotificationService
from app.states.leave_request.approved_state import ApprovedState
from app.states.leave_request.rejected_state import RejectedState
from app.states.leave_request.cancelled_state import CancelledState


class PendingState(LeaveState):
    """
    État "en attente" pour les demandes de congé.
    C'est l'état initial de toute nouvelle demande.
    """
    
    def can_approve(self) -> bool:
        """
        Vérifie si la demande peut être approuvée.
        Dans l'état en attente, une demande peut toujours être approuvée.
        
        Returns:
            bool: True, car l'approbation est possible dans l'état en attente
        """
        return True
        
    def can_reject(self) -> bool:
        """
        Vérifie si la demande peut être rejetée.
        Dans l'état en attente, une demande peut toujours être rejetée.
        
        Returns:
            bool: True, car le rejet est possible dans l'état en attente
        """
        return True
        
    def can_cancel(self) -> bool:
        """
        Vérifie si la demande peut être annulée.
        Dans l'état en attente, une demande peut toujours être annulée.
        
        Returns:
            bool: True, car l'annulation est possible dans l'état en attente
        """
        return True
    
    def approve(self, context, db: Session, approved_by: int, comment: str = None) -> dict:
        """
        Approuve la demande de congé, déplace le contexte vers l'état approuvé.
        """
        # Vérifier qu'on peut faire la transition
        if not self.can_approve():
            return {"success": False, "message": "Cette demande ne peut pas être approuvée car elle n'est pas en attente."}
        
        # Obtenir l'objet leave_request du contexte
        leave_request = context.get_request()
        
        try:
            # Mettre à jour les champs nécessaires en BD
            leave_request.status = "approuvé"
            leave_request.approved_by = approved_by
            leave_request.approved_date = datetime.now(UTC)
            leave_request.supervisor_comment = comment
            
            # Passer à l'état suivant
            context.change_state(ApprovedState())
            
            # Commit
            db.commit()
            
            # Notification à l'employé
            EnhancedNotificationService.send_multi_channel_notification(
                db=db,
                employee_id=leave_request.employee_id,
                message=f"Votre demande de congé du {leave_request.start_date} au {leave_request.end_date} a été approuvée.",
                channels=["in-app", "email"]
            )
            
            return {"success": True, "message": "Demande approuvée avec succès"}
            
        except Exception as e:
            db.rollback()
            print(f"Erreur lors de l'approbation: {str(e)}")
            return {"success": False, "message": f"Erreur lors de l'approbation: {str(e)}"}
    
    def reject(self, context, db: Session, rejected_by: int, reason: str = None) -> dict:
        """
        Rejette la demande de congé, déplace le contexte vers l'état rejeté.
        """
        # Vérifier qu'on peut faire la transition
        if not self.can_reject():
            return {"success": False, "message": "Cette demande ne peut pas être rejetée car elle n'est pas en attente."}
        
        # Obtenir l'objet leave_request du contexte
        leave_request = context.get_request()
        
        try:
            # Mettre à jour les champs nécessaires en BD
            leave_request.status = "refusé"
            leave_request.rejected_by = rejected_by
            leave_request.rejected_date = datetime.now(UTC)
            leave_request.rejection_reason = reason
            
            # Passer à l'état suivant
            context.change_state(RejectedState())
            
            # Commit
            db.commit()
            
            # Notification à l'employé
            message = f"Votre demande de congé du {leave_request.start_date} au {leave_request.end_date} a été refusée."
            if reason:
                message += f" Motif: {reason}"
                
            EnhancedNotificationService.send_multi_channel_notification(
                db=db,
                employee_id=leave_request.employee_id,
                message=message,
                channels=["in-app", "email"]
            )
            
            return {"success": True, "message": "Demande rejetée avec succès"}
            
        except Exception as e:
            db.rollback()
            print(f"Erreur lors du rejet: {str(e)}")
            return {"success": False, "message": f"Erreur lors du rejet: {str(e)}"}
    
    def cancel(self, context, db: Session, cancelled_by: int, reason: str = None) -> dict:
        """
        Annule la demande de congé, déplace le contexte vers l'état annulé.
        """
        # Vérifier qu'on peut faire la transition
        if not self.can_cancel():
            return {"success": False, "message": "Cette demande ne peut pas être annulée."}
        
        # Obtenir l'objet leave_request du contexte
        leave_request = context.get_request()
        
        try:
            # Mettre à jour les champs nécessaires en BD
            leave_request.status = "annulé"
            leave_request.cancelled_by = cancelled_by
            leave_request.cancelled_date = datetime.now(UTC)
            leave_request.cancellation_reason = reason
            
            # Passer à l'état suivant
            context.change_state(CancelledState())
            
            # Commit
            db.commit()
            
            # Notification
            if cancelled_by != leave_request.employee_id:
                # Si annulé par quelqu'un d'autre, notifier l'employé
                EnhancedNotificationService.send_notification(
                    db=db,
                    employee_id=leave_request.employee_id,
                    message=f"Votre demande de congé a été annulée. Motif: {reason or 'Non spécifié'}",
                    channel="in-app"
                )
            
            return {"success": True, "message": "Demande annulée avec succès"}
            
        except Exception as e:
            db.rollback()
            print(f"Erreur lors de l'annulation: {str(e)}")
            return {"success": False, "message": f"Erreur lors de l'annulation: {str(e)}"}
    
    def submit(self, context, db: Session, **kwargs) -> bool:
        """
        La demande est déjà soumise, donc cette action n'a pas d'effet dans cet état.
        
        Returns:
            bool: False car inapplicable dans cet état
        """
        # Déjà dans l'état soumis/en attente
        return False
    
    def get_allowed_transitions(self) -> Dict[str, str]:
        """
        Retourne les transitions autorisées à partir de l'état "en attente".
        
        Returns:
            Dict[str, str]: Dictionnaire des transitions possibles
        """
        return {
            "approve": "approuvé",
            "reject": "refusé",
            "cancel": "annulé"
        }
    
    def get_state_name(self) -> str:
        """
        Retourne le nom de l'état.
        
        Returns:
            str: "en attente"
        """
        return "en attente" 