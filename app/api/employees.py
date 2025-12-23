from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import EmployeeCreate, EmployeeUpdate, EmployeeRead
from app.services.employee_service import EmployeeService
from app.repositories.employee_repository import EmployeeRepository
from app.models.employee import Employee

router = APIRouter(prefix="/api/employees", tags=["Employees"])

"""
employees.py - Routes API REST pour la gestion des employés.

Responsabilités :
- Expose les endpoints CRUD (Create, Read, Update, Delete)
- Délègue la logique métier au service
- Utilise EmployeeRepository pour accéder aux données

Design patterns utilisés :
- Service (EmployeeService)
- Repository (EmployeeRepository)
"""


@router.get("/", response_model=list[EmployeeRead])
def get_all_employees(db: Session = Depends(get_db)):
    """
    Récupère la liste de tous les employés.
    """
    employees = EmployeeRepository.get_all(db)
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found")
    return employees


@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee_by_id(employee_id: int, db: Session = Depends(get_db)):
    """
    Récupère un employé par son identifiant unique.
    """
    employee = EmployeeRepository.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("/", response_model=EmployeeRead)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """
    Crée un nouvel employé dans la base de données.
    """
    return EmployeeService.create_employee(db, employee)


@router.put("/{employee_id}", response_model=EmployeeRead)
async def update_employee(employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    """
    Met à jour les informations d’un employé existant.
    """
    db_employee = EmployeeRepository.get_by_id(db, employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    updated_employee = EmployeeService.update_employee(db, db_employee, employee)
    return updated_employee


@router.patch("/{employee_id}", response_model=EmployeeRead)
async def partial_update_employee(employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    """
    Met à jour partiellement les informations d’un employé.
    """
    db_employee = EmployeeRepository.get_by_id(db, employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    updated_employee = EmployeeService.partial_update_employee(db, db_employee, employee)
    return updated_employee


@router.delete("/{employee_id}", response_model=str)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    Supprime un employé à partir de son identifiant.
    """
    db_employee = EmployeeRepository.get_by_id(db, employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    try:
        EmployeeRepository.delete(db, db_employee)
        return "Employee deleted successfully"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting employee: {str(e)}")


# Export pour import dans main.py
employee_router = router
