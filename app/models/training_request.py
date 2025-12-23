"""
training_request.py — Modèle de requête de formation faite par un employé.

Responsabilités :
- Représente une demande de participation à une formation.
- Suit le statut de la demande (en attente, approuvé, refusé).
- Permet d'associer un commentaire et un approbateur (le superviseur).

Design Patterns :
- Domain Model : une instance représente une demande de formation métier.
- Data Mapper : implémenté par SQLAlchemy pour la persistance.

Respect des principes SOLID :
- SRP : le modèle ne fait que représenter les données d'une demande de formation.
- OCP : facile à étendre (ex. : ajouter un champ de date, priorité, etc.).
- DIP : utilisé uniquement par la couche service, pas directement dans les routes.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class TrainingRequest(Base):
    """
    Requête de formation soumise par un employé pour une formation spécifique.

    Attributs :
    - id : identifiant unique de la requête
    - employee_id : identifiant de l'employé qui fait la demande
    - training_id : identifiant de la formation demandée
    - status : statut de la demande ("en attente", "approuvé", "refusé", etc.)
    - approved_by : ID du superviseur qui a validé/refusé
    - commentaire : commentaire ajouté par le superviseur

    Relations :
    - employee : lien vers l'employé demandeur
    - training : lien vers la formation concernée
    """

    __tablename__ = "training_requests"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    training_id = Column(Integer, ForeignKey("trainings.id", ondelete="CASCADE"), nullable=False)

    status = Column(String(20), default="en attente")  # Statut par défaut
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)  # Superviseur validateur
    commentaire = Column(Text, nullable=True)

    # Relations ORM
    employee = relationship("Employee", back_populates="training_requests", foreign_keys=[employee_id])
    training = relationship("Training", back_populates="requests")
