import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException

from app.services.leave_service import LeaveService, LeaveWorkflowFacade
from app.models.leave import Leave
from app.models.leave_balance import LeaveBalance
from app.models.employee import Employee
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.repositories.employee_repository import EmployeeRepository


@pytest.fixture
def mock_db_session():
    """Fixture pour simuler une session de base de données."""
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def mock_employee():
    """Fixture pour créer un employé mocké."""
    employee = MagicMock(spec=Employee)
    employee.id = 1
    employee.name = "Test Employee"
    employee.email = "test@example.com"
    employee.department = "IT"
    employee.supervisor_id = 2
    return employee


@pytest.fixture
def mock_supervisor():
    """Fixture pour créer un superviseur mocké."""
    supervisor = MagicMock(spec=Employee)
    supervisor.id = 2
    supervisor.name = "Test Supervisor"
    supervisor.email = "supervisor@example.com"
    supervisor.department = "IT"
    supervisor.role = "manager"
    return supervisor


@pytest.fixture
def mock_leave():
    """Fixture pour créer une demande de congé mockée."""
    leave = MagicMock(spec=Leave)
    leave.id = 1
    leave.employee_id = 1
    leave.supervisor_id = 2
    leave.status = "en attente"
    leave.start_date = datetime.now(UTC) + timedelta(days=5)
    leave.end_date = datetime.now(UTC) + timedelta(days=10)
    leave.created_at = datetime.now(UTC)
    leave.type = "congé annuel"
    return leave


@pytest.fixture
def mock_leave_balance():
    """Fixture pour créer un solde de congé mocké."""
    balance = MagicMock(spec=LeaveBalance)
    balance.employee_id = 1
    balance.balance = 25
    balance.sick_leave_balance = 10
    return balance


def test_get_employees_on_leave(mock_db_session, mock_supervisor, mock_employee):
    """Test pour obtenir les employés en congé sous la supervision d'un superviseur."""
    # Configurer le mock pour retourner le superviseur
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_supervisor
    
    # Créer un mock pour les congés
    mock_leave = MagicMock()
    mock_leave.employee = mock_employee
    mock_leave.start_date = datetime.now(UTC) - timedelta(days=2)
    mock_leave.end_date = datetime.now(UTC) + timedelta(days=3)
    mock_leave.status = "approuvé"
    
    # Configurer le mock pour retourner les congés
    mock_db_session.query.return_value.join.return_value.filter.return_value.all.return_value = [mock_leave]
    
    # Appeler la méthode
    result = LeaveService.get_employees_on_leave(mock_db_session, "supervisor@example.com")
    
    # Vérifier les résultats
    assert len(result) == 1
    assert result[0]["employee_name"] == mock_employee.name
    assert "start_date" in result[0]
    assert "end_date" in result[0]
    assert "status" in result[0]


def test_get_employees_on_leave_supervisor_not_found(mock_db_session):
    """Test pour obtenir les employés en congé avec un superviseur inexistant."""
    # Configurer le mock pour retourner None (superviseur non trouvé)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Appeler la méthode et vérifier qu'elle lève une exception
    with pytest.raises(HTTPException) as excinfo:
        LeaveService.get_employees_on_leave(mock_db_session, "nonexistent@example.com")
    
    assert excinfo.value.status_code == 404
    assert "Superviseur non trouvé" in str(excinfo.value.detail)


def test_get_employees_on_leave_no_employees(mock_db_session, mock_supervisor):
    """Test pour obtenir les employés en congé quand aucun n'est en congé."""
    # Configurer le mock pour retourner le superviseur
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_supervisor
    
    # Configurer le mock pour retourner une liste vide
    mock_db_session.query.return_value.join.return_value.filter.return_value.all.return_value = []
    
    # Appeler la méthode
    result = LeaveService.get_employees_on_leave(mock_db_session, "supervisor@example.com")
    
    # Vérifier les résultats
    assert len(result) == 0


def test_delete_employee(mock_db_session, mock_employee, mock_leave_balance):
    """Test pour supprimer un employé et ses congés."""
    # Configurer les mocks pour retourner l'employé et ses soldes
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_employee
    mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_leave_balance]
    
    # Appeler la méthode
    result = LeaveService.delete_employee(mock_db_session, 1)
    
    # Vérifier les résultats
    assert "deleted successfully" in result["detail"]
    assert mock_db_session.delete.called
    assert mock_db_session.commit.called


