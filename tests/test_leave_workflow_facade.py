import pytest
from unittest.mock import MagicMock
from app.services.leave_workflow_facade import LeaveWorkflowFacade
from app.models.leave import Leave
from app.models.employee import Employee
from app.models.notification import Notification
from fastapi import HTTPException
from app.services.notification_service import NotificationService


@pytest.fixture
def mock_db_session():
    """Fixture pour simuler une session de base de données."""
    db = MagicMock()
    return db


@pytest.fixture
def mock_leave():
    """Fixture pour simuler une demande de congé."""
    leave = MagicMock(spec=Leave)
    leave.id = 1
    leave.status = "en attente"
    leave.employee_id = 1
    leave.start_date = "2025-04-01"
    leave.end_date = "2025-04-10"
    leave.supervisor_id = 2
    return leave


@pytest.fixture
def mock_employee():
    """Fixture pour simuler un employé."""
    employee = MagicMock(spec=Employee)
    employee.id = 1
    employee.name = "Test Employee"
    employee.supervisor_id = 2
    return employee


@pytest.fixture
def mock_supervisor():
    """Fixture pour simuler un superviseur."""
    supervisor = MagicMock(spec=Employee)
    supervisor.id = 2
    supervisor.name = "Test Supervisor"
    supervisor.email = "supervisor@example.com"
    return supervisor


def test_approve_by_admin(mock_db_session, mock_leave, mock_employee):
    """Test de l'approbation par l'administrateur."""
    # Simuler la base de données
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_leave, mock_employee]

    # Simuler l'envoi de notification
    NotificationService.send_notification = MagicMock()

    # Appeler la méthode pour approuver la demande de congé
    leave_workflow = LeaveWorkflowFacade()
    result = leave_workflow.approve_by_admin(mock_db_session, mock_leave.id)

    # Vérifier le changement de statut et l'envoi de notification
    assert mock_leave.status == "approuvé"
    NotificationService.send_notification.assert_called_once()
    assert result["message"] == "Demande approuvée par l'administrateur."


def test_reject_by_admin(mock_db_session, mock_leave, mock_employee):
    """Test du rejet par l'administrateur."""
    # Simuler la base de données
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_leave, mock_employee]

    # Simuler l'envoi de notification
    NotificationService.send_notification = MagicMock()

    # Appeler la méthode pour rejeter la demande de congé
    leave_workflow = LeaveWorkflowFacade()
    result = leave_workflow.reject_by_admin(mock_db_session, mock_leave.id)

    # Vérifier le changement de statut et l'envoi de notification
    assert mock_leave.status == "refusé"
    NotificationService.send_notification.assert_called_once()
    assert result["message"] == "Demande refusée par l'administrateur."


def test_forward_to_supervisor(mock_db_session, mock_leave, mock_employee):
    """Test de la transmission au superviseur."""
    # Simuler la base de données avec les bonnes valeurs de retour
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_leave, mock_employee]

    # Simuler l'envoi de notification
    NotificationService.send_notification = MagicMock()

    # Appeler la méthode pour transmettre la demande au superviseur
    leave_workflow = LeaveWorkflowFacade()
    result = leave_workflow.forward_to_supervisor(mock_db_session, mock_leave.id)

    # Vérifier le changement de statut et l'envoi de notification
    assert mock_leave.status == "en attente sup"
    assert mock_leave.supervisor_id == mock_employee.supervisor_id
    NotificationService.send_notification.assert_called_once()
    assert result["message"] == "Demande transmise au superviseur."


def test_approve_by_supervisor(mock_db_session, mock_leave, mock_employee, mock_supervisor):
    """Test de l'approbation par le superviseur."""
    # Configurer les mocks pour retourner les valeurs attendues
    # D'abord le superviseur, puis la demande, puis l'employé
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_supervisor, mock_leave, mock_employee]
    
    # S'assurer que le supervisor_id dans le congé correspond à l'ID du superviseur
    mock_leave.supervisor_id = mock_supervisor.id

    # Simuler l'envoi de notification
    NotificationService.send_notification = MagicMock()
    NotificationService.send_notification_to_admin = MagicMock()

    # Appeler la méthode pour approuver la demande
    leave_workflow = LeaveWorkflowFacade()
    result = leave_workflow.approve_by_supervisor(mock_db_session, "supervisor@example.com", mock_leave.id)

    # Vérifier le changement de statut et l'envoi de notification
    assert mock_leave.status == "approuvé"
    assert NotificationService.send_notification.call_count == 1
    assert NotificationService.send_notification_to_admin.call_count == 1
    assert result["message"] == "Demande approuvée par le superviseur."


def test_reject_by_supervisor(mock_db_session, mock_leave, mock_employee, mock_supervisor):
    """Test du rejet par le superviseur."""
    # Configurer les mocks pour retourner les valeurs attendues
    # D'abord le superviseur, puis la demande, puis l'employé
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_supervisor, mock_leave, mock_employee]
    
    # S'assurer que le supervisor_id dans le congé correspond à l'ID du superviseur
    mock_leave.supervisor_id = mock_supervisor.id

    # Simuler l'envoi de notification
    NotificationService.send_notification = MagicMock()
    NotificationService.send_notification_to_admin = MagicMock()

    # Appeler la méthode pour rejeter la demande
    leave_workflow = LeaveWorkflowFacade()
    result = leave_workflow.reject_by_supervisor(mock_db_session, "supervisor@example.com", mock_leave.id)

    # Vérifier le changement de statut et l'envoi de notification
    assert mock_leave.status == "refusé"
    assert NotificationService.send_notification.call_count == 1
    assert NotificationService.send_notification_to_admin.call_count == 1
    assert result["message"] == "Demande refusée par le superviseur."
