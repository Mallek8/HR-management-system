# app/routes/users.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.schemas import EmployeeCreate, EmployeeRead

# -----------------------------------------------------------------------
# Définition du routeur pour les routes liées aux employés
# -----------------------------------------------------------------------
router = APIRouter(prefix="/employees", tags=["Employés"])


# -----------------------------------------------------------------------
# Création d’un nouvel employé
# -----------------------------------------------------------------------
@router.post("/", response_model=EmployeeRead)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


# -----------------------------------------------------------------------
# Récupération d’un employé par son ID
# -----------------------------------------------------------------------
@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    return employee


# -----------------------------------------------------------------------
# Liste de tous les employés
# -----------------------------------------------------------------------
@router.get("/", response_model=list[EmployeeRead])
def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


# -----------------------------------------------------------------------
# Mise à jour d’un employé existant
# -----------------------------------------------------------------------
@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee(employee_id: int, updated_employee: EmployeeCreate, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    for key, value in updated_employee.dict().items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)
    return employee


# -----------------------------------------------------------------------
# Suppression d’un employé
# -----------------------------------------------------------------------
@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    db.delete(employee)
    db.commit()
    return {"message": "Employé supprimé avec succès"}