def test_delete_employee_not_found(mock_db_session):
    """Test pour supprimer un employé inexistant."""
    # Configurer le mock pour retourner None (employé non trouvé)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Appeler la méthode et vérifier qu'elle lève une exception
    with pytest.raises(HTTPException) as excinfo:
        LeaveService.delete_employee(mock_db_session, 999)
    
    assert excinfo.value.status_code == 500
    assert "not found" in str(excinfo.value.detail)


def test_delete_employee_error(mock_db_session, mock_employee):
    """Test pour gérer les erreurs lors de la suppression d'un employé."""
    # Configurer le mock pour retourner l'employé
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_employee
    
    # Configurer le mock pour lever une exception lors du commit
    mock_db_session.commit.side_effect = Exception("Database error")
    
    # Appeler la méthode et vérifier qu'elle lève une exception
    with pytest.raises(HTTPException) as excinfo:
        LeaveService.delete_employee(mock_db_session, 1)
    
    assert excinfo.value.status_code == 500
    assert "Error deleting" in str(excinfo.value.detail)
    assert mock_db_session.rollback.called


def test_cancel_leave(mock_db_session, mock_leave):
    """Test pour annuler une demande de congé."""
    # Configurer le mock pour retourner la demande
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_leave
    
    # Mocker le contexte de congé
    with patch('app.states.leave_request.leave_context.LeaveContext') as mock_context_class:
        # Configurer le mock du contexte
        mock_context = mock_context_class.return_value
        mock_context.cancel.return_value = {"success": True, "message": "Demande annulée avec succès"}
        
        # Appeler la méthode
        result = LeaveService.cancel_leave(mock_db_session, 1)
        
        # Vérifier les résultats
        assert result is mock_leave
        mock_context.cancel.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_leave)


def test_cancel_leave_not_found(mock_db_session):
    """Test pour annuler une demande de congé inexistante."""
    # Configurer le mock pour retourner None (demande non trouvée)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Appeler la méthode et vérifier qu'elle lève une exception
    with pytest.raises(HTTPException) as excinfo:
        LeaveService.cancel_leave(mock_db_session, 999)
    
    assert excinfo.value.status_code == 404
    assert "Demande introuvable" in str(excinfo.value.detail)


def test_cancel_leave_failure(mock_db_session, mock_leave):
    """Test pour gérer les échecs lors de l'annulation d'une demande."""
    # Configurer le mock pour retourner la demande
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_leave
    
    # Mocker le contexte de congé
    with patch('app.states.leave_request.leave_context.LeaveContext') as mock_context_class:
        # Configurer le mock du contexte pour simuler un échec
        mock_context = mock_context_class.return_value
        mock_context.cancel.return_value = {"success": False, "message": "Erreur lors de l'annulation"}
        
        # Appeler la méthode et vérifier qu'elle lève une exception
        with pytest.raises(HTTPException) as excinfo:
            LeaveService.cancel_leave(mock_db_session, 1)
        
        assert excinfo.value.status_code == 400
        assert "Erreur lors de l'annulation" in str(excinfo.value.detail)


def test_leave_workflow_facade_approve_by_admin(mock_db_session, mock_leave, mock_employee):
    """Test pour approuver une demande par l'administrateur via la façade."""
    # Configurer les mocks pour retourner la demande et l'employé
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_leave, mock_employee]
    
    # Mocker la méthode send_notification
    with patch.object(NotificationService, 'send_notification') as mock_send:
        # Appeler la méthode
        result = LeaveWorkflowFacade.approve_by_admin(mock_db_session, 1)
        
        # Vérifier les résultats
        assert "Demande approuvée" in result["message"]
        assert result["leave_id"] == mock_leave.id
        assert mock_leave.status == "approuvé"
        assert mock_db_session.commit.called
        mock_send.assert_called_once()


