from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.evaluation import Evaluation
from app.schemas import EvaluationCreate, EvaluationRead
from app.services.evaluation_service import EvaluationService


router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])
# Initialiser le répertoire pour les templates Jinja2
templates = Jinja2Templates(directory="frontend/templates")
# Servir les fichiers statiques du répertoire 'static'

@router.get("/page", response_class=HTMLResponse)
async def get_evaluations_page(request: Request):
    """
    Route pour afficher la page des évaluations.
    """
    return templates.TemplateResponse("evaluations.html", {"request": request})

@router.post("/", response_model=EvaluationRead)
def create_evaluation(
    evaluation: EvaluationCreate, db: Session = Depends(get_db)
):
    return EvaluationService.create_evaluation(db, evaluation)

@router.get("/{evaluation_id}", response_model=EvaluationRead)
def get_evaluation(
    evaluation_id: int, db: Session = Depends(get_db)
):
    return EvaluationService.get_evaluation(db, evaluation_id)

@router.get("/", response_model=List[EvaluationRead])
def get_all_evaluations(db: Session = Depends(get_db)):
    return EvaluationService.get_all_evaluations(db)

@router.get("/api/evaluations/{employee_id}")
async def get_employee_evaluations(employee_id: int, db: Session = Depends(get_db)):
    evaluations = db.query(Evaluation).filter(Evaluation.employee_id == employee_id).all()
    if not evaluations:
        raise HTTPException(status_code=404, detail="Aucune évaluation trouvée pour cet employé")
    return evaluations


evaluation_router=router