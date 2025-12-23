import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.services.evaluation_service import EvaluationService
from app.models.evaluation import Evaluation


@pytest.fixture
def mock_db_session():
    """Fixture pour simuler une session de base de données."""
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def mock_evaluation():
    """Fixture pour simuler une évaluation."""
    evaluation = MagicMock(spec=Evaluation)
    evaluation.id = 1
    evaluation.employee_id = 100
    evaluation.date = datetime(2023, 6, 15)
    evaluation.score = 4
    evaluation.feedback = "Très bon travail"
    return evaluation


@pytest.fixture
def mock_dict_method():
    """Mock pour la méthode dict() qui est attendue par le service."""
    with patch('app.schemas.EvaluationCreate.dict') as mock:
        mock.return_value = {
            'employee_id': 100,
            'score': 4,
            'feedback': 'Très bon travail',
            'date': datetime(2023, 6, 15)
        }
        yield mock


def test_create_evaluation(mock_db_session, mock_dict_method):
    """Test de création d'une évaluation."""
    # Mock de l'objet EvaluationCreate
    evaluation_data = MagicMock()
    evaluation_data.dict.return_value = {
        'employee_id': 100,
        'score': 4,
        'feedback': 'Très bon travail',
        'date': datetime(2023, 6, 15)
    }
    
    # Mock du résultat attendu
    mock_result = MagicMock(spec=Evaluation)
    mock_db_session.refresh.return_value = mock_result
    
    # Appeler la méthode à tester
    result = EvaluationService.create_evaluation(mock_db_session, evaluation_data)
    
    # Vérifications
    assert mock_db_session.add.called
    assert mock_db_session.commit.called
    assert mock_db_session.refresh.called


def test_get_evaluation(mock_db_session, mock_evaluation):
    """Test de récupération d'une évaluation par ID."""
    # Configurer le mock pour retourner l'évaluation simulée
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_evaluation
    
    # Appeler la méthode à tester
    result = EvaluationService.get_evaluation(mock_db_session, 1)
    
    # Vérifications
    assert result == mock_evaluation
    mock_db_session.query.assert_called_once_with(Evaluation)
    mock_db_session.query.return_value.filter.assert_called_once()


def test_get_evaluation_not_found(mock_db_session):
    """Test de récupération d'une évaluation inexistante."""
    # Configurer le mock pour retourner None
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Vérifier que l'exception est levée
    with pytest.raises(HTTPException) as excinfo:
        EvaluationService.get_evaluation(mock_db_session, 999)
    
    # Vérifications
    assert excinfo.value.status_code == 404
    assert "Evaluation not found" in excinfo.value.detail
    mock_db_session.query.assert_called_once_with(Evaluation)


def test_get_all_evaluations(mock_db_session, mock_evaluation):
    """Test de récupération de toutes les évaluations."""
    # Configurer le mock pour retourner une liste d'évaluations
    mock_evaluations = [mock_evaluation, MagicMock(spec=Evaluation)]
    mock_db_session.query.return_value.all.return_value = mock_evaluations
    
    # Appeler la méthode à tester
    result = EvaluationService.get_all_evaluations(mock_db_session)
    
    # Vérifications
    assert result == mock_evaluations
    assert len(result) == 2
    mock_db_session.query.assert_called_once_with(Evaluation) 