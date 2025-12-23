"""
event.py - Modèle représentant un événement système.

Responsabilités :
- Représenter les événements du système (demandes de congé, formations, etc.)
- Relier chaque événement à un employé si applicable

Design Patterns :
- Data Mapper (via SQLAlchemy ORM)
- Domain Model : encapsule une entité métier
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Event(Base):
    """
    Représente un événement dans le système (demande de congé, formation, etc.).

    Champs :
    - id : identifiant unique de l'événement
    - title : titre de l'événement
    - description : description de l'événement (optionnel)
    - start_date : date/heure de début
    - end_date : date/heure de fin
    - event_type : type d'événement (string)
    - employee_id : identifiant de l'employé concerné (optionnel)
    - created_at : date/heure de création (défaut = maintenant)
    """

    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Informations de base
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Type d'événement
    event_type = Column(String, nullable=False)
    
    # Relation avec l'employé (optionnel)
    employee_id = Column(Integer, ForeignKey('employees.id', ondelete='CASCADE'), nullable=True)
    
    # Timestamp de création
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation vers Employee
    employee = relationship('Employee', foreign_keys=[employee_id])

