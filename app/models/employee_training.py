"""
employee_training.py — Modèle de liaison entre les employés et les formations suivies.

Responsabilités :
- Représente une association many-to-many entre `Employee` et `Training`.
- Permet de suivre quelles formations ont été attribuées ou suivies par chaque employé.

Design Patterns :
- Data Mapper : SQLAlchemy mappe cette classe vers la base de données.
- Association Table : motif pour les relations many-to-many enrichissables.

Respect des principes SOLID :
- SRP : Gère uniquement la relation entre employés et formations.
- DIP : Le code métier ne dépend pas de la base de données mais de ce modèle abstrait.

"""

from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class EmployeeTraining(Base):
    """
    Table d'association entre employés et formations.

    Chaque enregistrement représente une relation entre un employé et une formation.
    """
    __tablename__ = "employee_trainings"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    training_id = Column(Integer, ForeignKey("trainings.id", ondelete="CASCADE"), nullable=False)
