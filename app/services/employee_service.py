"""
EmployeeService - Couche métier pour la gestion des employés.

Responsabilités :
- Gérer la création, lecture, mise à jour et suppression des employés
- Isoler la logique métier de la couche API

Design Patterns :
- Service Layer : centralise la logique métier dans une couche intermédiaire
- Repository-like (accès direct SQLAlchemy encapsulé)
- DTO (via EmployeeCreate et EmployeeUpdate)

Respect des principes SOLID :
- SRP : chaque méthode a une responsabilité unique
- OCP : ouvert à l'extension (via partial_update), fermé à la modification
- DIP : les contrôleurs/API dépendent de ce service, et non directement de SQLAlchemy

"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, UTC

from app.models.employee import Employee
from app.models.leave_balance import LeaveBalance
from app.schemas import EmployeeCreate, EmployeeUpdate


class EmployeeService:

    @staticmethod
    def get_all_employees(db: Session) -> List[Employee]:
        """
        Récupère tous les employés.

        Returns:
            List[Employee]: Liste complète des employés.
        """
        return db.query(Employee).all()

    @staticmethod
    def get_supervisor(db: Session, supervisor_id: Optional[int]) -> Optional[Employee]:
        """
        Récupère un superviseur selon son ID.

        Args:
            supervisor_id (int | None): ID du superviseur.

        Returns:
            Employee | None
        """
        if supervisor_id is None:
            return None
        return db.query(Employee).filter(Employee.id == supervisor_id).first()

    @staticmethod
    def get_employee_by_email(db: Session, email: str) -> Optional[Employee]:
        """
        Recherche un employé par email.

        Args:
            email (str): Email de l'employé.

        Returns:
            Employee | None
        """
        return db.query(Employee).filter(Employee.email == email).first()

    @staticmethod
    def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
        """
        Crée un nouvel employé dans la base.

        Args:
            employee (EmployeeCreate): Données du nouvel employé.

        Returns:
            Employee: Employé créé.
        """
        db_employee = Employee(
            name=employee.name,
            email=employee.email,
            password=employee.password or "default_password",
            role=employee.role,
            department=employee.department,
            salary=employee.salary,
            experience=employee.experience,
            birth_date=employee.birth_date,
            hire_date=employee.hire_date,
            status=True,
            supervisor_id=employee.supervisor_id
        )

        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee

    @staticmethod
    def update_employee(db: Session, db_employee: Employee, employee: EmployeeUpdate) -> Employee:
        """
        Mise à jour complète d'un employé.

        Args:
            db_employee (Employee): Instance existante.
            employee (EmployeeUpdate): Nouvelles données.

        Returns:
            Employee: Employé mis à jour.
        """
        db_employee.name = employee.name or db_employee.name
        db_employee.email = employee.email or db_employee.email
        db_employee.role = employee.role or db_employee.role
        db_employee.department = employee.department or db_employee.department
        db_employee.salary = employee.salary or db_employee.salary
        db_employee.experience = employee.experience or db_employee.experience
        db_employee.birth_date = employee.birth_date or db_employee.birth_date
        db_employee.supervisor_id = employee.supervisor_id or db_employee.supervisor_id

        db.commit()
        db.refresh(db_employee)
        return db_employee

    @staticmethod
    def partial_update_employee(db: Session, db_employee: Employee, employee: EmployeeUpdate) -> Employee:
        """
        Mise à jour partielle d'un employé (seulement les champs fournis).

        Args:
            db_employee (Employee): Instance existante.
            employee (EmployeeUpdate): Données à mettre à jour.

        Returns:
            Employee: Employé mis à jour.
        """
        for key, value in employee.model_dump(exclude_unset=True).items():
            if hasattr(db_employee, key) and value is not None:
                setattr(db_employee, key, value)

        db.commit()
        db.refresh(db_employee)
        return db_employee

    @staticmethod
    def delete_employee(db: Session, employee_id: int):
        """
        Supprime un employé et ses soldes de congés.

        Args:
            employee_id (int): ID de l'employé à supprimer.

        Raises:
            ValueError: Si l'employé n'existe pas ou une erreur SQL survient.
        """
        try:
            db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee_id).delete()

            db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
            if not db_employee:
                raise ValueError("Employee not found")

            db.delete(db_employee)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise ValueError(f"Error deleting employee: {str(e)}")

    @staticmethod
    def add_employee(db: Session, employee_data: Dict[str, Any]) -> Tuple[bool, Optional[int]]:
        """
        Ajoute un nouvel employé dans la base de données.
        
        Args:
            db: Session de base de données
            employee_data: Données de l'employé à ajouter
            
        Returns:
            Tuple[bool, Optional[int]]: (Succès de l'opération, ID de l'employé créé si succès)
        """
        try:
            # Création d'un nouvel employé avec les données fournies
            new_employee = Employee(
                name=employee_data.get("name"),
                email=employee_data.get("email"),
                password=employee_data.get("password"),
                role=employee_data.get("role", "employee"),
                department=employee_data.get("department"),
                supervisor_id=employee_data.get("supervisor_id"),
                hire_date=employee_data.get("hire_date", datetime.now(UTC).date()),
                birth_date=employee_data.get("birth_date"),
                salary=employee_data.get("salary"),
                experience=employee_data.get("experience"),
                status=employee_data.get("status", True)
            )
            
            db.add(new_employee)
            db.flush()
            
            # Initialisation des soldes de congés pour le nouvel employé
            if employee_data.get("initialize_balances", True):
                from app.services.leave_service import LeaveService
                LeaveService.initialize_balances(db, new_employee.id)
            
            db.commit()
            return True, new_employee.id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Erreur lors de l'ajout de l'employé: {str(e)}")
            return False, None
