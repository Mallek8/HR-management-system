"""
employee_role.py — Modèle de table d'association entre employés et rôles.

Responsabilités :
- Représente une liaison many-to-many entre les employés et les rôles.

Design Patterns :
- Data Mapper : SQLAlchemy mappe cette classe à une table relationnelle
- Association Table : motif classique de modélisation des relations many-to-many

Respect des principes SOLID :
- SRP : Représente uniquement la liaison entre `Employee` et `Role`
"""

from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class EmployeeRole(Base):
    """
    Table de liaison entre les employés et les rôles.
    Chaque ligne associe un employé à un rôle spécifique.
    """
    __tablename__ = "employee_roles"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
