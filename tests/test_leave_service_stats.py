import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

from app.services.leave_service import LeaveService
from app.models.leave import Leave
from app.models.leave_balance import LeaveBalance
from app.models.employee import Employee


@pytest.fixture
def mock_db_session():
    """Fixture pour simuler une session de base de données."""
    db = MagicMock()
    return db


@pytest.fixture
def mock_leaves():
    """Fixture pour créer des congés mockés."""
    # Create three leaves with different statuses
    leave1 = MagicMock(spec=Leave)
    leave1.id = 1
    leave1.employee_id = 1
    leave1.status = "approuvé"
    leave1.start_date = datetime(2023, 5, 10)
    leave1.end_date = datetime(2023, 5, 15)
    
    leave2 = MagicMock(spec=Leave)
    leave2.id = 2
    leave2.employee_id = 1
    leave2.status = "en attente"
    leave2.start_date = datetime(2023, 6, 20)
    leave2.end_date = datetime(2023, 6, 25)
    
    leave3 = MagicMock(spec=Leave)
    leave3.id = 3
    leave3.employee_id = 1
    leave3.status = "refusé"
    leave3.start_date = datetime(2023, 7, 5)
    leave3.end_date = datetime(2023, 7, 10)
    
    return [leave1, leave2, leave3]


def test_get_leave_stats_for_employee(mock_db_session, mock_leaves):
    """Test pour obtenir les statistiques de congés d'un employé."""
    # Configure the mock to return our mock leaves
    mock_db_session.query.return_value.filter.return_value.all.return_value = mock_leaves
    
    # Call the method
    stats = LeaveService.get_leave_stats_for_employee(mock_db_session, 1)
    
    # Verify the results
    assert stats["total"] == 3
    assert stats["approved"] == 1
    assert stats["pending"] == 1
    assert stats["rejected"] == 1
    
    # Verify the query was called correctly
    mock_db_session.query.assert_called_with(Leave)
    # Don't check specific filter calls as they use objects that may not be equal


def test_get_leave_stats_for_employee_empty(mock_db_session):
    """Test pour obtenir les statistiques de congés d'un employé sans congés."""
    # Configure the mock to return an empty list
    mock_db_session.query.return_value.filter.return_value.all.return_value = []
    
    # Call the method
    stats = LeaveService.get_leave_stats_for_employee(mock_db_session, 1)
    
    # Verify the results
    assert stats["total"] == 0
    assert stats["approved"] == 0
    assert stats["pending"] == 0
    assert stats["rejected"] == 0


def test_get_leave_stats_for_employee_exception(mock_db_session):
    """Test pour gérer une exception lors de la récupération des statistiques."""
    # Configure the mock to raise an exception
    mock_db_session.query.side_effect = SQLAlchemyError("Database error")
    
    # Mock logging
    with patch('builtins.__import__', return_value=MagicMock(error=MagicMock())):
        # Call the method
        stats = LeaveService.get_leave_stats_for_employee(mock_db_session, 1)
    
    # Verify the results
    assert stats["total"] == 0
    assert stats["approved"] == 0
    assert stats["pending"] == 0
    assert stats["rejected"] == 0
    
    # Verify rollback was called
    mock_db_session.rollback.assert_called_once()


def test_get_leave_evolution_for_employee(mock_db_session):
    """Test pour obtenir l'évolution des congés d'un employé sur une année."""
    # Create mock leaves that span several days in different months
    leave1 = MagicMock(spec=Leave)
    leave1.employee_id = 1
    leave1.status = "approuvé"
    leave1.start_date = datetime(2023, 3, 29)  # March
    leave1.end_date = datetime(2023, 4, 2)    # April
    
    leave2 = MagicMock(spec=Leave)
    leave2.employee_id = 1
    leave2.status = "approuvé"
    leave2.start_date = datetime(2023, 7, 10)  # July
    leave2.end_date = datetime(2023, 7, 14)    # July
    
    # Configure the mock to return our leaves
    mock_db_session.query.return_value.filter.return_value.all.return_value = [leave1, leave2]
    
    # Call the method
    evolution = LeaveService.get_leave_evolution_for_employee(mock_db_session, 1, 2023)
    
    # Expected result: days in each month (0-indexed)
    # March (2): 3 days (29, 30, 31)
    # April (3): 2 days (1, 2)
    # July (6): 5 days (10, 11, 12, 13, 14)
    expected = [0, 0, 3, 2, 0, 0, 5, 0, 0, 0, 0, 0]
    assert evolution == expected
    
    # Verify the query was called correctly
    mock_db_session.query.assert_called_with(Leave)


def test_get_leave_evolution_for_employee_no_leaves(mock_db_session):
    """Test pour obtenir l'évolution des congés d'un employé sans congés."""
    # Configure the mock to return an empty list
    mock_db_session.query.return_value.filter.return_value.all.return_value = []
    
    # Call the method
    evolution = LeaveService.get_leave_evolution_for_employee(mock_db_session, 1, 2023)
    
    # Expected result: zeros for all months
    expected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert evolution == expected


def test_get_leave_evolution_for_employee_exception(mock_db_session):
    """Test pour gérer une exception lors de la récupération de l'évolution des congés."""
    # Configure the mock to raise an exception
    mock_db_session.query.side_effect = SQLAlchemyError("Database error")
    
    # Mock logging
    with patch('builtins.__import__', return_value=MagicMock(error=MagicMock())):
        # Call the method
        evolution = LeaveService.get_leave_evolution_for_employee(mock_db_session, 1, 2023)
    
    # Expected result: zeros for all months
    expected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert evolution == expected
    
    # Verify rollback was called
    mock_db_session.rollback.assert_called_once() 