import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, datetime, UTC

from app.services.employee_service import EmployeeService
from app.models.employee import Employee
from app.models.leave_balance import LeaveBalance
from app.schemas import EmployeeCreate, EmployeeUpdate


@pytest.fixture
def mock_db_session():
    """Fixture pour créer un mock de session de base de données"""
    session = MagicMock()
    session.query.return_value = session
    session.filter.return_value = session
    session.first.return_value = None
    session.all.return_value = []
    return session


@pytest.fixture
def mock_employee():
    """Fixture pour créer un mock d'employé"""
    employee = MagicMock(spec=Employee)
    employee.id = 1
    employee.name = "Jean Dupont"
    employee.email = "jean.dupont@example.com"
    employee.role = "employee"
    employee.department = "IT"
    employee.salary = 50000
    employee.experience = 5
    employee.birth_date = date(1985, 1, 1)
    employee.hire_date = date(2020, 1, 1)
    employee.status = True
    employee.supervisor_id = 2
    return employee


def test_get_all_employees(mock_db_session, mock_employee):
    """Test la récupération de tous les employés"""
    # Arrange
    mock_db_session.all.return_value = [mock_employee]
    
    # Act
    result = EmployeeService.get_all_employees(mock_db_session)
    
    # Assert
    assert len(result) == 1
    assert result[0] == mock_employee
    mock_db_session.query.assert_called_once_with(Employee)


def test_get_supervisor_found(mock_db_session, mock_employee):
    """Test la récupération d'un superviseur existant"""
    # Arrange
    supervisor_id = 2
    mock_db_session.first.return_value = mock_employee
    
    # Act
    result = EmployeeService.get_supervisor(mock_db_session, supervisor_id)
    
    # Assert
    assert result == mock_employee
    mock_db_session.query.assert_called_once_with(Employee)
    mock_db_session.filter.assert_called_once()


def test_get_supervisor_none_id(mock_db_session):
    """Test la récupération d'un superviseur avec ID None"""
    # Act
    result = EmployeeService.get_supervisor(mock_db_session, None)
    
    # Assert
    assert result is None
    mock_db_session.query.assert_not_called()


def test_get_supervisor_not_found(mock_db_session):
    """Test la récupération d'un superviseur inexistant"""
    # Arrange
    supervisor_id = 999
    mock_db_session.first.return_value = None
    
    # Act
    result = EmployeeService.get_supervisor(mock_db_session, supervisor_id)
    
    # Assert
    assert result is None
    mock_db_session.query.assert_called_once_with(Employee)


def test_get_employee_by_email_found(mock_db_session, mock_employee):
    """Test la récupération d'un employé par email avec succès"""
    # Arrange
    email = "jean.dupont@example.com"
    mock_db_session.first.return_value = mock_employee
    
    # Act
    result = EmployeeService.get_employee_by_email(mock_db_session, email)
    
    # Assert
    assert result == mock_employee
    mock_db_session.query.assert_called_once_with(Employee)
    mock_db_session.filter.assert_called_once()


def test_get_employee_by_email_not_found(mock_db_session):
    """Test la récupération d'un employé par email non trouvé"""
    # Arrange
    email = "unknown@example.com"
    mock_db_session.first.return_value = None
    
    # Act
    result = EmployeeService.get_employee_by_email(mock_db_session, email)
    
    # Assert
    assert result is None
    mock_db_session.query.assert_called_once_with(Employee)


def test_create_employee(mock_db_session):
    """Test la création d'un employé"""
    # Arrange
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()
    
    employee_data = EmployeeCreate(
        name="Pierre Martin",
        email="pierre.martin@example.com",
        password="secret",
        role="employee",
        department="Marketing",
        salary=60000,
        experience=3,
        birth_date=date(1990, 5, 15),
        hire_date=date(2021, 3, 1),
        supervisor_id=2
    )
    
    # Act
    result = EmployeeService.create_employee(mock_db_session, employee_data)
    
    # Assert
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()
    assert isinstance(result, Employee)


def test_update_employee(mock_db_session, mock_employee):
    """Test la mise à jour complète d'un employé"""
    # Arrange
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()
    
    update_data = EmployeeUpdate(
        name="Jean Dupont Modifié",
        email="jean.modifie@example.com",
        role="manager",
        department="HR",
        salary=55000,
        experience=6,
        birth_date=date(1985, 1, 1),
        supervisor_id=3
    )
    
    # Act
    result = EmployeeService.update_employee(mock_db_session, mock_employee, update_data)
    
    # Assert
    assert result == mock_employee
    assert mock_employee.name == "Jean Dupont Modifié"
    assert mock_employee.email == "jean.modifie@example.com"
    assert mock_employee.role == "manager"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_employee)


def test_partial_update_employee(mock_db_session, mock_employee):
    """Test la mise à jour partielle d'un employé"""
    # Arrange
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()
    
    # Mise à jour partielle (seulement le salaire)
    update_data = EmployeeUpdate(salary=60000)
    
    # Act
    result = EmployeeService.partial_update_employee(mock_db_session, mock_employee, update_data)
    
    # Assert
    assert result == mock_employee
    assert mock_employee.salary == 60000
    # Les autres champs ne doivent pas être modifiés
    assert mock_employee.name == "Jean Dupont"
    assert mock_employee.email == "jean.dupont@example.com"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_employee)


