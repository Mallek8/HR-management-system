"""
employee.py — Modèle de données représentant un employé.

Responsabilités :
- Définit la structure et les relations d'un employé dans la base de données.
- Sert de pivot central pour les relations avec les congés, évaluations, formations, etc.

Design Patterns :
- Data Mapper (via SQLAlchemy ORM)
- Active Record : le modèle porte les données et permet la persistance
- Aggregate Root : Employee est la racine de plusieurs agrégats (leaves, trainings, evaluations)

Respect des principes SOLID :
- SRP (Responsabilité unique) : représente uniquement l'état d'un employé.
- OCP : extensible via des colonnes ou relations additionnelles.
- DIP : les services accèdent à Employee via une couche d'abstraction (repository/service).
"""

from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class Employee(Base):
    """
    Modèle de la table `employees`.
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String)

    role = Column(String, nullable=False)
    department = Column(String)
    hire_date = Column(Date, nullable=False, default=datetime.now().date)
    birth_date = Column(Date, nullable=True)

    status = Column(Boolean, default=True)
    salary = Column(Float, nullable=True)
    experience = Column(Integer, nullable=True)

    supervisor_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    # Relations : Congés
    leaves = relationship(
        "Leave",
        foreign_keys="Leave.employee_id",
        back_populates="employee"
    )

    supervised_leaves = relationship(
        "Leave",
        foreign_keys="Leave.supervisor_id",
        back_populates="supervisor"
    )

    # Relations hiérarchiques
    supervised_employees = relationship(
        "Employee",
        foreign_keys=[supervisor_id],
        backref="supervisor",
        remote_side=[id]
    )

    # Évaluations liées à l'employé
    evaluations = relationship(
        "Evaluation",
        back_populates="employee",
        cascade="all, delete-orphan"
    )

    # Solde de congé unique
    leave_balances = relationship(
        "LeaveBalance",
        uselist=False
    )

    # Demandes de formations
    training_requests = relationship(
        "TrainingRequest",
        back_populates="employee",
        cascade="all, delete-orphan",
        foreign_keys="TrainingRequest.employee_id"
    )
    
    # Objectifs de l'employé
    objectives = relationship("Objective", back_populates="employee", cascade="all, delete-orphan")
