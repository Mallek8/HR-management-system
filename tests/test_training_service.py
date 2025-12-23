import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.services.training_service import TrainingService
from app.models.training import Training
from app.models.training_request import TrainingRequest
from app.models.employee import Employee


@pytest.fixture
def mock_db_session():
    """Fixture pour simuler une session de base de données."""
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def mock_training():
    """Fixture pour créer une formation mockée."""
    training = MagicMock(spec=Training)
    training.id = 1
    training.title = "Formation Python Avancée"
    training.description = "Apprenez Python en profondeur"
    training.duration = 20
    training.max_participants = 10
    training.employees = []
    return training


@pytest.fixture
def mock_employee():
    """Fixture pour créer un employé mocké."""
    employee = MagicMock(spec=Employee)
    employee.id = 1
    employee.name = "Test Employee"
    employee.email = "test@example.com"
    employee.trainings = []
    return employee


@pytest.fixture
def mock_training_request():
    """Fixture pour créer une demande de formation mockée."""
    request = MagicMock(spec=TrainingRequest)
    request.id = 1
    request.employee_id = 1
    request.title = "Formation Python"
    request.description = "Je souhaite améliorer mes compétences en Python"
    request.status = "en attente"
    return request


def test_create_training(mock_db_session, mock_training):
    """Test pour créer une formation."""
    # Configurer le mock pour que db.commit() ne fasse rien
    training_data = {
        "title": "Formation Python Avancée",
        "description": "Apprenez Python en profondeur",
        "duration": 20,
        "max_participants": 10
    }
    
    # Configurer le mock pour simuler la création d'une formation
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None
    
    # Mocker Training pour renvoyer l'objet mock_training quand il est créé
    with patch('app.services.training_service.Training', return_value=mock_training):
        result = TrainingService.create_training(mock_db_session, training_data)
    
    # Vérifier que la formation a bien été créée
    assert result == mock_training
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_create_training_error(mock_db_session):
    """Test de gestion des erreurs lors de la création d'une formation."""
    # Configurer le mock pour lever une exception lors du commit
    mock_db_session.commit.side_effect = Exception("Database error")
    
    training_data = {
        "title": "Formation Python Avancée",
        "description": "Apprenez Python en profondeur",
        "duration": 20,
        "max_participants": 10
    }
    
    # Créer une formation (qui va échouer)
    result = TrainingService.create_training(mock_db_session, training_data)
    
    # Vérifier que l'erreur est gérée correctement
    assert result is None
    mock_db_session.rollback.assert_called_once()


def test_get_all_trainings(mock_db_session):
    """Test pour récupérer toutes les formations."""
    # Créer des formations mockées
    training1 = MagicMock(spec=Training)
    training1.id = 1
    training1.title = "Formation Python"
    
    training2 = MagicMock(spec=Training)
    training2.id = 2
    training2.title = "Formation Java"
    
    # Configurer le mock pour retourner les formations
    mock_db_session.query.return_value.all.return_value = [training1, training2]
    
    # Récupérer les formations
    trainings = TrainingService.get_all_trainings(mock_db_session)
    
    # Vérifier les résultats
    assert len(trainings) == 2
    assert trainings[0].id == 1
    assert trainings[1].id == 2


def test_get_training_by_id(mock_db_session, mock_training):
    """Test pour récupérer une formation par son ID."""
    # Configurer le mock pour retourner la formation
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_training
    
    # Récupérer la formation
    training = TrainingService.get_training_by_id(mock_db_session, 1)
    
    # Vérifier les résultats
    assert training.id == 1
    assert training.title == "Formation Python Avancée"


def test_update_training(mock_db_session, mock_training):
    """Test pour mettre à jour une formation existante."""
    # Configurer le mock pour retourner la formation
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_training
    
    # Données de mise à jour
    update_data = {
        "title": "Nouveau titre",
        "description": "Nouvelle description"
    }
    
    # Mettre à jour la formation
    result = TrainingService.update_training(mock_db_session, 1, update_data)
    
    # Vérifier les résultats
    assert result == mock_training
    assert mock_training.title == "Nouveau titre"
    assert mock_training.description == "Nouvelle description"
    mock_db_session.commit.assert_called_once()


