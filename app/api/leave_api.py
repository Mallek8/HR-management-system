from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models.leave import Leave
from app.models.employee import Employee
from app.models.department import Department
from app.models.leave_balance import LeaveBalance
from app.services.leave_service import LeaveService
from app.services.notification_service import NotificationService
from app.repositories.leave_repository import LeaveRepository
from app.repositories.employee_repository import EmployeeRepository
from app.services.leave_workflow_facade import LeaveWorkflowFacade
"""
Le fichier leave_api.py définit toutes les routes HTTP de
 l'API REST pour la gestion des demandes de congés.
Il utilise FastAPI pour exposer les endpoints, 
   et délègue la logique métier complexe à la façade LeaveWorkflowFacade.
"""
router = APIRouter(prefix="/api/leaves", tags=["Leaves"])
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)

# Utilitaire pour récupérer l'utilisateur courant à partir des cookies
def get_current_user(request: Request):
    user_email = request.cookies.get("user_email")
    user_role = request.cookies.get("user_role", "employee")
    return {"email": user_email, "role": user_role} if user_email else {"email": None, "role": None}

# ========================================
# EMPLOYÉS & DÉPARTEMENTS
# ========================================

@router.get("/employee/{email}")
def get_employee_by_email(email: str, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.email == email).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    return {
        "id": employee.id,
        "name": employee.name,
        "email": employee.email,
        "role": employee.role,
        "department_id": getattr(employee, "department_id", None),
        "position": getattr(employee, "position", None)
    }

@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    departments = db.query(Department).all()
    return [{"id": d.id, "name": d.name} for d in departments]

# ========================================
# DEMANDES DE CONGÉS
# ========================================

@router.get("/")
def list_leaves(db: Session = Depends(get_db)):
    query = text("""
        SELECT l.id, l.employee_id, l.start_date, l.end_date, l.status, l.type,
               e.name as employee_name
        FROM leaves l
        JOIN employees e ON l.employee_id = e.id
        ORDER BY l.start_date DESC
    """)
    result = db.execute(query)
    return [{
        "id": row.id,
        "employee_id": row.employee_id,
        "employee_name": row.employee_name,
        "start_date": row.start_date.strftime("%Y-%m-%d"),
        "end_date": row.end_date.strftime("%Y-%m-%d"),
        "status": row.status or "en attente",
        "type": row.type or "Congé"
    } for row in result]

@router.get("/all")
def list_all_leaves(db: Session = Depends(get_db)):
    query = text("""
        SELECT l.id, l.employee_id, l.start_date, l.end_date, l.status, l.type,
               e.name as employee_name, e.department as department_name
        FROM leaves l
        JOIN employees e ON l.employee_id = e.id
        ORDER BY l.start_date DESC
    """)
    result = db.execute(query)
    return [{
        "id": row.id,
        "employee_id": row.employee_id,
        "employee_name": row.employee_name,
        "department_id": None,
        "department_name": row.department_name,
        "start_date": row.start_date.strftime("%Y-%m-%d"),
        "end_date": row.end_date.strftime("%Y-%m-%d"),
        "status": row.status or "en attente",
        "type": row.type or "Congé"
    } for row in result]

