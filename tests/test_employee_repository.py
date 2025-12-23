import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.repositories.employee_repository import EmployeeRepository
from app.models.employee import Employee


@pytest.fixture
def mock_db_session():
    """Fixture pour créer un mock de session de base de données"""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_employee():
    """Fixture pour créer un mock d'employé"""
    employee = MagicMock(spec=Employee)
    employee.id = 1
    employee.name = "Jean Dupont"
    employee.email = "jean.dupont@example.com"
    employee.role = "employé"
    employee.department = "IT"
    return employee


@pytest.fixture
def mock_employees_list(mock_employee):
    """Fixture pour créer une liste de mocks d'employés"""
    employee2 = MagicMock(spec=Employee)
    employee2.id = 2
    employee2.name = "Marie Martin"
    employee2.email = "marie.martin@example.com"
    employee2.role = "superviseur"
    employee2.department = "RH"
    
    employee3 = MagicMock(spec=Employee)
    employee3.id = 3
    employee3.name = "Pierre Durand"
    employee3.email = "pierre.durand@example.com"
    employee3.role = "employé"
    employee3.department = "Finance"
    
    return [mock_employee, employee2, employee3]


def test_get_all(mock_db_session, mock_employees_list):
    """Test la récupération de tous les employés"""
    # Arrange
    mock_db_session.query.return_value.all.return_value = mock_employees_list
    
    # Act
    result = EmployeeRepository.get_all(mock_db_session)
    
    # Assert
    assert result == mock_employees_list
    mock_db_session.query.assert_called_once_with(Employee)
    mock_db_session.query.return_value.all.assert_called_once()


def test_get_by_id_found(mock_db_session, mock_employee):
    """Test la récupération d'un employé par son ID avec succès"""
    # Arrange
    employee_id = 1
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_employee
    
    # Act
    result = EmployeeRepository.get_by_id(mock_db_session, employee_id)
    
    # Assert
    assert result == mock_employee
    mock_db_session.query.assert_called_once_with(Employee)
    mock_db_session.query.return_value.filter.assert_called_once()


def test_get_by_id_not_found(mock_db_session):
    """Test la récupération d'un employé inexistant par son ID"""
    # Arrange
    employee_id = 999
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Act
    result = EmployeeRepository.get_by_id(mock_db_session, employee_id)
    
    # Assert
    assert result is None
    mock_db_session.query.assert_called_once_with(Employee)
    mock_db_session.query.return_value.filter.assert_called_once()


def test_get_by_email_found(mock_db_session, mock_employee):
    """Test la récupération d'un employé par son email avec succès"""
    # Arrange
    email = "jean.dupont@example.com"
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_employee
    
    # Act
    result = EmployeeRepository.get_by_email(mock_db_session, email)
    
    # Assert
    assert result == mock_employee
    mock_db_session.query.assert_called_once_with(Employee)
    mock_db_session.query.return_value.filter.assert_called_once()


def test_get_by_email_not_found(mock_db_session):
    """Test la récupération d'un employé inexistant par son email"""
    # Arrange
    email = "inconnu@example.com"
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Act
    result = EmployeeRepository.get_by_email(mock_db_session, email)
    
    # Assert
    assert result is None
    mock_db_session.query.assert_called_once_with(Employee)
    mock_db_session.query.return_value.filter.assert_called_once()


def test_get_managers(mock_db_session, mock_employees_list):
    """Test la récupération de tous les managers"""
    # Arrange
    # On filtre uniquement les superviseurs de notre liste
    managers = [emp for emp in mock_employees_list if emp.role == "superviseur"]
    mock_db_session.query.return_value.filter.return_value.all.return_value = managers
    
    # Act
    result = EmployeeRepository.get_managers(mock_db_session)
    
    # Assert
    assert result == managers
    mock_db_session.query.assert_called_once_with(Employee)
    mock_db_session.query.return_value.filter.assert_called_once()


def test_get_team_by_department(mock_db_session, mock_employees_list):
    """Test la récupération des employés par département"""
    # Arrange
    department = "IT"
    # On filtre uniquement les employés du département IT
    it_employees = [emp for emp in mock_employees_list if emp.department == department]
    mock_db_session.query.return_value.filter.return_value.all.return_value = it_employees
    
    # Act
    result = EmployeeRepository.get_team_by_department(mock_db_session, department)
    
    # Assert
    assert result == it_employees
    mock_db_session.query.assert_called_once_with(Employee)
    mock_db_session.query.return_value.filter.assert_called_once()


def test_create(mock_db_session, mock_employee):
    """Test la création d'un employé"""
    # Arrange
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()
    
    # Act
    result = EmployeeRepository.create(mock_db_session, mock_employee)
    
    # Assert
    assert result == mock_employee
    mock_db_session.add.assert_called_once_with(mock_employee)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_employee)


def test_update(mock_db_session, mock_employee):
    """Test la mise à jour d'un employé"""
    # Arrange
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()
    
    update_data = {
        "name": "Jean Dupont Modifié",
        "role": "manager"
    }
    
    # Act
    result = EmployeeRepository.update(mock_db_session, mock_employee, update_data)
    
    # Assert
    assert result == mock_employee
    assert mock_employee.name == "Jean Dupont Modifié"
    assert mock_employee.role == "manager"
    # L'email ne doit pas être modifié
    assert mock_employee.email == "jean.dupont@example.com"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_employee)


def test_delete(mock_db_session, mock_employee):
    """Test la suppression d'un employé"""
    # Arrange
    mock_db_session.delete = MagicMock()
    mock_db_session.commit = MagicMock()
    
    # Act
    EmployeeRepository.delete(mock_db_session, mock_employee)
    
    # Assert
    mock_db_session.delete.assert_called_once_with(mock_employee)
    mock_db_session.commit.assert_called_once() 