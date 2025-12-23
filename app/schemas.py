"""
schemas.py – Définition des schémas Pydantic utilisés pour la validation et
le transfert des données entre les couches (DTO).

Responsabilités :
- Définir les structures de données pour les entrées/sorties de l'API.
- Assurer la validation automatique grâce à Pydantic.
- Servir d'interface entre la base de données (SQLAlchemy) et la couche API.

Design Pattern :
- DTO (Data Transfer Object)

Respect SOLID :
- SRP : Ce module ne fait que valider les données.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import date, datetime

# -------------------------------------------------------
#  EMPLOYE SCHÉMAS
# -------------------------------------------------------

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    role: str
    hire_date: date
    status: Optional[bool] = False
    department: Optional[str]
    salary: Optional[float]
    experience: Optional[int]
    birth_date: Optional[date]
    supervisor_id: Optional[int]

class EmployeeCreate(EmployeeBase):
    password: Optional[str] = None

class EmployeeRead(EmployeeBase):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class EmployeeInDB(EmployeeRead):
    password: str  # Utilisé en interne pour inclure le mot de passe

class EmployeeStatusUpdate(BaseModel):
    status: bool

class ProfileUpdate(EmployeeBase):
    password: Optional[str] = None

class EmployeeUpdate(EmployeeBase):
    # Tous les champs deviennent optionnels pour permettre la mise à jour partielle
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = None
    experience: Optional[int] = None
    birth_date: Optional[date] = None
    hire_date: Optional[date] = None
    supervisor_id: Optional[int] = None


# -------------------------------------------------------
#  LEAVE (CONGÉS) SCHÉMAS
# -------------------------------------------------------

class LeaveBase(BaseModel):
    employee_id: int
    start_date: date
    end_date: date

class LeaveRead(LeaveBase):
    id: int
    start_date: datetime
    end_date: datetime
    status: str

    class Config:
        from_attributes = True  # Permet de mapper un modèle SQLAlchemy

class LeaveCreate(BaseModel):
    employee_id: int
    start_date: datetime
    end_date: datetime
    type: str = "Vacances"
    status: str = "en attente"
    admin_approved: bool = False
    supervisor_id: Optional[int] = None
    supervisor_comment: Optional[str] = None

    class Config:
        from_attributes = True

class LeaveRequest(BaseModel):
    employee_id: int
    start_date: datetime
    end_date: datetime

class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    start_date: datetime
    end_date: datetime
    status: str

    class Config:
        from_attributes = True  # Remplacer orm_mode par from_attributes pour Pydantic V2


# -------------------------------------------------------
#  TRAINING SCHÉMAS
# -------------------------------------------------------

class TrainingCreate(BaseModel):
    title: str
    description: str
    domain: str
    level: str
    start_date: date
    end_date: date
    target_department: str

class TrainingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    level: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_department: Optional[str] = None

class TrainingRead(TrainingCreate):
    id: int

    class Config:
        from_attributes = True


# -------------------------------------------------------
#  TRAINING REQUEST SCHÉMAS
# -------------------------------------------------------

class TrainingRequestCreate(BaseModel):
    employee_id: int
    training_id: int

class TrainingRequestRead(BaseModel):
    id: int
    employee_id: int
    training_id: int
    status: str
    approved_by: Optional[int] = None
    commentaire: Optional[str] = None

    class Config:
        from_attributes = True

class SupervisorValidation(BaseModel):
    decision: str  # "approuvé" ou "refusé"
    comment: Optional[str] = None


# -------------------------------------------------------
#  TRAINING PLAN SCHÉMAS
# -------------------------------------------------------

class TrainingPlanCreate(BaseModel):
    employee_id: int
    training_id: int

class TrainingPlanRead(BaseModel):
    id: int
    employee_id: int
    training_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# -------------------------------------------------------
#  EVALUATION SCHÉMAS
# -------------------------------------------------------
class EvaluationCreate(BaseModel):
    employee_id: int
    score: int
    feedback: str
    date: datetime = None  # Si aucune date n'est fournie, la date actuelle sera utilisée.

    class Config:
        orm_mode = True  # Permet à Pydantic de travailler avec des objets SQLAlchemy.

class EvaluationRead(EvaluationCreate):
    id: int

    class Config:
        orm_mode = True

# -------------------------------------------------------
#  OBJECTIVE SCHÉMAS
# -------------------------------------------------------
class ObjectiveCreate(BaseModel):
    employee_id: int
    description: str
    start_date: date
    end_date: date
    progress: Optional[int] = 0  # Progression en pourcentage (0-100)

    class Config:
        from_attributes = True  # Remplace orm_mode dans Pydantic v2

class ObjectiveRead(ObjectiveCreate):
    id: int

    class Config:
        from_attributes = True

# -------------------------------------------------------
#  EVENT SCHÉMAS
# -------------------------------------------------------
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    event_type: str
    employee_id: Optional[int] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_type: Optional[str] = None
    employee_id: Optional[int] = None

class EventRead(EventBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# -------------------------------------------------------
#  NOTIFICATION SCHÉMAS
# -------------------------------------------------------
class NotificationBase(BaseModel):
    employee_id: int
    message: str
    type: Optional[str] = "INFO"
    is_read: Optional[bool] = False
    title: Optional[str] = None
    link: Optional[str] = None
    reference_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    message: Optional[str] = None
    type: Optional[str] = None
    is_read: Optional[bool] = None
    title: Optional[str] = None
    link: Optional[str] = None

class NotificationRead(NotificationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True