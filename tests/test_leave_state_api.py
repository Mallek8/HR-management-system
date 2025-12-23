import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.leave_state_api import (
    get_leave_state_info,
    approve_leave,
    reject_leave,
    cancel_leave,
    router
)
from app.services.leave_state_service import LeaveStateService
from app.models.leave import Leave


@pytest.fixture
def mock_db_session():
    """Fixture pour simuler une session de base de données."""
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def test_client():
    """Client de test FastAPI."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def successful_state_info():
    """Fixture pour une réponse réussie de get_leave_state_info."""
    return {
        "success": True,
        "leave_id": 1,
        "employee_id": 100,
        "current_state": "en attente",
        "allowed_transitions": {
            "approve": "approuvé",
            "reject": "refusé",
            "cancel": "annulé"
        },
        "start_date": datetime(2023, 1, 1),
        "end_date": datetime(2023, 1, 7)
    }


@pytest.fixture
def failed_state_info():
    """Fixture pour une réponse échouée de get_leave_state_info."""
    return {
        "success": False,
        "message": "Demande de congé #999 non trouvée"
    }


def test_get_leave_state_info_success(mock_db_session, successful_state_info):
    """Test de récupération des informations d'état avec succès."""
    # Simuler la réponse du service
    with patch.object(LeaveStateService, 'get_leave_state_info', return_value=successful_state_info) as mock_service:
        # Appeler la fonction de l'API
        result = get_leave_state_info(leave_id=1, db=mock_db_session)
        
        # Vérifications
        mock_service.assert_called_once_with(mock_db_session, 1)
        assert result == successful_state_info
        assert result["success"] is True
        assert result["leave_id"] == 1


def test_get_leave_state_info_not_found(mock_db_session, failed_state_info):
    """Test de récupération des informations d'état pour une demande inexistante."""
    # Simuler la réponse du service
    with patch.object(LeaveStateService, 'get_leave_state_info', return_value=failed_state_info) as mock_service:
        # Vérifier que l'exception est levée
        with pytest.raises(HTTPException) as excinfo:
            get_leave_state_info(leave_id=999, db=mock_db_session)
        
        # Vérifications
        mock_service.assert_called_once_with(mock_db_session, 999)
        assert excinfo.value.status_code == 404
        assert "non trouvée" in excinfo.value.detail


def test_approve_leave_success(mock_db_session):
    """Test d'approbation d'une demande de congé avec succès."""
    # Simuler une réponse réussie du service
    success_response = {
        "success": True,
        "message": "L'approbation a réussi",
        "leave_id": 1,
        "current_state": "approuvé",
        "allowed_transitions": {"cancel": "annulé"}
    }
    
    with patch.object(LeaveStateService, 'process_approval', return_value=success_response) as mock_service:
        # Appeler la fonction de l'API
        result = approve_leave(leave_id=1, approved_by=2, db=mock_db_session)
        
        # Vérifications
        mock_service.assert_called_once_with(mock_db_session, 1, 2, approved=True)
        assert result == success_response
        assert result["success"] is True
        assert result["current_state"] == "approuvé"


def test_approve_leave_failure(mock_db_session):
    """Test d'approbation d'une demande de congé avec échec."""
    # Simuler une réponse échouée du service
    error_response = {
        "success": False,
        "message": "L'approbation a échoué: statut incompatible",
        "leave_id": 1,
        "current_state": "refusé",
        "allowed_transitions": {}
    }
    
    with patch.object(LeaveStateService, 'process_approval', return_value=error_response) as mock_service:
        # Vérifier que l'exception est levée
        with pytest.raises(HTTPException) as excinfo:
            approve_leave(leave_id=1, approved_by=2, db=mock_db_session)
        
        # Vérifications
        mock_service.assert_called_once_with(mock_db_session, 1, 2, approved=True)
        assert excinfo.value.status_code == 400


def test_approve_leave_not_found(mock_db_session):
    """Test d'approbation d'une demande de congé inexistante."""
    # Simuler une réponse "non trouvée" du service
    not_found_response = {
        "success": False,
        "message": "Demande de congé #999 non trouvée"
    }
    
    with patch.object(LeaveStateService, 'process_approval', return_value=not_found_response) as mock_service:
        # Vérifier que l'exception est levée
        with pytest.raises(HTTPException) as excinfo:
            approve_leave(leave_id=999, approved_by=2, db=mock_db_session)
        
        # Vérifications
        assert excinfo.value.status_code == 404
        assert "non trouvée" in excinfo.value.detail


def test_reject_leave_success(mock_db_session):
    """Test de rejet d'une demande de congé avec succès."""
    # Simuler une réponse réussie du service
    success_response = {
        "success": True,
        "message": "Le rejet a réussi",
        "leave_id": 1,
        "current_state": "refusé",
        "allowed_transitions": {}
    }
    
    with patch.object(LeaveStateService, 'process_approval', return_value=success_response) as mock_service:
        # Appeler la fonction de l'API
        result = reject_leave(leave_id=1, rejected_by=2, reason="Test reason", db=mock_db_session)
        
        # Vérifications
        mock_service.assert_called_once_with(mock_db_session, 1, 2, approved=False, reason="Test reason")
        assert result == success_response
        assert result["success"] is True
        assert result["current_state"] == "refusé"


def test_cancel_leave_success(mock_db_session):
    """Test d'annulation d'une demande de congé avec succès."""
    # Simuler une réponse réussie du service
    success_response = {
        "success": True,
        "message": "L'annulation a réussi",
        "leave_id": 1,
        "current_state": "annulé",
        "allowed_transitions": {}
    }
    
    with patch.object(LeaveStateService, 'cancel_leave', return_value=success_response) as mock_service:
        # Appeler la fonction de l'API
        result = cancel_leave(leave_id=1, cancelled_by=2, reason="Test reason", db=mock_db_session)
        
        # Vérifications
        mock_service.assert_called_once_with(mock_db_session, 1, 2, "Test reason")
        assert result == success_response
        assert result["success"] is True
        assert result["current_state"] == "annulé"


def test_cancel_leave_failure(mock_db_session):
    """Test d'annulation d'une demande de congé avec échec."""
    # Simuler une réponse échouée du service
    error_response = {
        "success": False,
        "message": "L'annulation a échoué: statut incompatible",
        "leave_id": 1,
        "current_state": "refusé",
        "allowed_transitions": {}
    }
    
    with patch.object(LeaveStateService, 'cancel_leave', return_value=error_response) as mock_service:
        # Vérifier que l'exception est levée
        with pytest.raises(HTTPException) as excinfo:
            cancel_leave(leave_id=1, cancelled_by=2, db=mock_db_session)
        
        # Vérifications
        assert excinfo.value.status_code == 400 