def test_delete_employee_success(mock_db_session, mock_employee):
    """Test la suppression réussie d'un employé"""
    # Arrange
    employee_id = 1
    mock_db_session.query.side_effect = lambda model: {
        Employee: MagicMock(filter=lambda *args: MagicMock(first=lambda: mock_employee)),
        LeaveBalance: MagicMock(filter=lambda *args: MagicMock(delete=MagicMock()))
    }[model]
    
    mock_db_session.delete = MagicMock()
    mock_db_session.commit = MagicMock()
    
    # Act
    EmployeeService.delete_employee(mock_db_session, employee_id)
    
    # Assert
    mock_db_session.delete.assert_called_once_with(mock_employee)
    mock_db_session.commit.assert_called_once()


def test_delete_employee_not_found(mock_db_session):
    """Test la suppression d'un employé inexistant"""
    # Arrange
    employee_id = 999
    mock_db_session.query.side_effect = lambda model: {
        Employee: MagicMock(filter=lambda *args: MagicMock(first=lambda: None)),
        LeaveBalance: MagicMock(filter=lambda *args: MagicMock(delete=MagicMock()))
    }[model]
    
    # Act & Assert
    with pytest.raises(ValueError, match="Employee not found"):
        EmployeeService.delete_employee(mock_db_session, employee_id)
    
    mock_db_session.commit.assert_not_called()


def test_delete_employee_sql_error(mock_db_session, mock_employee):
    """Test l'échec de la suppression à cause d'une erreur SQL"""
    # Arrange
    employee_id = 1
    mock_db_session.query.side_effect = lambda model: {
        Employee: MagicMock(filter=lambda *args: MagicMock(first=lambda: mock_employee)),
        LeaveBalance: MagicMock(filter=lambda *args: MagicMock(delete=MagicMock()))
    }[model]
    
    mock_db_session.delete = MagicMock()
    mock_db_session.commit = MagicMock(side_effect=SQLAlchemyError("Database error"))
    mock_db_session.rollback = MagicMock()
    
    # Act & Assert
    with pytest.raises(ValueError, match="Error deleting employee"):
        EmployeeService.delete_employee(mock_db_session, employee_id)
    
    mock_db_session.rollback.assert_called_once()


def test_add_employee_success(mock_db_session):
    """Test l'ajout réussi d'un employé avec add_employee"""
    # Arrange
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.flush = MagicMock()
    
    # Utiliser les attributs corrects qui correspondent à la classe Employee
    employee_data = {
        "name": "Sophie Dubois",
        "email": "sophie.dubois@example.com",
        "password": "password123",
        "role": "employee",
        "department": "IT",
        "supervisor_id": 2
    }
    
    # Créer un mock pour l'employé créé
    mock_employee = MagicMock(spec=Employee)
    mock_employee.id = 5
    
    # Simuler l'ajout d'un employé
    mock_db_session.add.side_effect = lambda employee: setattr(employee, 'id', 5)
    
    # Mock pour LeaveService
    with patch('app.services.leave_service.LeaveService') as mock_leave_service:
        mock_leave_service.initialize_balances = MagicMock()
        
        # Act
        success, employee_id = EmployeeService.add_employee(mock_db_session, employee_data)
        
        # Assert
        assert success is True
        assert employee_id == 5
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_leave_service.initialize_balances.assert_called_once_with(mock_db_session, 5)


def test_add_employee_failure(mock_db_session):
    """Test l'échec de l'ajout d'un employé"""
    # Arrange
    mock_db_session.add = MagicMock(side_effect=SQLAlchemyError("Database error"))
    mock_db_session.rollback = MagicMock()
    
    # Utiliser les attributs corrects
    employee_data = {
        "name": "Sophie Dubois",
        "email": "sophie.dubois@example.com",
        "password": "password123"
    }
    
    # Act
    with patch('builtins.print') as mock_print:
        success, employee_id = EmployeeService.add_employee(mock_db_session, employee_data)
    
    # Assert
    assert success is False
    assert employee_id is None
    mock_db_session.rollback.assert_called_once()
    mock_print.assert_called_once()


def test_add_employee_without_balance_initialization(mock_db_session):
    """Test l'ajout d'un employé sans initialisation des soldes de congés"""
    # Arrange
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.flush = MagicMock()
    
    # Utiliser les attributs corrects
    employee_data = {
        "name": "Sophie Dubois",
        "email": "sophie.dubois@example.com",
        "password": "password123",
        "initialize_balances": False
    }
    
    # Créer un mock pour l'employé créé
    mock_employee = MagicMock(spec=Employee)
    mock_employee.id = 5
    
    # Simuler l'ajout d'un employé
    mock_db_session.add.side_effect = lambda employee: setattr(employee, 'id', 5)
    
    # Mock pour LeaveService
    with patch('app.services.leave_service.LeaveService') as mock_leave_service:
        mock_leave_service.initialize_balances = MagicMock()
        
        # Act
        success, employee_id = EmployeeService.add_employee(mock_db_session, employee_data)
        
        # Assert
        assert success is True
        assert employee_id == 5
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_leave_service.initialize_balances.assert_not_called() 