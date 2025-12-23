import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from typing import List

from app.services.leave_service import LeaveService
from app.models.leave import Leave
from app.models.leave_balance import LeaveBalance
from app.models.employee import Employee
from app.models.training_request import TrainingRequest
from app.services.notification_service import NotificationService
from app.repositories.employee_repository import EmployeeRepository
from fastapi import HTTPException


@pytest.fixture
def mock_db_session():
    """Fixture pour simuler une session de base de données."""
    db = MagicMock()
    return db


@pytest.fixture
def mock_employee():
    """Fixture pour créer un employé mocké."""
    employee = MagicMock(spec=Employee)
    employee.id = 1
    employee.name = "Test Employee"
    employee.department = "IT"
    employee.supervisor_id = 2  # Assume there's a supervisor
    return employee


@patch('app.services.notification_service.NotificationService.send_notification')
def test_request_leave(mock_send_notification, mock_db_session, mock_employee):
    """Test de la demande de congé."""
    # Simuler la base de données
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_employee

    # Créer un solde de congé fictif
    mock_balance = MagicMock(spec=LeaveBalance)
    mock_balance.balance = 10  # L'employé a 10 jours de congé
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_balance

    # Configuration pour résoudre le problème avec count()
    # En retournant 0 pour le nombre de congés qui se chevauchent
    mock_db_session.query.return_value.join.return_value.filter.return_value.count.return_value = 0

    # Créer la demande de congé
    leave_service = LeaveService()
    start_date = datetime.today() + timedelta(days=1)
    end_date = start_date + timedelta(days=2)

    # Appeler la méthode pour créer la demande de congé
    leave = leave_service.request_leave(mock_db_session, mock_employee.id, start_date, end_date)

    # Vérification que la demande de congé a bien été créée
    assert leave is not None
    assert leave.employee_id == mock_employee.id
    assert leave.status == "en attente"


def test_request_leave_balance_insufficient(mock_db_session, mock_employee):
    """Test de la demande de congé avec solde insuffisant."""
    # Simuler la base de données
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_employee

    # Solde insuffisant pour l'employé
    mock_balance = MagicMock(spec=LeaveBalance)
    mock_balance.balance = 0  # L'employé n'a aucun jour de congé
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_balance

    # Créer la demande de congé
    leave_service = LeaveService()
    start_date = datetime.today() + timedelta(days=1)
    end_date = start_date + timedelta(days=2)

    # Appeler la méthode et vérifier l'exception
    with pytest.raises(HTTPException):
        leave_service.request_leave(mock_db_session, mock_employee.id, start_date, end_date)


@patch('app.services.notification_service.NotificationService.send_notification')
def test_approve_leave(mock_send_notification, mock_db_session, mock_employee):
    """Test de l'approbation d'une demande de congé."""
    # Simuler une demande de congé en attente
    mock_leave = MagicMock(spec=Leave)
    mock_leave.id = 1
    mock_leave.status = "en attente"
    mock_leave.employee_id = mock_employee.id
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_leave

    # Appeler la méthode pour approuver la demande
    leave_service = LeaveService()
    approved_leave = leave_service.approve_leave(mock_db_session, mock_leave.id)

    # Vérification que le statut a changé à "approuvé"
    assert approved_leave.status == "approuvé"


@patch('app.services.notification_service.NotificationService.send_notification')
def test_reject_leave(mock_send_notification, mock_db_session, mock_employee):
    """Test du rejet d'une demande de congé."""
    # Simuler une demande de congé en attente
    mock_leave = MagicMock(spec=Leave)
    mock_leave.id = 1
    mock_leave.status = "en attente"
    mock_leave.employee_id = mock_employee.id
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_leave

    # Appeler la méthode pour rejeter la demande
    leave_service = LeaveService()
    rejected_leave = leave_service.reject_leave(mock_db_session, mock_leave.id)

    # Vérification que le statut a changé à "refusé"
    assert rejected_leave.status == "refusé"


def test_get_team_absences(mock_db_session, mock_employee):
    """Test de la récupération des absences d'une équipe."""
    # Mocker le comportement statique de EmployeeRepository.get_by_id
    with patch.object(EmployeeRepository, 'get_by_id', return_value=mock_employee):
        # Créer un mock pour l'employé lié au congé
        mock_leave_employee = MagicMock()
        mock_leave_employee.name = "Test Employee"
        mock_leave_employee.role = "employee"
        
        # Créer un mock pour le congé avec une référence à l'employé
        mock_leave = MagicMock(spec=Leave)
        mock_leave.employee = mock_leave_employee
        mock_leave.start_date = datetime.today()
        mock_leave.end_date = datetime.today() + timedelta(days=2)
        
        # Configurer la requête pour retourner le congé mocké
        mock_db_session.query.return_value.join.return_value.filter.return_value.all.return_value = [mock_leave]
        
        # Appeler la méthode pour obtenir les absences de l'équipe
        leave_service = LeaveService()
        absences = leave_service.get_team_absences(mock_db_session, mock_employee.id)
        
        # Vérification que les absences sont récupérées
        assert len(absences) > 0
        assert "Test Employee" in absences[0]["employee_name"]


def test_get_notifications(mock_db_session, mock_employee):
    """Test de récupération des notifications."""
    # Configurer le mock pour l'employé
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_employee
    
    # Créer un mock pour un congé avec le statut "approuvé"
    mock_leave = MagicMock(spec=Leave)
    mock_leave.id = 1
    mock_leave.status = "approuvé"
    mock_leave.start_date = datetime.today()
    mock_leave.end_date = datetime.today() + timedelta(days=2)
    mock_leave.type = "Vacances"
    
    # Configurer la requête pour retourner le congé
    mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_leave]
    
    leave_service = LeaveService()
    notifications = leave_service.get_notifications(mock_db_session, "testemployee@example.com")
    
    # Vérification que les notifications sont retournées
    assert len(notifications) > 0
    assert "approuvée" in notifications[0]["message"]
