from fastapi import APIRouter, Query, Request, Depends, HTTPException, logger
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates  # Import de Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.employee import Employee
from app.models.leave import Leave
from app.models.leave_balance import LeaveBalance
from app.schemas import EmployeeRead, LeaveCreate, LeaveRequest, LeaveResponse
from typing import List
from app.models.department import Department
from app.services.employee_service import EmployeeService
from app.services.leave_request_service import LeaveRequestService

# Initialiser le répertoire pour les templates Jinja2
templates = Jinja2Templates(directory="frontend/templates")

# Définir un routeur pour les demandes de congé
leave_requests_router = APIRouter(prefix="/request-leave", tags=["Leave Requests"])

# Définir un routeur pour les notifications
notification_router = APIRouter(prefix="/notifications", tags=["Notifications"])
api_router = APIRouter(prefix="/api", tags=["API"])

# Route pour afficher la page de notifications
@notification_router.get("/")
async def get_notifications(request: Request):
    """
    Récupère toutes les notifications et rend la page des notifications.
    """
    return templates.TemplateResponse("notifications.html", {"request": request})

# Route pour afficher le formulaire de demande de congé
@leave_requests_router.get("/", response_class=HTMLResponse)
async def request_leave_page(request: Request, db: Session = Depends(get_db)):
    """
    Cette route affiche le formulaire de demande de congé.
    """
    # Get the employee from the token/cookie
    user_email = request.cookies.get("user_email")
    if not user_email:
        raise HTTPException(status_code=403, detail="Non authentifié")
    
    employee = EmployeeService.get_employee_by_email(db, user_email)
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Add current_user context
    current_user = {
        "username": employee.name,
        "role": employee.role,
        "is_admin": employee.role == "admin"
    }
    
    return templates.TemplateResponse("request_leave.html", {
        "request": request, 
        "employee": employee,
        "current_user": current_user
    })

@leave_requests_router.get("/all", response_model=List[LeaveResponse])
async def get_leave_requests(db: Session = Depends(get_db)):
    """
    Récupère toutes les demandes de congé.
    """
    leave_requests = db.query(Leave).all()  # Vous pouvez filtrer selon le statut ou d'autres critères
    if not leave_requests:
        raise HTTPException(status_code=404, detail="Aucune demande de congé trouvée")
    return leave_requests

# Route pour créer une nouvelle demande de congé
@leave_requests_router.post("/")
async def create_leave(leave: LeaveCreate, db: Session = Depends(get_db)):
    """Create a new leave request."""
    try:
        # Créer la demande de congé
        new_leave = Leave(
            employee_id=leave.employee_id,
            start_date=leave.start_date,
            end_date=leave.end_date,
            type=leave.type,
            status="en attente",
            admin_approved=False,
            supervisor_id=None
        )
        db.add(new_leave)
        db.commit()
        db.refresh(new_leave)

        # Renvoyer tous les champs nécessaires dans la réponse
        return {
            "id": new_leave.id,
            "employee_id": new_leave.employee_id,
            "start_date": new_leave.start_date,
            "end_date": new_leave.end_date,
            "type": new_leave.type,
            "status": new_leave.status,
            "admin_approved": new_leave.admin_approved,
            "supervisor_id": new_leave.supervisor_id
        }

    except Exception as e:
        print(f"Exception générale: {str(e)}")
        import traceback
        print("Traceback complet:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur inattendue: {str(e)}")

