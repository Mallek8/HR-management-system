"""
leave_balance.py — Modèle représentant le solde de congés d'un employé.

Responsabilités :
- Définir la structure de la table `leave_balances`.
- Associer un solde à chaque employé via une relation un-à-un.

Design Patterns :
- Data Mapper : via SQLAlchemy pour le mapping objet-relationnel.

Respect des principes SOLID :
- SRP (Single Responsibility Principle) : représente uniquement le solde de congé.
- OCP (Open-Closed Principle) : peut être étendu avec de nouveaux champs ou logiques sans modifier la base.
"""

from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

class LeaveBalance(Base):
    """
    Représente le solde de congés d’un employé.

    - Un enregistrement correspond à un employé.
    - Le champ `balance` indique le nombre de jours restants.
    """
    __tablename__ = "leave_balances"

    # Identifiant unique
    id = Column(Integer, primary_key=True, index=True)

    # Clé étrangère vers l’employé (relation 1:1)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Solde de jours de congés disponibles
    balance = Column(Float, default=20.0)

    # Relation ORM vers l’objet Employee
    employee = relationship("Employee", overlaps="leave_balances")
