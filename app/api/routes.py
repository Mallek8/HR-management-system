from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.leave_service import LeaveService
from app.models.employee import Employee
from app.database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/employees/by-email/{email}")
async def get_employee_by_email(email: str, db: Session = Depends(get_db)):
    """
    Récupère les détails d'un employé par son email
    """
    try:
        employee = db.query(Employee).filter(Employee.email == email).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
        
        # Rechercher le superviseur si l'employé en a un
        supervisor = None
        if employee.supervisor_id:
            supervisor = db.query(Employee).filter(Employee.id == employee.supervisor_id).first()
        
        return {
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "role": employee.role,
            "department": employee.department,
            "hire_date": employee.hire_date,
            "supervisor_id": employee.supervisor_id,
            "supervisor_name": supervisor.name if supervisor else None
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'employé par email: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur serveur lors de la récupération de l'employé")

@router.get("/leaves/balance/{employee_id}")
async def get_leave_balance(employee_id: int, db: Session = Depends(get_db)):
    """
    Récupère le solde de congés d'un employé
    """
    try:
        balance = LeaveService.get_leave_balance(db, employee_id)
        return {"balance": balance}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du solde de congés: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur serveur lors de la récupération du solde de congés") 