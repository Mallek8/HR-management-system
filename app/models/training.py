"""
training.py — Modèle représentant une formation dans le système RH.

Responsabilités :
- Définit les attributs d'une formation proposée aux employés.
- Gère les relations avec les demandes de formation.

Design Patterns :
- Domain Model : chaque instance représente une entité métier "Formation".
- Data Mapper : persistance via SQLAlchemy (mapping objet-relationnel).

Respect des principes SOLID :
- SRP : la classe ne fait que modéliser les données de la formation.
- OCP : facilement extensible avec des champs supplémentaires (ex. : lieu, formateur, coût).
- LSP : utilisable dans toutes les fonctions attendues comme instance de base métier.
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Training(Base):
    """
    Modèle représentant une formation disponible pour les employés.

    Attributs :
    - id : identifiant unique de la formation
    - title : nom de la formation
    - description : résumé ou détails de la formation
    - domain : domaine concerné (ex. : 'Informatique', 'Marketing')
    - level : niveau de la formation (débutant, intermédiaire, avancé)
    - start_date / end_date : dates de début et fin de la session
    - target_department : département ciblé par la formation

    Relations :
    - requests : liste des demandes faites par les employés pour cette formation
    """

    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    domain = Column(String(100), nullable=True)  # Ex : "Développement", "Gestion"
    level = Column(String(50), nullable=True)    # Ex : "Débutant", "Intermédiaire", "Avancé"
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    target_department = Column(String(100), nullable=True)

    # === Relations ===
    requests = relationship(
        "TrainingRequest",
        back_populates="training",
        cascade="all, delete-orphan"
    )
