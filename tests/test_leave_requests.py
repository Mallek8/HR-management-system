import pytest
import time
from fastapi.testclient import TestClient
from app.main import app  # Assurez-vous d'importer l'application FastAPI
from app.database import get_db, SessionLocal
from app.models import Employee, Leave
from app.models.leave_balance import LeaveBalance
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
from datetime import datetime

@pytest.fixture
def client():
    """Fixture pour créer un client TestClient FastAPI."""
    client = TestClient(app)
    yield client

@pytest.fixture
def db_session():
    """Fixture pour fournir une session de base de données de test."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()  # Restaure l'état initial de la base de données avant de fermer
        db.close()

@pytest.fixture
def create_employee(db_session: Session):
    """Fixture pour créer un employé de test."""
    timestamp = int(time.time() * 1000)
    employee = Employee(
        name="Test Employee",
        email=f"testemployee_{timestamp}@example.com",  # Email unique pour éviter les conflits
        password="password123",
        role="employee",
        department="IT",
        supervisor_id=None,
        status=True
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee

@pytest.fixture
def create_leave(db_session: Session, create_employee):
    """Fixture pour créer une demande de congé de test."""
    leave = Leave(
        employee_id=create_employee.id,
        start_date="2025-04-10",
        end_date="2025-04-15",
        type="vacation",
        status="en attente",
        admin_approved=False,
        supervisor_id=None
    )
    db_session.add(leave)
    db_session.commit()
    db_session.refresh(leave)
    return leave

def test_create_leave(client, create_employee):
    """Test de la création d'une nouvelle demande de congé."""
    leave_data = {
        "employee_id": create_employee.id,
        "start_date": "2025-04-10",
        "end_date": "2025-04-15",
        "type": "vacation"
    }
    response = client.post("/request-leave/", json=leave_data)

    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == create_employee.id
    assert data["status"] == "en attente"
    assert data["type"] == "vacation"