def test_update_training_not_found(mock_db_session):
    """Test pour mettre à jour une formation inexistante."""
    # Configurer le mock pour retourner None (formation non trouvée)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Données de mise à jour
    update_data = {
        "title": "Nouveau titre",
        "description": "Nouvelle description"
    }
    
    # Mettre à jour la formation
    result = TrainingService.update_training(mock_db_session, 999, update_data)
    
    # Vérifier les résultats
    assert result is None
    mock_db_session.commit.assert_not_called()


def test_update_training_error(mock_db_session, mock_training):
    """Test de gestion des erreurs lors de la mise à jour d'une formation."""
    # Configurer le mock pour retourner la formation
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_training
    
    # Configurer le mock pour lever une exception lors du commit
    mock_db_session.commit.side_effect = Exception("Database error")
    
    # Données de mise à jour
    update_data = {
        "title": "Nouveau titre",
        "description": "Nouvelle description"
    }
    
    # Mettre à jour la formation
    result = TrainingService.update_training(mock_db_session, 1, update_data)
    
    # Vérifier les résultats
    assert result is None
    mock_db_session.rollback.assert_called_once()


def test_delete_training(mock_db_session, mock_training):
    """Test pour supprimer une formation."""
    # Configurer le mock pour retourner la formation
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_training
    
    # Supprimer la formation
    result = TrainingService.delete_training(mock_db_session, 1)
    
    # Vérifier les résultats
    assert result is True
    mock_db_session.delete.assert_called_once_with(mock_training)
    mock_db_session.commit.assert_called_once()


def test_delete_training_not_found(mock_db_session):
    """Test pour supprimer une formation inexistante."""
    # Configurer le mock pour retourner None (formation non trouvée)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Supprimer la formation
    result = TrainingService.delete_training(mock_db_session, 999)
    
    # Vérifier les résultats
    assert result is False
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_delete_training_error(mock_db_session, mock_training):
    """Test de gestion des erreurs lors de la suppression d'une formation."""
    # Configurer le mock pour retourner la formation
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_training
    
    # Configurer le mock pour lever une exception lors du commit
    mock_db_session.commit.side_effect = Exception("Database error")
    
    # Supprimer la formation
    result = TrainingService.delete_training(mock_db_session, 1)
    
    # Vérifier les résultats
    assert result is False
    mock_db_session.rollback.assert_called_once()


def test_create_training_request(mock_db_session, mock_training_request):
    """Test pour créer une demande de formation."""
    # Données de la demande
    request_data = {
        "employee_id": 1,
        "title": "Formation Python",
        "description": "Je souhaite améliorer mes compétences en Python",
        "status": "en attente"
    }
    
    # Configurer le mock pour simuler la création d'une demande
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None
    
    # Mocker TrainingRequest pour renvoyer l'objet mock_training_request quand il est créé
    with patch('app.services.training_service.TrainingRequest', return_value=mock_training_request):
        result = TrainingService.create_training_request(mock_db_session, request_data)
    
    # Vérifier que la demande a bien été créée
    assert result == mock_training_request
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_get_training_requests_for_employee(mock_db_session, mock_training_request):
    """Test pour récupérer les demandes de formation d'un employé."""
    # Configurer le mock pour retourner les demandes
    mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_training_request]
    
    # Récupérer les demandes
    requests = TrainingService.get_training_requests_for_employee(mock_db_session, 1)
    
    # Vérifier les résultats
    assert len(requests) == 1
    assert requests[0].id == 1
    assert requests[0].employee_id == 1
    assert requests[0].status == "en attente"


def test_get_trainings_by_employee(mock_db_session, mock_employee, mock_training):
    """Test pour récupérer les formations suivies par un employé."""
    # Configurer le mock pour retourner l'employé
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_employee
    
    # Ajouter des formations à l'employé
    mock_employee.trainings = [mock_training]
    
    # Récupérer les formations
    trainings = TrainingService.get_trainings_by_employee(mock_db_session, 1)
    
    # Vérifier les résultats
    assert len(trainings) == 1
    assert trainings[0].id == 1
    assert trainings[0].title == "Formation Python Avancée"


