from sqlalchemy.orm import Session
from app.models.evaluation import Evaluation
from app.schemas import EvaluationCreate
from fastapi import HTTPException

class EvaluationService:
    @staticmethod
    def create_evaluation(db: Session, evaluation_data: EvaluationCreate):
        new_evaluation = Evaluation(**evaluation_data.dict())
        db.add(new_evaluation)
        db.commit()
        db.refresh(new_evaluation)
        return new_evaluation

    @staticmethod
    def get_evaluation(db: Session, evaluation_id: int):
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        return evaluation

    @staticmethod
    def get_all_evaluations(db: Session):
        return db.query(Evaluation).all()
