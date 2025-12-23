"""
evaluation.py — Modèle représentant une évaluation d'un employé.

Responsabilités :
- Définir la structure d'une évaluation dans la base de données.
- Associer une évaluation à un employé via une relation de type plusieurs-à-un.

Design Patterns :
- Data Mapper (via SQLAlchemy)
- Active Record (représente à la fois les données et le comportement de persistance)

Respect des principes SOLID :
- SRP : Ce modèle ne représente qu'une évaluation.
- OCP : Le modèle peut être étendu sans modifier son code existant.
"""

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Evaluation(Base):
    """
    Représente une évaluation de performance d'un employé.
    """
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)

    # Lien vers l'employé évalué
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    # Score de l'évaluation (ex : sur 100)
    score = Column(Integer, nullable=False)

    # Commentaire ou feedback textuel
    feedback = Column(String)

    # Date de l'évaluation (par défaut : maintenant)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    # Relation vers l'objet Employee (back_populates = "evaluations" dans Employee)
    employee = relationship("Employee", back_populates="evaluations")
