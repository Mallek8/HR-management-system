"""
event_types.py - Définition des types d'événements pour le pattern Observer

Ce module définit les types d'événements qui peuvent être observés
dans l'application. Chaque type d'événement est représenté par une
constante unique.

Design Pattern : Observer (composant "Event Types")
- Standardise les types d'événements dans l'application
- Facilite l'accès et la référence aux types d'événements
"""

from enum import Enum, auto


class EventType(Enum):
    """
    Types d'événements qui peuvent être observés dans l'application.
    """
    
    # Événements liés aux demandes de congé
    LEAVE_REQUESTED = auto()
    LEAVE_APPROVED = auto()
    LEAVE_REJECTED = auto()
    LEAVE_CANCELLED = auto()
    
    # Événements liés aux employés
    EMPLOYEE_CREATED = auto()
    EMPLOYEE_UPDATED = auto()
    EMPLOYEE_DELETED = auto()
    
    # Événements liés aux évaluations
    EVALUATION_CREATED = auto()
    EVALUATION_UPDATED = auto()
    
    # Événements liés aux formations
    TRAINING_ASSIGNED = auto()
    TRAINING_COMPLETED = auto()
    
    # Événements liés aux objectifs
    OBJECTIVE_CREATED = auto()
    OBJECTIVE_COMPLETED = auto()
    
    # Événements divers
    NOTIFICATION_SENT = auto()
    SYSTEM_ALERT = auto() 