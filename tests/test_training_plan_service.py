import pytest
from unittest.mock import MagicMock, patch, ANY
from app.services.training_plan_service import TrainingPlanService
from app.models.training_request import TrainingRequest
from app.models.training_plan import TrainingPlan
from app.models.employee import Employee
from app.models.leave_balance import LeaveBalance

@pytest.fixture
def mock_db():
    """Fixture pour simuler une session de base de données"""
    db = MagicMock()
    return db

@pytest.fixture
def mock_training_request():
    """Fixture pour simuler une demande de formation"""
    return TrainingRequest(
        id=1,
        employee_id=1,
        training_id=101,
        status="approved"
    )

@pytest.fixture
def mock_existing_plan():
    """Fixture pour simuler un plan de formation déjà existant"""
    return TrainingPlan(
        employee_id=1,
        training_id=101
    )

def test_generate_plan_if_approved(mock_db, mock_training_request):
    """Test la génération d'un plan de formation si la demande est approuvée"""
    
    # Configuration des mocks
    # Pour le premier appel à query().filter_by().first() - récupération de la demande
    training_request_query = MagicMock()
    training_request_filter = MagicMock()
    training_request_filter.first.return_value = mock_training_request
    training_request_query.filter_by.return_value = training_request_filter
    
    # Pour le deuxième appel à query().filter_by().first() - vérification si un plan existe
    training_plan_query = MagicMock()
    training_plan_filter = MagicMock()
    training_plan_filter.first.return_value = None  # Pas de plan existant
    training_plan_query.filter_by.return_value = training_plan_filter
    
    # Configuration du mock_db.query pour retourner le bon query selon l'argument
    def side_effect_query(model):
        if model == TrainingRequest:
            return training_request_query
        elif model == TrainingPlan:
            return training_plan_query
        return MagicMock()
    
    mock_db.query = MagicMock(side_effect=side_effect_query)
    
    # Simuler l'ajout et l'engagement dans la base de données
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()

    # Appeler la méthode de génération du plan de formation
    TrainingPlanService.generate_plan_if_approved(mock_db, mock_training_request.id)

    # Vérifier que db.add a été appelé
    assert mock_db.add.call_count == 1
    
    # Vérifier les propriétés de l'objet TrainingPlan passé à add()
    added_plan = mock_db.add.call_args[0][0]
    assert isinstance(added_plan, TrainingPlan)
    assert added_plan.employee_id == mock_training_request.employee_id
    assert added_plan.training_id == mock_training_request.training_id
    
    # Vérifier que db.commit a été appelé
    mock_db.commit.assert_called_once()

def test_generate_plan_if_approved_existing_plan(mock_db, mock_training_request, mock_existing_plan):
    """Test si la génération du plan est ignorée si un plan existe déjà"""
    
    # Configuration des mocks
    # Pour le premier appel à query().filter_by().first() - récupération de la demande
    training_request_query = MagicMock()
    training_request_filter = MagicMock()
    training_request_filter.first.return_value = mock_training_request
    training_request_query.filter_by.return_value = training_request_filter
    
    # Pour le deuxième appel à query().filter_by().first() - vérification si un plan existe
    training_plan_query = MagicMock()
    training_plan_filter = MagicMock()
    training_plan_filter.first.return_value = mock_existing_plan  # Un plan existe déjà
    training_plan_query.filter_by.return_value = training_plan_filter
    
    # Configuration du mock_db.query pour retourner le bon query selon l'argument
    def side_effect_query(model):
        if model == TrainingRequest:
            return training_request_query
        elif model == TrainingPlan:
            return training_plan_query
        return MagicMock()
    
    mock_db.query = MagicMock(side_effect=side_effect_query)
    
    # Simuler l'ajout et l'engagement dans la base de données
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()

    # Appeler la méthode de génération du plan de formation
    TrainingPlanService.generate_plan_if_approved(mock_db, mock_training_request.id)

    # Vérifier que la méthode commit n'a pas été appelée
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()

