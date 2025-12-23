"""
training_plan.py — Modèle représentant un plan de formation attribué à un employé.

Responsabilités :
- Associer un employé à une formation après validation par le superviseur.
- Permettre le suivi des formations assignées aux employés.

Design Patterns :
- Domain Model : chaque instance représente un plan de formation attribué.
- Data Mapper : implémenté par SQLAlchemy pour la persistance.

Respect des principes SOLID :
- SRP : Ce modèle est uniquement responsable de la structure du plan de formation.
- OCP : Facile à étendre pour ajouter des champs comme statut, score, etc.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class TrainingPlan(Base):
    """
    Représente un plan de formation assigné à un employé.

    Attributs :
    - id : Identifiant unique du plan.
    - employee_id : Référence vers l'employé concerné.
    - training_id : Référence vers la formation attribuée.
    - created_at : Date de création du plan.
    """

    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    training_id = Column(Integer, ForeignKey("trainings.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    employee = relationship("Employee")
    training = relationship("Training")
