import pytest
from unittest.mock import MagicMock
from app.models.employee import Employee
from app.models.leave_balance import LeaveBalance
from app.models.training_request import TrainingRequest
from app.schemas import EmployeeCreate
from app.services.abstract_factory import EmployeeFactory

# Test que la création de l'employé fonctionne avec des données valides
def test_create_employee_valid():
    # Données simulées
    employee_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "securepassword123",
        "role": "Developer",
        "department": "Engineering",
        "hire_date": "2023-01-01",
        "birth_date": "1990-01-01",
        "status": True,
        "salary": 60000.0,
        "experience": 5,
    }

    # Simulation d'un schéma EmployeeCreate
    mock_employee_create_schema = MagicMock(spec=EmployeeCreate)
    mock_employee_create_schema.model_dump.return_value = employee_data

    # Appel à la méthode create_employee
    employee = EmployeeFactory.create_employee(mock_employee_create_schema)

    # Vérifier que l'objet Employee est créé avec les bonnes données
    assert isinstance(employee, Employee)
    assert employee.name == "John Doe"
    assert employee.email == "john.doe@example.com"
    assert employee.role == "Developer"
    assert employee.salary == 60000.0