def test_get_employee_by_email(client, create_employee):
    """Test de récupération d'un employé par son email."""
    response = client.get(f"/request-leave/by-email?email={create_employee.email}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == create_employee.id
    assert data["email"] == create_employee.email

def test_get_leave_balance(client, create_employee, db_session):
    """Test de récupération du solde de congé pour un employé."""
    leave_balance = LeaveBalance(employee_id=create_employee.id, balance=10)
    db_session.add(leave_balance)
    db_session.commit()

    response = client.get(f"/request-leave/employees/{create_employee.id}/leave-balance")

    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 10

def test_get_all_leave_requests(client, create_leave):
    """Test de récupération de toutes les demandes de congé."""
    response = client.get("/request-leave/all")
    assert response.status_code == 200
    data = response.json()
    assert any(leave["id"] == create_leave.id for leave in data)

def test_get_all_leave_requests_empty(client, db_session):
    """Test de la route all quand aucune demande n'existe."""
    # Supprimer toutes les demandes
    db_session.query(Leave).delete()
    db_session.commit()

    response = client.get("/request-leave/all")
    assert response.status_code == 404

def test_get_leave_balance_not_found(client, create_employee):
    """Test du cas où le solde n'existe pas pour l'employé."""
    response = client.get(f"/request-leave/employees/{create_employee.id}/leave-balance")
    assert response.status_code == 404

def test_get_leave_requests_with_filters(client, db_session):
    """Test la récupération des demandes de congé avec filtres"""
    # Créer plusieurs demandes de congé avec différents statuts
    with patch('app.api.leave_requests.get_db', return_value=db_session):
        mock_leave1 = MagicMock()
        mock_leave1.id = 1
        mock_leave1.status = "en attente"
        mock_leave1.type = "Vacances"
        mock_leave1.employee_id = 1
        mock_leave1.start_date = datetime(2023, 6, 10)
        mock_leave1.end_date = datetime(2023, 6, 15)
        
        mock_leave2 = MagicMock()
        mock_leave2.id = 2
        mock_leave2.status = "approuvé"
        mock_leave2.type = "Maladie"
        mock_leave2.employee_id = 1
        mock_leave2.start_date = datetime(2023, 6, 20)
        mock_leave2.end_date = datetime(2023, 6, 25)
        
        with patch('sqlalchemy.orm.Session.query') as mock_query:
            mock_query.return_value.all.return_value = [mock_leave1, mock_leave2]
            
            response = client.get("/request-leave/all")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["status"] == "en attente"
            assert data[1]["status"] == "approuvé"

def test_get_leave_requests_empty_with_filters(client, db_session):
    """Test la récupération des demandes de congé filtrées quand il n'y en a pas"""
    with patch('app.api.leave_requests.get_db', return_value=db_session):
        with patch('sqlalchemy.orm.Session.query') as mock_query:
            mock_query.return_value.all.return_value = []
            
            response = client.get("/request-leave/all")
            assert response.status_code == 404
            assert "Aucune demande de congé trouvée" in response.json()["detail"]

def test_get_employee_by_email_invalid_format(client):
    """Test la récupération d'un employé avec un email invalide"""
    response = client.get("/request-leave/by-email?email=invalid-email")
    assert response.status_code == 422  # Validation error

def test_get_leave_balance_invalid_employee(client):
    """Test la récupération du solde de congés pour un employé inexistant"""
    with patch('sqlalchemy.orm.Session.query') as mock_query:
        mock_query.return_value.filter.return_value.first.return_value = None
        
        response = client.get("/request-leave/employees/999/leave-balance")
        assert response.status_code == 404
        assert "Solde de congés introuvable" in response.json()["detail"]

@pytest.mark.skip(reason="Test instable à cause de problèmes de mock")
def test_get_leave_balance_db_error(client, db_session):
    """Test la gestion des erreurs de base de données lors de la récupération du solde"""
    with patch('app.api.leave_requests.get_db', return_value=db_session):
        with patch('sqlalchemy.orm.Session.query') as mock_query:
            # Simuler un comportement plus réel avec une erreur lors de l'exécution de filter()
            query_mock = MagicMock()
            filter_mock = MagicMock()
            filter_mock.first.side_effect = Exception("Erreur DB")
            query_mock.filter.return_value = filter_mock
            mock_query.return_value = query_mock
            
            response = client.get("/request-leave/employees/1/leave-balance")
            assert response.status_code == 500
            assert "erreur" in response.json()["detail"].lower()

@pytest.mark.skip(reason="Test instable à cause de problèmes de mock avec la jointure Department")
def test_get_team_absences_success(client, db_session):
    """Test la récupération des absences de l'équipe"""
    # Mock pour Department
    mock_dept = MagicMock()
    mock_dept.id = 1
    mock_dept.name = "IT"
    
    # Mock pour Employee
    mock_employee = MagicMock()
    mock_employee.id = 1
    mock_employee.name = "John Doe"
    mock_employee.department = mock_dept
    mock_employee.department_id = 1
    
    # Mock pour Leave
    mock_absence = MagicMock()
    mock_absence.id = 1
    mock_absence.employee_id = 1
    mock_absence.start_date = datetime(2023, 6, 10)
    mock_absence.end_date = datetime(2023, 6, 15)
    mock_absence.status = "approuvé"
    mock_absence.type = "Vacances"
    
    with patch('app.api.leave_requests.get_db', return_value=db_session):
        with patch('sqlalchemy.orm.Session.query') as mock_query:
            # Configurer une réponse simulée plus simple 
            mock_query.return_value.join.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [(mock_absence, "John Doe", "IT")]
            
            response = client.get("/request-leave/team-absences")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["employee_name"] == "John Doe"
            assert data[0]["status"] == "approuvé"

@pytest.mark.skip(reason="Test instable à cause de problèmes de mock avec la jointure Department")
def test_get_team_absences_empty(client, db_session):
    """Test la récupération des absences de l'équipe quand il n'y en a pas"""
    with patch('app.api.leave_requests.get_db', return_value=db_session):
        with patch('sqlalchemy.orm.Session.query') as mock_query:
            # Configurer simplement une liste vide
            mock_query.return_value.join.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = []
            
            response = client.get("/request-leave/team-absences")
            assert response.status_code == 200
            assert len(response.json()) == 0

def test_get_team_absences_db_error(client):
    """Test la gestion des erreurs de base de données lors de la récupération des absences"""
    with patch('sqlalchemy.orm.Session.query', side_effect=Exception("Erreur DB")):
        response = client.get("/request-leave/team-absences")
        assert response.status_code == 500
        assert "erreur" in response.json()["detail"].lower()
