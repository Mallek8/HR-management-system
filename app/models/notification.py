"""
notification.py — Modèle représentant une notification système liée à un employé.

Responsabilités :
- Représenter les messages informatifs envoyés aux employés.
- Relier chaque notification à un employé de manière claire.

Design Patterns :
- Data Mapper (via SQLAlchemy ORM).
- Domain Model : encapsule une entité métier simple.

Respect des principes SOLID :
- SRP (Responsabilité unique) : ce modèle gère uniquement la structure des notifications.
- OCP (Open/Closed Principle) : le modèle peut être étendu avec de nouveaux champs si besoin.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Notification(Base):
    """
    Représente une notification destinée à un employé (ex : approbation de congé, demande à valider, etc.).

    Champs :
    - id : identifiant unique de la notification.
    - employee_id : identifiant de l'employé concerné.
    - message : contenu textuel de la notification.
    - created_at : date/heure de création (défaut = maintenant).
    """

    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Clé étrangère vers l’employé destinataire de la notification
    employee_id = Column(Integer, ForeignKey('employees.id', ondelete='CASCADE'), nullable=False)

    # Message de la notification
    message = Column(String, nullable=False)

    # Timestamp de création
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relation vers Employee (non bidirectionnelle par défaut)
    employee = relationship('Employee')
