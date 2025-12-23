
"""
trainings.py — API de gestion des formations

Responsabilités :
- Affichage de la page des formations
- Création, modification, suppression et récupération de formations

Design Patterns :
- DTO (TrainingCreate, TrainingRead) pour échanger les données
- RESTful API : routes bien définies selon les verbes HTTP
- (possibilité future d'ajouter Service Layer / Repository si besoin)

Respect des principes SOLID :
- SRP : chaque route gère une seule responsabilité
- DIP : si un service est utilisé plus tard, les dépendances seront inversées
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.training import Training
from app.schemas import TrainingCreate, TrainingRead

# Moteur de templates pour la page HTML
templates = Jinja2Templates(directory="frontend/templates")

# Routeur principal pour les formations
router = APIRouter()

# ----------------------
# ROUTES HTML
# ----------------------

@router.get("/trainings", name="trainings_page")
async def trainings_page(request: Request):
    """
    Affiche la page HTML contenant le tableau des formations.
    """
    return templates.TemplateResponse("trainings.html", {"request": request})


# ----------------------
# API REST : Formations
# ----------------------

@router.get("/api/trainings", response_model=List[TrainingRead])
def get_all_trainings(db: Session = Depends(get_db)):
    """
    Récupère toutes les formations de la base de données.
    """
    trainings = db.query(Training).all()
    return trainings


@router.post("/api/trainings", response_model=TrainingRead)
def create_training(training: TrainingCreate, db: Session = Depends(get_db)):
    """
    Crée une nouvelle formation à partir des données fournies.
    """
    db_training = Training(
        title=training.title,
        description=training.description,
        domain=training.domain,
        level=training.level,
        start_date=training.start_date,
        end_date=training.end_date,
        target_department=training.target_department
    )
    db.add(db_training)
    db.commit()
    db.refresh(db_training)
    return db_training


@router.put("/api/trainings/{training_id}", response_model=TrainingRead)
def update_training(training_id: int, updated: TrainingCreate, db: Session = Depends(get_db)):
    """
    Met à jour une formation existante selon son ID.
    """
    db_training = db.query(Training).filter(Training.id == training_id).first()
    if not db_training:
        raise HTTPException(status_code=404, detail="Formation non trouvée")

    # Mise à jour des champs
    db_training.title = updated.title
    db_training.description = updated.description
    db_training.domain = updated.domain
    db_training.level = updated.level
    db_training.start_date = updated.start_date
    db_training.end_date = updated.end_date
    db_training.target_department = updated.target_department

    db.commit()
    db.refresh(db_training)
    return db_training


@router.delete("/api/trainings/{training_id}", status_code=204)
def delete_training(training_id: int, db: Session = Depends(get_db)):
    """
    Supprime une formation existante selon son ID.
    """
    db_training = db.query(Training).filter(Training.id == training_id).first()
    if not db_training:
        raise HTTPException(status_code=404, detail="Formation non trouvée")

    db.delete(db_training)
    db.commit()
    return  # Status 204 : pas de contenu


# Alias pour inclusion dans main.py
training_router = router
