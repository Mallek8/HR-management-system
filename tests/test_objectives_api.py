import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.api.objectives import create_objective, get_employee_objectives, format_date
from app.models.objective import Objective
from app.schemas import ObjectiveCreate


@pytest.fixture
def mock_db_session():
    """Fixture pour simuler une session de base de données."""
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def sample_objective_data():
    """Fixture pour des données d'objectif."""
    return {
        "description": "Apprendre FastAPI",
        "employee_id": 1,
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "progress": 0
    }


def test_create_objective(mock_db_session, sample_objective_data):
    """Test de la création d'un objectif."""
    # Créer un objectif avec les données de test
    objective_create = ObjectiveCreate(**sample_objective_data)
    
    # Configurer le comportement de la base de données
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()
    
    # Exécuter la fonction
    result = create_objective(objective_create, mock_db_session)
    
    # Vérifications
    assert mock_db_session.add.called
    assert mock_db_session.commit.called
    assert mock_db_session.refresh.called
    
    # Vérifier les propriétés de l'objectif créé
    objective_added = mock_db_session.add.call_args[0][0]
    assert objective_added.description == sample_objective_data["description"]
    assert objective_added.employee_id == sample_objective_data["employee_id"]
    assert objective_added.progress == sample_objective_data["progress"]


def test_create_objective_error(mock_db_session, sample_objective_data):
    """Test de la création d'un objectif avec une erreur."""
    # Créer un objectif avec les données de test
    objective_create = ObjectiveCreate(**sample_objective_data)
    
    # Simuler une erreur lors de l'ajout à la base de données
    mock_db_session.add.side_effect = Exception("Database error")
    
    # Vérifier que l'exception est bien levée
    with pytest.raises(HTTPException) as excinfo:
        create_objective(objective_create, mock_db_session)
    
    # Vérifier le code d'erreur et le message
    assert excinfo.value.status_code == 500
    assert "Erreur lors de la création d'un objectif" in excinfo.value.detail


def test_get_employee_objectives(mock_db_session):
    """Test de la récupération des objectifs d'un employé."""
    # Créer quelques objectifs factices
    objective1 = MagicMock(spec=Objective)
    objective1.employee_id = 1
    objective1.description = "Objectif 1"
    objective1.start_date = datetime(2023, 1, 1)
    objective1.end_date = datetime(2023, 6, 30)
    objective1.progress = 50
    
    objective2 = MagicMock(spec=Objective)
    objective2.employee_id = 1
    objective2.description = "Objectif 2"
    objective2.start_date = datetime(2023, 7, 1)
    objective2.end_date = datetime(2023, 12, 31)
    objective2.progress = 0
    
    # Configurer le comportement de la requête
    mock_db_session.query.return_value.filter.return_value.all.return_value = [objective1, objective2]
    
    # Exécuter la fonction
    result = get_employee_objectives(1, mock_db_session)
    
    # Vérifications
    assert len(result) == 2
    assert result[0].description == "Objectif 1"
    assert result[1].description == "Objectif 2"
    
    # Vérifier que les dates sont formatées
    assert hasattr(result[0], 'start_date')
    assert hasattr(result[0], 'end_date')


def test_get_employee_objectives_empty(mock_db_session):
    """Test de la récupération des objectifs d'un employé sans objectifs."""
    # Configurer le comportement de la requête pour retourner une liste vide
    mock_db_session.query.return_value.filter.return_value.all.return_value = []
    
    # Exécuter la fonction
    result = get_employee_objectives(1, mock_db_session)
    
    # Vérifications
    assert result == []


def test_format_date_datetime():
    """Test de la fonction format_date avec un objet datetime."""
    date_obj = datetime(2023, 1, 15)
    result = format_date(date_obj)
    assert result == "2023-01-15"


def test_format_date_string_iso():
    """Test de la fonction format_date avec une chaîne ISO."""
    date_str = "2023-01-15T12:30:45"
    result = format_date(date_str)
    assert result == "2023-01-15"


def test_format_date_string_simple():
    """Test de la fonction format_date avec une chaîne simple."""
    date_str = "2023-01-15"
    result = format_date(date_str)
    assert result == "2023-01-15"


def test_format_date_invalid_string():
    """Test de la fonction format_date avec une chaîne invalide."""
    date_str = "invalid-date"
    result = format_date(date_str)
    assert result == "invalid-date"  # Devrait retourner la valeur telle quelle


def test_format_date_other_type():
    """Test de la fonction format_date avec un autre type."""
    value = 123
    result = format_date(value)
    assert result == 123  # Devrait retourner la valeur telle quelle


def test_create_objective_mock_dict_method(mock_db_session, sample_objective_data):
    """Test de la création d'un objectif en mockant la méthode dict()."""
    # Créer un mock de l'objet ObjectiveCreate
    objective_create = MagicMock()
    objective_create.model_dump = MagicMock(side_effect=AttributeError)  # Force l'utilisation de dict()
    objective_create.dict = MagicMock(return_value=sample_objective_data)
    
    # Configurer le comportement de la base de données
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()
    
    # Exécuter la fonction avec try/except pour capturer les exceptions potentielles
    try:
        result = create_objective(objective_create, mock_db_session)
        
        # Vérifications
        assert mock_db_session.add.called
        assert mock_db_session.commit.called
        assert mock_db_session.refresh.called
        
        # Vérifier que l'objectif a bien été créé
        added_objective = mock_db_session.add.call_args[0][0]
        assert isinstance(added_objective, Objective)
        assert added_objective.description == sample_objective_data["description"]
        assert added_objective.employee_id == sample_objective_data["employee_id"]
        
    except Exception as e:
        pytest.fail(f"create_objective a levé une exception inattendue: {e}") 