def test_get_trainings_by_employee_not_found(mock_db_session):
    """Test pour récupérer les formations d'un employé inexistant."""
    # Configurer le mock pour retourner None (employé non trouvé)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Récupérer les formations
    trainings = TrainingService.get_trainings_by_employee(mock_db_session, 999)
    
    # Vérifier les résultats
    assert trainings == []


def test_get_trainings_by_employee_error(mock_db_session):
    """Test de gestion des erreurs lors de la récupération des formations d'un employé."""
    # Configurer le mock pour lever une exception
    mock_db_session.query.side_effect = SQLAlchemyError("Database error")
    
    # Récupérer les formations
    trainings = TrainingService.get_trainings_by_employee(mock_db_session, 1)
    
    # Vérifier les résultats
    assert trainings == []
    mock_db_session.rollback.assert_called_once()


def test_register_employee_to_training(mock_db_session, mock_employee, mock_training):
    """Test pour inscrire un employé à une formation."""
    # Configurer les mocks pour retourner l'employé et la formation
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_employee, mock_training]
    
    # Inscrire l'employé
    result = TrainingService.register_employee_to_training(mock_db_session, 1, 1)
    
    # Vérifier les résultats
    assert result["success"] is True
    assert "inscrit" in result["message"]
    mock_db_session.commit.assert_called_once()


def test_register_employee_to_training_already_registered(mock_db_session, mock_employee, mock_training):
    """Test pour inscrire un employé déjà inscrit à une formation."""
    # Ajouter la formation à l'employé (déjà inscrit)
    mock_employee.trainings = [mock_training]
    
    # Configurer les mocks pour retourner l'employé et la formation
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_employee, mock_training]
    
    # Inscrire l'employé
    result = TrainingService.register_employee_to_training(mock_db_session, 1, 1)
    
    # Vérifier les résultats
    assert result["success"] is False
    assert "déjà inscrit" in result["message"]
    mock_db_session.commit.assert_not_called()


def test_unregister_employee_from_training(mock_db_session, mock_employee, mock_training):
    """Test pour désinscrire un employé d'une formation."""
    # Ajouter la formation à l'employé (déjà inscrit)
    mock_employee.trainings = [mock_training]
    
    # Configurer les mocks pour retourner l'employé et la formation
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_employee, mock_training]
    
    # Désinscrire l'employé
    result = TrainingService.unregister_employee_from_training(mock_db_session, 1, 1)
    
    # Vérifier les résultats
    assert result["success"] is True
    assert "désinscrit" in result["message"]
    mock_db_session.commit.assert_called_once()


def test_get_training_stats_for_employee(mock_db_session, mock_training_request):
    """Test pour récupérer les statistiques de formation d'un employé."""
    # Créer des demandes avec différents statuts
    request1 = MagicMock(spec=TrainingRequest)
    request1.status = "en attente"
    
    request2 = MagicMock(spec=TrainingRequest)
    request2.status = "approuvé"
    
    request3 = MagicMock(spec=TrainingRequest)
    request3.status = "refusé"
    
    # Configurer le mock pour retourner les demandes
    mock_db_session.query.return_value.filter.return_value.all.return_value = [request1, request2, request3]
    
    # Récupérer les statistiques
    stats = TrainingService.get_training_stats_for_employee(mock_db_session, 1)
    
    # Vérifier les résultats
    assert stats["total"] == 3
    assert stats["sent"] == 1
    assert stats["approved"] == 1
    assert stats["rejected"] == 1


def test_get_training_stats_for_employee_error(mock_db_session):
    """Test de gestion des erreurs lors de la récupération des statistiques."""
    # Configurer le mock pour lever une exception
    mock_db_session.query.side_effect = Exception("Database error")
    
    # Récupérer les statistiques
    stats = TrainingService.get_training_stats_for_employee(mock_db_session, 1)
    
    # Vérifier les résultats par défaut en cas d'erreur
    assert stats["total"] == 0
    assert stats["sent"] == 0
    assert stats["approved"] == 0
    assert stats["rejected"] == 0 