def test_leave_workflow_facade_reject_by_admin(mock_db_session, mock_leave, mock_employee):
    """Test pour rejeter une demande par l'administrateur via la façade."""
    # Configurer les mocks pour retourner la demande et l'employé
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_leave, mock_employee]
    
    # Mocker la méthode send_notification
    with patch.object(NotificationService, 'send_notification') as mock_send:
        # Appeler la méthode
        result = LeaveWorkflowFacade.reject_by_admin(mock_db_session, 1)
        
        # Vérifier les résultats
        assert "Demande refusée" in result["message"]
        assert result["leave_id"] == mock_leave.id
        assert mock_leave.status == "refusé"
        assert mock_db_session.commit.called
        mock_send.assert_called_once()


def test_leave_workflow_facade_forward_to_supervisor(mock_db_session, mock_leave, mock_employee):
    """Test pour transférer une demande au superviseur via la façade."""
    # Configurer les mocks pour retourner la demande et l'employé
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_leave, mock_employee]
    
    # Mocker la méthode send_notification
    with patch.object(NotificationService, 'send_notification') as mock_send:
        # Appeler la méthode
        result = LeaveWorkflowFacade.forward_to_supervisor(mock_db_session, 1)
        
        # Vérifier les résultats
        assert "Demande transmise" in result["message"]
        assert result["leave_id"] == mock_leave.id
        assert mock_leave.status == "en attente sup"
        assert mock_leave.supervisor_id == mock_employee.supervisor_id
        assert mock_db_session.commit.called
        mock_send.assert_called_once()


def test_leave_workflow_facade_forward_to_supervisor_no_supervisor(mock_db_session, mock_leave):
    """Test pour transférer une demande sans superviseur via la façade."""
    # Créer un mock d'employé sans superviseur
    employee_no_supervisor = MagicMock(spec=Employee)
    employee_no_supervisor.id = 1
    employee_no_supervisor.name = "Test Employee"
    employee_no_supervisor.supervisor_id = None
    
    # Configurer les mocks pour retourner la demande et l'employé sans superviseur
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_leave, employee_no_supervisor]
    
    # Appeler la méthode et vérifier qu'elle lève une exception
    with pytest.raises(HTTPException) as excinfo:
        LeaveWorkflowFacade.forward_to_supervisor(mock_db_session, 1)
    
    assert excinfo.value.status_code == 400
    assert "n'a pas de superviseur" in str(excinfo.value.detail)


def test_leave_workflow_facade_approve_by_supervisor(mock_db_session, mock_leave, mock_employee, mock_supervisor):
    """Test pour approuver une demande par le superviseur via la façade."""
    # Configurer la demande avec le bon superviseur
    mock_leave.supervisor_id = mock_supervisor.id
    
    # Configurer les mocks pour retourner le superviseur, la demande et l'employé
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_supervisor, mock_leave, mock_employee]
    
    # Mocker les méthodes send_notification et send_notification_to_admin
    with patch.object(NotificationService, 'send_notification') as mock_send:
        with patch.object(NotificationService, 'send_notification_to_admin') as mock_send_admin:
            # Appeler la méthode
            result = LeaveWorkflowFacade.approve_by_supervisor(mock_db_session, "supervisor@example.com", 1)
            
            # Vérifier les résultats
            assert "Demande approuvée" in result["message"]
            assert result["leave_id"] == mock_leave.id
            assert mock_leave.status == "approuvé"
            assert mock_db_session.commit.called
            mock_send.assert_called_once()
            mock_send_admin.assert_called_once()


def test_leave_workflow_facade_reject_by_supervisor(mock_db_session, mock_leave, mock_employee, mock_supervisor):
    """Test pour rejeter une demande par le superviseur via la façade."""
    # Configurer la demande avec le bon superviseur
    mock_leave.supervisor_id = mock_supervisor.id
    
    # Configurer les mocks pour retourner le superviseur, la demande et l'employé
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_supervisor, mock_leave, mock_employee]
    
    # Mocker les méthodes send_notification et send_notification_to_admin
    with patch.object(NotificationService, 'send_notification') as mock_send:
        with patch.object(NotificationService, 'send_notification_to_admin') as mock_send_admin:
            # Appeler la méthode
            result = LeaveWorkflowFacade.reject_by_supervisor(mock_db_session, "supervisor@example.com", 1)
            
            # Vérifier les résultats
            assert "Demande refusée" in result["message"]
            assert result["leave_id"] == mock_leave.id
            assert mock_leave.status == "refusé"
            assert mock_db_session.commit.called
            mock_send.assert_called_once()
            mock_send_admin.assert_called_once() 