"""
role.py — Modèle représentant un rôle (admin, superviseur, employé, etc.)

Responsabilités :
- Définir les types de rôles disponibles dans le système.
- Être référencé dans les relations de gestion des autorisations (ex : table `employee_roles`).

Design Patterns :
- Domain Model : chaque instance représente un rôle du système.
- Data Mapper : via SQLAlchemy.

Respect des principes SOLID :
- SRP (Responsabilité unique) : le modèle ne représente que la structure des rôles.
- OCP (Open/Closed Principle) : il peut être étendu sans modifier les classes existantes (ex : ajout d’un champ description).

"""

from sqlalchemy import Column, Integer, String
from app.database import Base

class Role(Base):
    """
    Représente un rôle d'utilisateur dans le système RH.
    (ex : 'admin', 'superviseur', 'employé').

    Champs :
    - id : identifiant unique du rôle.
    - name : nom du rôle (unique et obligatoire).
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
