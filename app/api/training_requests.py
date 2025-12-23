from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.employee import Employee
from app.models.notification import Notification
from app.models.training import Training
from app.models.training_plan import TrainingPlan
from app.models.training_request import TrainingRequest
from app.schemas import SupervisorValidation, TrainingRead, TrainingRequestCreate, TrainingRequestRead
from app.services.training_plan_service import TrainingPlanService
"""
training_requests.py — API de gestion des demandes de formation

Responsabilités :
- Créer, envoyer et valider des demandes de formation
- Afficher les suggestions de formation
- Générer un plan de formation après validation

"""

training_request_router= APIRouter(prefix="/api/training-requests", tags=["Training Requests"])
templates = Jinja2Templates(directory="frontend/templates")

training_request_page_router = APIRouter()

@training_request_page_router.get("/training-request")
def show_training_request_form(request: Request):
    return templates.TemplateResponse("training_request.html", {"request": request})

@training_request_router.post("/", response_model=TrainingRequestRead)
def create_training_request(request: TrainingRequestCreate, db: Session = Depends(get_db)):
    # Vérifier s'il existe déjà une demande pour cette formation et cet employé
    existing = db.query(TrainingRequest).filter_by(
        employee_id=request.employee_id,
        training_id=request.training_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Demande déjà soumise pour cette formation.")

    new_request = TrainingRequest(**request.model_dump())
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

@training_request_router.get("/full")
def list_requests_full(db: Session = Depends(get_db)):
    requests = db.query(TrainingRequest).all()
    result = []
    for req in requests:
        result.append({
            "id": req.id,
            "status": req.status,
            "commentaire": req.commentaire,
            "employee_name": req.employee.name,
            "employee_email": req.employee.email,
            "training_title": req.training.title
        })
    return result
@training_request_router.post("/send-to-supervisor/{request_id}")

def send_to_supervisor(request_id: int, db: Session = Depends(get_db)):
    """
    Envoyer une demande de formation au superviseur de l'employé.
    Crée une notification dans la table `notifications`.
    """
    # Étape 1 : Récupération de la demande
    training_request = db.query(TrainingRequest).filter_by(id=request_id).first()
    if not training_request:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    # Étape 2 : Récupération de l'employé
    employee = db.query(Employee).filter_by(id=training_request.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé introuvable")

    # Étape 3 : Vérification du superviseur
    if not employee.supervisor_id:
        raise HTTPException(status_code=400, detail="Aucun superviseur assigné à cet employé")

    supervisor = db.query(Employee).filter_by(id=employee.supervisor_id).first()
    if not supervisor:
        raise HTTPException(status_code=404, detail="Superviseur introuvable")

    # Étape 4 : Création de la notification
    message = f"Nouvelle demande de formation de {employee.name} à valider."
    notification = Notification(employee_id=supervisor.id, message=message)

    db.add(notification)
    db.commit()
@training_request_router.get("/supervisor/requests")
def get_training_requests_for_supervisor(request: Request, db: Session = Depends(get_db)):
    user_email = request.cookies.get("user_email")

    supervisor = db.query(Employee).filter(Employee.email == user_email).first()
    if not supervisor:
        raise HTTPException(status_code=404, detail="Superviseur non trouvé")

    # On récupère les employés supervisés
    employees = db.query(Employee).filter(Employee.supervisor_id == supervisor.id).all()
    employee_ids = [emp.id for emp in employees]

    requests = db.query(TrainingRequest).filter(
        TrainingRequest.employee_id.in_(employee_ids),
        TrainingRequest.status == "en attente"
    ).all()

    result = []
    for req in requests:
        result.append({
            "id": req.id,
            "employee_name": req.employee.name,
            "employee_email": req.employee.email,
            "training_title": req.training.title,
            "status": req.status,
            "commentaire": req.commentaire
        })

    return result




@training_request_router.get("/employee/{employee_id}/training-plan")
def get_training_plan(employee_id: int, db: Session = Depends(get_db)):
    plans = db.query(TrainingPlan).filter_by(employee_id=employee_id).all()
    employee = db.query(Employee).filter_by(id=employee_id).first()
    if not employee:
      raise HTTPException(status_code=404, detail="Employé non trouvé")

    return [{
        "title": p.training.title,
        "start_date": p.training.start_date,
        "end_date": p.training.end_date,
        "domain": p.training.domain
    } for p in plans]
@training_request_router.post("/supervisor/validate/{request_id}")
def validate_training_request(
    request_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    decision = data.get("decision")
    comment = data.get("comment", "")

    # Vérification de la demande
    training_request = db.query(TrainingRequest).filter_by(id=request_id).first()
    if not training_request:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    # Validation de la décision
    if decision not in ["approuvé", "refusé"]:
        raise HTTPException(status_code=400, detail="Décision invalide")

    # Mise à jour du statut et commentaire
    training_request.status = decision
    training_request.manager_comment = comment

    # ✅ Génération du plan de formation si approuvé
    if decision == "approuvé":
        TrainingPlanService.generate_plan_if_approved(db, request_id)

    # Envoi d'une notification à l'employé
    message = f"Votre demande de formation '{training_request.training.title}' a été {decision}."
    notification = Notification(
        employee_id=training_request.employee_id,
        message=message
    )
    db.add(notification)

    db.commit()
    return {"message": "Décision enregistrée"}
@training_request_router.get("/suggestions", response_model=List[TrainingRead])
def suggest_trainings_by_profile(email: str, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.email == email).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    trainings = db.query(Training).filter(
        Training.target_department == employee.department
    ).all()
    return trainings