@leave_requests_router.get("/by-email", response_model=EmployeeRead)
async def get_employee_by_email(
    email: str = Query(..., regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"), 
    db: Session = Depends(get_db)
):
    """Récupérer un employé par son email."""
    print(f"API /request-leave/by-email appelée avec email: {email}")
    try:
        # Nettoyer l'email (supprimer les guillemets s'ils existent)
        clean_email = email
        if clean_email.startswith('"') and clean_email.endswith('"'):
            clean_email = clean_email[1:-1]
    
        # Recherche de l'employé
        employee = db.query(Employee).filter(Employee.email == clean_email).first()
        
        if not employee:
            # Si non trouvé, essayer avec l'email original
            employee = db.query(Employee).filter(Employee.email == email).first()
        
        if not employee:
            print(f"Aucun employé trouvé avec email: {clean_email} ou {email}")
            raise HTTPException(status_code=404, detail="Employee not found")
        
        print(f"Employé trouvé: {employee.name}, ID: {employee.id}")
        return employee
    except Exception as e:
        print(f"ERREUR get_employee_by_email: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@leave_requests_router.get("/employees/{employee_id}/leave-balance")
async def get_leave_balance(employee_id: int, db: Session = Depends(get_db)):
    """
    Récupère le solde de congés pour un employé donné.
    """
    leave_balance = db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee_id).first()
    if not leave_balance:
        raise HTTPException(status_code=404, detail="Solde de congés introuvable")
    return {"balance": leave_balance.balance}

def initialize_leave_balances(db: Session):
    employees = db.query(Employee).all()
    for employee in employees:
        if not db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee.id).first():
            db.add(LeaveBalance(employee_id=employee.id, balance=0))  # Exemple : 0 jours de congés
    db.commit()

@leave_requests_router.get("/notifications")
async def get_employee_notifications(
    email: str = Query(..., regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"),
    db: Session = Depends(get_db)
):
    """Récupérer les notifications d'un employé."""
    try:
        # Nettoyer l'email
        clean_email = email.replace('"', '')
        
        # Récupérer l'employé
        employee = db.query(Employee).filter(Employee.email == clean_email).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Récupérer les demandes de congé de l'employé
        leaves = db.query(Leave).filter(Leave.employee_id == employee.id).all()
        
        # Créer les notifications
        notifications = []
        for leave in leaves:
            notification = {
                "id": leave.id,
                "created_at": leave.created_at.isoformat() if leave.created_at else None,
                "message": f"Votre demande de congé du {leave.start_date} au {leave.end_date} est {leave.status}.",
                "status": leave.status
            }
            notifications.append(notification)
        
        return notifications
    except Exception as e:
        print(f"Erreur lors de la récupération des notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@leave_requests_router.get("/team-absences")
async def get_team_absences(db: Session = Depends(get_db)):
    """Récupère les absences de l'équipe."""
    try:
        # Récupérer toutes les demandes de congés approuvées
        query = (
            db.query(
                Leave,
                Employee.name.label("employee_name"),
                Department.name.label("department_name")
            )
            .join(Employee, Leave.employee_id == Employee.id)
            .join(Department, Employee.department_id == Department.id)
            .filter(Leave.status == "approuvé")
            .order_by(Leave.start_date.desc())
        )
        
        absences = query.all()
        
        # Formater les résultats
        result = []
        for absence, employee_name, department_name in absences:
            result.append({
                "id": absence.id,
                "employee_id": absence.employee_id,
                "employee_name": employee_name,
                "department_name": department_name,
                "start_date": absence.start_date.strftime("%Y-%m-%d"),
                "end_date": absence.end_date.strftime("%Y-%m-%d"),
                "type": absence.type,
                "status": absence.status,
                "days": (absence.end_date - absence.start_date).days + 1
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des absences: {str(e)}"
        )

@leave_requests_router.get("/leaves-dashboard")
async def leave_requests_dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard des demandes de congé"""
    # Get user email from cookie
    user_email = request.cookies.get("user_email")
    if not user_email:
        raise HTTPException(status_code=403, detail="Non authentifié")
    
    employee = EmployeeService.get_employee_by_email(db, user_email)
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Add current_user context
    current_user = {
        "username": employee.name,
        "role": employee.role,
        "is_admin": employee.role == "admin"
    }
    
    # Get leave requests based on user role
    if employee.role in ["admin", "rh"]:
        # For admins and HR, show all requests
        leave_requests = LeaveRequestService.get_all_leave_requests(db)
    elif employee.role == "manager":
        # For managers, show requests from their team members
        leave_requests = LeaveRequestService.get_team_leave_requests(db, employee.id)
    else:
        # For regular employees, show only their requests
        leave_requests = LeaveRequestService.get_employee_leave_requests(db, employee.id)
    
    return templates.TemplateResponse("leave_requests.html", {
        "request": request, 
        "leave_requests": leave_requests,
        "current_user": current_user
    })