from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.objective import Objective
from app.schemas import ObjectiveCreate

router = APIRouter(prefix="/api/objectives", tags=["Objectives"])

@router.post("/")
def create_objective(objective: ObjectiveCreate, db: Session = Depends(get_db)):
    try:
        # Log pour le débogage
        print(f"Données reçues: {objective}")
        
        # Essayer avec Pydantic v2 (model_dump) puis se replier sur v1 (dict) si nécessaire
        try:
            # Pour Pydantic v2
            data = objective.model_dump()
        except AttributeError:
            # Pour Pydantic v1
            data = objective.dict()
            
        new_objective = Objective(**data)
        db.add(new_objective)
        db.commit()
        db.refresh(new_objective)
        return new_objective
    except Exception as e:
        # Log de l'erreur pour le débogage
        print(f"Erreur lors de la création d'un objectif: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création d'un objectif: {str(e)}")

# Fonction pour formater une date
def format_date(date_value):
    # Si date_value est déjà un objet datetime, on le formate directement
    if isinstance(date_value, datetime):
        return date_value.strftime("%Y-%m-%d")
    # Si c'est une chaîne de caractères, on essaie différents formats
    elif isinstance(date_value, str):
        try:
            # Essayer le format ISO avec heure
            date_obj = datetime.strptime(date_value, "%Y-%m-%dT%H:%M:%S")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            try:
                # Essayer le format date simple
                date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                # Retourner la valeur telle quelle si aucun format ne correspond
                return date_value
    return date_value  # Si ce n'est ni une chaîne, ni un datetime, on retourne la valeur telle quelle

@router.get("/{employee_id}")
def get_employee_objectives(employee_id: int, db: Session = Depends(get_db)):
    objectives = db.query(Objective).filter(Objective.employee_id == employee_id).all()
    
    # Retourner une liste vide au lieu de lever une exception
    if not objectives:
        return []
    
    # Formater les dates avant de renvoyer la réponse
    for objective in objectives:
        if hasattr(objective, 'start_date') and objective.start_date:
            objective.start_date = format_date(objective.start_date)
        if hasattr(objective, 'end_date') and objective.end_date:
            objective.end_date = format_date(objective.end_date)
    
    return objectives

objective_router = router