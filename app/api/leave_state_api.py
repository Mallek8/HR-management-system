"""
leave_state_api.py - API de démonstration du pattern State pour les demandes de congé

Ce module fournit des endpoints REST pour manipuler les demandes de congé
en utilisant le pattern State. Il sert à démontrer l'utilisation du pattern
sans affecter l'application existante.

Design Pattern : State
- Utilise LeaveStateService qui encapsule l'utilisation du pattern State
- Permet de manipuler les demandes de congé selon leur état actuel
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.database import get_db
from app.services.leave_state_service import LeaveStateService

# Router indépendant pour ne pas perturber la structure existante
router = APIRouter(
    prefix="/api/leave-state",
    tags=["leave-state-demo"],
    responses={404: {"description": "Not found"}}
)


@router.get("/{leave_id}/info", response_model=Dict[str, Any])
def get_leave_state_info(
    leave_id: int = Path(..., description="ID de la demande de congé"),
    db: Session = Depends(get_db)
):
    """
    Récupère les informations sur l'état d'une demande de congé,
    y compris les transitions autorisées.
    """
    info = LeaveStateService.get_leave_state_info(db, leave_id)
    
    if not info["success"]:
        raise HTTPException(status_code=404, detail=info["message"])
    
    return info


@router.post("/{leave_id}/approve", response_model=Dict[str, Any])
def approve_leave(
    leave_id: int = Path(..., description="ID de la demande de congé"),
    approved_by: int = Query(..., description="ID de l'employé qui approuve"),
    db: Session = Depends(get_db)
):
    """
    Approuve une demande de congé.
    Cette action n'est possible que si la demande est dans l'état "en attente".
    """
    result = LeaveStateService.process_approval(db, leave_id, approved_by, approved=True)
    
    if not result["success"]:
        if "non trouvée" in result["message"]:
            raise HTTPException(status_code=404, detail=result["message"])
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.post("/{leave_id}/reject", response_model=Dict[str, Any])
def reject_leave(
    leave_id: int = Path(..., description="ID de la demande de congé"),
    rejected_by: int = Query(..., description="ID de l'employé qui rejette"),
    reason: Optional[str] = Query(None, description="Motif du rejet"),
    db: Session = Depends(get_db)
):
    """
    Rejette une demande de congé.
    Cette action n'est possible que si la demande est dans l'état "en attente".
    """
    result = LeaveStateService.process_approval(
        db, leave_id, rejected_by, approved=False, reason=reason
    )
    
    if not result["success"]:
        if "non trouvée" in result["message"]:
            raise HTTPException(status_code=404, detail=result["message"])
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.post("/{leave_id}/cancel", response_model=Dict[str, Any])
def cancel_leave(
    leave_id: int = Path(..., description="ID de la demande de congé"),
    cancelled_by: int = Query(..., description="ID de l'employé qui annule"),
    reason: Optional[str] = Query(None, description="Motif de l'annulation"),
    db: Session = Depends(get_db)
):
    """
    Annule une demande de congé.
    Cette action n'est possible que si la demande est dans l'état "en attente" ou "approuvé".
    """
    result = LeaveStateService.cancel_leave(db, leave_id, cancelled_by, reason)
    
    if not result["success"]:
        if "non trouvée" in result["message"]:
            raise HTTPException(status_code=404, detail=result["message"])
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


# Note: Pour activer ce routeur, ajouter la ligne suivante dans app/factories/app_factory.py:
# from app.api.leave_state_api import router as leave_state_api_router
# app.include_router(leave_state_api_router) 