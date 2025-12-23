"""
TrainingPlanService - Service pour la génération des plans de formation.

Responsabilités :
- Générer un plan de formation si une demande est approuvée.
- Vérifier qu’un plan n'existe pas déjà pour un employé donné.

Design pattern utilisé : Service
Pattern suggéré : Repository (si séparation des accès DB souhaitée)
"""

from sqlalchemy.orm import Session
from app.models.training_plan import TrainingPlan
from app.models.training_request import TrainingRequest


class TrainingPlanService:
    @staticmethod
    def generate_plan_if_approved(db: Session, request_id: int):
        """
        Génère un plan de formation pour un employé à partir d'une demande validée.

        - Vérifie si une demande de formation existe pour l'ID donné.
        - Vérifie si un plan a déjà été généré pour cet employé et cette formation.
        - Si ce n’est pas le cas, crée un nouveau plan de formation.

        Args:
            db (Session): La session SQLAlchemy.
            request_id (int): L'identifiant de la demande de formation.

        Returns:
            None
        """
        training_request = db.query(TrainingRequest).filter_by(id=request_id).first()

        if training_request:
            # Vérifie si un plan existe déjà
            existing_plan = db.query(TrainingPlan).filter_by(
                employee_id=training_request.employee_id,
                training_id=training_request.training_id
            ).first()

            if existing_plan:
                return  # Ne rien faire si le plan existe déjà

            # Crée et sauvegarde un nouveau plan
            plan = TrainingPlan(
                employee_id=training_request.employee_id,
                training_id=training_request.training_id
            )
            db.add(plan)
            db.commit()
