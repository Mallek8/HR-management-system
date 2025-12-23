"""
notification_api.py - Démo d'API pour le pattern Strategy des notifications

Cette API permet de :
- Envoyer des notifications via différents canaux
- Tester les différentes stratégies de notification

Design Pattern : Strategy
- Utilise EnhancedNotificationService qui implémente le pattern Strategy
- Montre comment utiliser différentes stratégies à travers une API REST

Note :
- Il s'agit d'une démonstration non intrusive qui n'affecte pas l'application existante
- Ces endpoints peuvent être utilisés en parallèle avec les fonctionnalités existantes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional

from app.database import get_db
from app.services.enhanced_notification_service import EnhancedNotificationService

# Création d'un routeur indépendant pour ne pas perturber la structure existante
router = APIRouter(
    prefix="/api/notification-strategy",
    tags=["notification-strategy-demo"],
    responses={404: {"description": "Not found"}},
)


@router.get("/channels", response_model=List[str])
def get_available_channels(db: Session = Depends(get_db)):
    """
    Récupère la liste des canaux de notification disponibles.
    """
    return EnhancedNotificationService.get_available_channels()


@router.post("/send/{employee_id}")
def send_notification(
    employee_id: int,
    message: str,
    channel: str = Query("in-app", description="Canal de notification à utiliser"),
    db: Session = Depends(get_db)
):
    """
    Envoie une notification à un employé via le canal spécifié.
    
    Exemple de canaux disponibles :
    - "in-app" (par défaut, utilise la base de données)
    - "email" (simulation)
    - "sms" (simulation)
    """
    success = EnhancedNotificationService.send_notification(
        db, employee_id, message, channel
    )
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail=f"Échec de l'envoi de la notification via le canal '{channel}'"
        )
    
    return {"success": True, "channel": channel, "message": message}


@router.post("/send-multi/{employee_id}")
def send_multi_channel_notification(
    employee_id: int,
    message: str,
    channels: Optional[List[str]] = Query(None, description="Canaux à utiliser (tous par défaut)"),
    db: Session = Depends(get_db)
):
    """
    Envoie une notification via plusieurs canaux.
    
    Si aucun canal n'est spécifié, la notification est envoyée via tous les canaux disponibles.
    """
    results = EnhancedNotificationService.send_multi_channel_notification(
        db, employee_id, message, channels
    )
    
    return {
        "success": any(results.values()),
        "results": results,
        "message": message
    }


# Note: Pour activer ce routeur, ajouter la ligne suivante dans app/main.py:
# from app.api.notification_api import router as notification_api_router
# app.include_router(notification_api_router) 