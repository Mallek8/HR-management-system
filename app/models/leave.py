"""
leave.py — Modèle représentant une demande de congé dans le système RH.

Responsabilités :
- Définir la structure de la table `leaves` (congés).
- Gérer les relations entre employés et superviseurs.

Design Patterns :
- Data Mapper : SQLAlchemy pour le mapping objet-relationnel.
- Domain Model : encapsule les règles métier de la demande de congé.

Respect des principes SOLID :
- SRP : ce modèle représente uniquement la structure d'une demande de congé.
- OCP : peut être étendu avec de nouveaux champs sans modifier le comportement existant.
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Leave(Base):
    """
    Représente une demande de congé soumise par un employé.

    Champs :
    - employee_id : identifiant de l'employé demandeur.
    - supervisor_id : identifiant du superviseur (facultatif).
    - start_date / end_date : période du congé.
    - type : nature du congé (vacances, maladie, formation...).
    - status : état de la demande (en attente, approuvé, refusé...).
    - admin_approved : statut d’approbation par un administrateur.
    - supervisor_comment : commentaire éventuel du superviseur.
    """

    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)

    # Clé étrangère vers l’employé qui fait la demande
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    # Période du congé
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    # Statut de la demande (en attente, approuvé, refusé)
    status = Column(String, default="en attente")

    # Type de congé (par défaut : Vacances)
    type = Column(String, default="Vacances")

    # Commentaire du superviseur (optionnel)
    supervisor_comment = Column(String, nullable=True)

    # Approbation par l'administrateur
    admin_approved = Column(Boolean, default=False)

    # Clé étrangère vers le superviseur en charge
    supervisor_id = Column(Integer, ForeignKey("employees.id"))

    # Relations ORM
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="leaves")
    supervisor = relationship("Employee", foreign_keys=[supervisor_id], back_populates="supervised_leaves")