@router.get("/calendar")
def get_calendar_events(
    start: str = Query(...),
    end: str = Query(...),
    department_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
    end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
    query = db.query(Leave).join(Employee, Leave.employee_id == Employee.id)
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    leaves = query.filter(
        Leave.start_date <= end_date,
        Leave.end_date >= start_date,
        Leave.status == "approuvé"
    ).all()
    return [{
        "id": leave.id,
        "title": f"{leave.employee.name} - Congé",
        "start": leave.start_date.isoformat(),
        "end": (leave.end_date + timedelta(days=1)).isoformat(),
        "allDay": True,
        "backgroundColor": "#3788d8"
    } for leave in leaves if leave.employee]

# ========================================
# SOLDE DE CONGÉS
# ========================================

@router.get("/balance/{employee_id}")
def get_leave_balance(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    default_balance = 25
    current_year = datetime.now().year
    start_of_year = datetime(current_year, 1, 1)
    query = text("""
        SELECT l.start_date, l.end_date FROM leaves l
        WHERE l.employee_id = :employee_id
        AND l.status = 'approuvé'
        AND l.type = 'Congé payé'
        AND l.start_date >= :start_of_year
    """)
    results = db.execute(query, {"employee_id": employee_id, "start_of_year": start_of_year}).fetchall()
    used_days = sum((r.end_date - r.start_date).days + 1 for r in results)
    remaining_balance = max(0, default_balance - used_days)
    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "balance": remaining_balance,
        "total_annual": default_balance,
        "used_days": used_days
    }

# ========================================
# VALIDATION / REJET / TRANSMISSION (FACADE)
# ========================================

@router.put("/{leave_id}/approve")
def approve_leave(leave_id: int, db: Session = Depends(get_db)):
    return LeaveWorkflowFacade.approve_by_admin(db, leave_id)

@router.put("/{leave_id}/reject")
def reject_leave(leave_id: int, db: Session = Depends(get_db)):
    return LeaveWorkflowFacade.reject_by_admin(db, leave_id)

@router.put("/{leave_id}/forward")
def forward_to_supervisor(leave_id: int, db: Session = Depends(get_db)):
    return LeaveWorkflowFacade.forward_to_supervisor(db, leave_id)

@router.put("/supervisor/{leave_id}/approve")
def supervisor_approve_leave(leave_id: int, request: Request, db: Session = Depends(get_db)):
    supervisor_email = request.cookies.get("user_email")
    return LeaveWorkflowFacade.approve_by_supervisor(db, supervisor_email, leave_id)

@router.put("/supervisor/{leave_id}/reject")
def supervisor_reject_leave(leave_id: int, request: Request, db: Session = Depends(get_db)):
    supervisor_email = request.cookies.get("user_email")
    return LeaveWorkflowFacade.reject_by_supervisor(db, supervisor_email, leave_id)

# ========================================
# SUPERVISEUR : DEMANDES EN ATTENTE
# ========================================

@router.get("/supervisor/requests")
def get_supervisor_requests(request: Request, db: Session = Depends(get_db)):
    supervisor_email = request.cookies.get("user_email")
    if not supervisor_email:
        raise HTTPException(status_code=401, detail="Non authentifié")
    supervisor = db.query(Employee).filter(Employee.email == supervisor_email).first()
    if not supervisor:
        raise HTTPException(status_code=404, detail="Superviseur non trouvé")
    requests = db.query(Leave).filter(
        Leave.supervisor_id == supervisor.id,
        Leave.status == "en attente sup"
    ).all()
    return [{
        "id": req.id,
        "employee_name": req.employee.name,
        "start_date": req.start_date.strftime("%Y-%m-%d"),
        "end_date": req.end_date.strftime("%Y-%m-%d"),
        "type": req.type or "Congé"
    } for req in requests]

# ========================================
# NOTIFICATIONS
# ========================================

@router.get("/notifications")
def get_employee_notifications(email: str, db: Session = Depends(get_db)):
    return LeaveService.get_notifications(db, email)

# ========================================
# CRÉATION DE DEMANDE DE CONGÉ
# ========================================

@router.post("/request")
async def create_leave_request(request: Request, db: Session = Depends(get_db)):
    """
    Crée une nouvelle demande de congé.
    """
    try:
        # Récupérer les données JSON du corps de la requête
        data = await request.json()
        
        # Récupérer l'email de l'employé
        email = data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email de l'employé manquant")
        
        # Récupérer l'employé par son email
        employee = db.query(Employee).filter(Employee.email == email).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
        
        # Créer une nouvelle demande de congé
        leave = Leave(
            employee_id=employee.id,
            start_date=datetime.fromisoformat(data.get("start_date")),
            end_date=datetime.fromisoformat(data.get("end_date")),
            type=data.get("leave_type", "Congé"),
            status="en attente",
            admin_approved=False,
            supervisor_id=None,
            supervisor_comment=data.get("comment")
        )
        
        # Sauvegarder dans la base de données
        db.add(leave)
        db.commit()
        db.refresh(leave)
        
        # Notifier les administrateurs
        NotificationService.send_notification_to_admin(
            db, 
            f"Nouvelle demande de congé de {employee.name} du {leave.start_date.strftime('%d/%m/%Y')} au {leave.end_date.strftime('%d/%m/%Y')}"
        )
        
        # Retourner les détails de la demande créée
        return {
            "id": leave.id,
            "employee_id": leave.employee_id,
            "employee_name": employee.name,
            "start_date": leave.start_date.strftime("%Y-%m-%d"),
            "end_date": leave.end_date.strftime("%Y-%m-%d"),
            "type": leave.type,
            "status": leave.status,
            "comment": leave.supervisor_comment
        }
        
    except Exception as e:
        print(f"Erreur lors de la création d'une demande de congé: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-availability")
async def check_leave_availability(request: Request, db: Session = Depends(get_db)):
    """
    Vérifie si les dates demandées sont disponibles pour un congé.
    """
    try:
        # Récupérer les données JSON du corps de la requête
        data = await request.json()
        
        # Récupérer l'email de l'employé
        email = data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email de l'employé manquant")
        
        # Récupérer l'employé par son email
        employee = db.query(Employee).filter(Employee.email == email).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
        
        # Récupérer les dates demandées
        start_date = datetime.fromisoformat(data.get("start_date"))
        end_date = datetime.fromisoformat(data.get("end_date"))
        
        # Vérifier si les dates sont cohérentes
        if start_date > end_date:
            return {
                "available": False,
                "reason": "La date de début doit être antérieure à la date de fin."
            }
        
        # Vérifier si l'employé a déjà des congés qui se chevauchent
        existing_leaves = db.query(Leave).filter(
            Leave.employee_id == employee.id,
            Leave.status.in_(["en attente", "approuvé"]),
            Leave.start_date <= end_date,
            Leave.end_date >= start_date
        ).all()
        
        if existing_leaves:
            return {
                "available": False,
                "reason": "Vous avez déjà une demande de congé pour cette période."
            }
        
        # Vérifier le solde de congés de l'employé
        leave_days = (end_date - start_date).days + 1
        
        # Obtenir le solde actuel
        leave_balance = db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee.id).first()
        balance = leave_balance.balance if leave_balance else 0
        
        if leave_days > balance:
            return {
                "available": False,
                "reason": f"Solde de congés insuffisant. Vous avez {balance} jours disponibles et demandez {leave_days} jours."
            }
        
        # Toutes les vérifications sont passées
        return {
            "available": True,
            "days": leave_days,
            "message": f"Ces dates sont disponibles. Durée du congé: {leave_days} jours."
        }
        
    except Exception as e:
        print(f"Erreur lors de la vérification de disponibilité: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# INITIALISATION (au démarrage de l'app)
# ========================================

def initialize_departments(db: Session):
    default_departments = ["Ressources Humaines", "Informatique", "Finance", "Marketing"]
    for idx, name in enumerate(default_departments, start=1):
        if not db.query(Department).filter(Department.name == name).first():
            db.add(Department(id=idx, name=name))
    db.commit()

leave_router = router
