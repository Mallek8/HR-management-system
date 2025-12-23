import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from app.main import app
from app.api.trainings import get_all_trainings, create_training, update_training, delete_training, trainings_page
from app.models.training import Training
from app.database import get_db
from app.schemas import TrainingCreate, TrainingRead

client = TestClient(app)

# Données de test pour les formations
TEST_DATE = date.today()
TEST_TRAINING_DATA = {
    "title": "Formation Test",
    "description": "Description de la formation de test",
    "domain": "Test",
    "level": "Intermédiaire",
    "start_date": TEST_DATE.isoformat(),
    "end_date": (TEST_DATE + timedelta(days=5)).isoformat(),
    "target_department": "IT"
}


@pytest.fixture
def mock_db_session():
    """Fixture pour créer un mock de session de base de données"""
    mock_session = MagicMock()
    return mock_session


# Fonction pour créer un mock de formation avec des attributs valides pour la sérialisation
def create_mock_training(id=1, title="Formation Test"):
    mock_training = MagicMock(spec=Training)
    mock_training.id = id
    mock_training.title = title
    mock_training.description = "Description de la formation de test"
    mock_training.domain = "Test"
    mock_training.level = "Intermédiaire"
    mock_training.start_date = TEST_DATE
    mock_training.end_date = TEST_DATE + timedelta(days=5)
    mock_training.target_department = "IT"
    # Pour la sérialisation en JSON
    mock_training.dict = lambda: {
        "id": mock_training.id,
        "title": mock_training.title,
        "description": mock_training.description,
        "domain": mock_training.domain,
        "level": mock_training.level,
        "start_date": mock_training.start_date,
        "end_date": mock_training.end_date,
        "target_department": mock_training.target_department
    }
    mock_training.__getitem__ = lambda self, key: getattr(self, key)
    return mock_training


@pytest.fixture
def client_with_mocked_db(mock_db_session):
    """Fixture pour créer un client de test avec une base de données mockée"""
    
    def override_get_db():
        return mock_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client, mock_db_session
    
    # Nettoyer après les tests
    app.dependency_overrides.clear()


def test_get_all_trainings_empty(client_with_mocked_db):
    """Test la récupération de toutes les formations quand il n'y en a pas"""
    client, mock_db = client_with_mocked_db
    
    # Configurer le mock pour retourner une liste vide
    mock_db.query.return_value.all.return_value = []
    
    # Faire la requête
    response = client.get("/api/trainings")
    
    # Vérifier la réponse
    assert response.status_code == 200
    assert response.json() == []
    mock_db.query.assert_called_once()


def test_get_all_trainings_with_data(client_with_mocked_db):
    """Test la récupération de toutes les formations avec des données"""
    client, mock_db = client_with_mocked_db
    
    # Créer une vraie instance de Training au lieu d'un mock
    # pour éviter les problèmes de sérialisation
    training = Training(
        id=1,
        title="Formation Test",
        description="Description de la formation de test",
        domain="Test",
        level="Intermédiaire",
        start_date=TEST_DATE,
        end_date=TEST_DATE + timedelta(days=5),
        target_department="IT"
    )
    
    # Configurer le mock pour retourner la formation
    mock_db.query.return_value.all.return_value = [training]
    
    # Faire la requête
    response = client.get("/api/trainings")
    
    # Vérifier la réponse
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert len(result) == 1
    assert "title" in result[0]
    assert result[0]["title"] == "Formation Test"


def test_create_training_success(client_with_mocked_db):
    """Test la création d'une formation avec succès"""
    client, mock_db = client_with_mocked_db
    
    # Configurer le mock pour simuler l'ajout à la base de données
    def side_effect_add(training):
        # Simuler l'ajout d'ID après commit
        training.id = 1
    
    mock_db.add.side_effect = side_effect_add
    
    # Faire la requête
    response = client.post("/api/trainings", json=TEST_TRAINING_DATA)
    
    # Vérifier la réponse
    assert response.status_code == 200
    result = response.json()
    assert "title" in result
    assert result["title"] == TEST_TRAINING_DATA["title"]
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_update_training_success(client_with_mocked_db):
    """Test la mise à jour d'une formation avec succès"""
    client, mock_db = client_with_mocked_db
    
    # Créer un mock de formation existante
    mock_training = MagicMock()
    mock_training.id = 1
    mock_training.title = "Ancien Titre"
    
    # Configurer le mock pour retourner la formation
    mock_db.query.return_value.filter.return_value.first.return_value = mock_training
    
    # Préparer les données de mise à jour
    updated_data = dict(TEST_TRAINING_DATA)
    updated_data["title"] = "Formation Mise à Jour"
    
    # Faire la requête
    response = client.put("/api/trainings/1", json=updated_data)
    
    # Vérifier la réponse
    assert response.status_code == 200
    
    # Vérifier que les attributs ont été mis à jour
    assert mock_training.title == updated_data["title"]
    assert mock_training.description == updated_data["description"]
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_update_training_not_found(client_with_mocked_db):
    """Test la mise à jour d'une formation inexistante"""
    client, mock_db = client_with_mocked_db
    
    # Configurer le mock pour ne pas trouver la formation
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Faire la requête
    response = client.put("/api/trainings/999", json=TEST_TRAINING_DATA)
    
    # Vérifier la réponse
    assert response.status_code == 404
    assert "detail" in response.json()
    assert response.json()["detail"] == "Formation non trouvée"
    mock_db.commit.assert_not_called()


def test_delete_training_success(client_with_mocked_db):
    """Test la suppression d'une formation avec succès"""
    client, mock_db = client_with_mocked_db
    
    # Créer un mock de formation existante
    mock_training = MagicMock()
    mock_training.id = 1
    
    # Configurer le mock pour retourner la formation
    mock_db.query.return_value.filter.return_value.first.return_value = mock_training
    
    # Faire la requête
    response = client.delete("/api/trainings/1")
    
    # Vérifier la réponse
    assert response.status_code == 204
    assert response.content == b''  # Corps vide pour 204 No Content
    mock_db.delete.assert_called_once_with(mock_training)
    mock_db.commit.assert_called_once()


def test_delete_training_not_found(client_with_mocked_db):
    """Test la suppression d'une formation inexistante"""
    client, mock_db = client_with_mocked_db
    
    # Configurer le mock pour ne pas trouver la formation
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Faire la requête
    response = client.delete("/api/trainings/999")
    
    # Vérifier la réponse
    assert response.status_code == 404
    assert "detail" in response.json()
    assert response.json()["detail"] == "Formation non trouvée"
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()


# Tests des fonctions directement
def test_get_trainings_page(client_with_mocked_db):
    """Test l'affichage de la page des formations"""
    client, _ = client_with_mocked_db
    
    # Faire la requête
    response = client.get("/trainings")
    
    # Vérifier la réponse
    assert response.status_code == 200
    # Vérifier qu'il s'agit bien d'une réponse HTML et non d'une API
    assert "text/html" in response.headers["content-type"]


# Tests directs des fonctions d'API
def test_function_get_all_trainings(mock_db_session):
    """Test la fonction get_all_trainings directement"""
    # Configuration du mock
    mock_training = MagicMock(spec=Training)
    mock_db_session.query.return_value.all.return_value = [mock_training]
    
    # Appel de la fonction
    result = get_all_trainings(db=mock_db_session)
    
    # Vérifications
    assert result == [mock_training]
    mock_db_session.query.assert_called_once_with(Training)


def test_function_create_training(mock_db_session):
    """Test la fonction create_training directement"""
    # Préparation des données
    training_create = TrainingCreate(
        title="Formation Test Direct",
        description="Description de la formation de test direct",
        domain="Test Direct",
        level="Avancé",
        start_date=TEST_DATE,
        end_date=TEST_DATE + timedelta(days=10),
        target_department="RH"
    )
    
    # Configuration du mock
    def mock_db_add(training):
        training.id = 2
        
    mock_db_session.add.side_effect = mock_db_add
    
    # Appel de la fonction
    result = create_training(training=training_create, db=mock_db_session)
    
    # Vérifications
    assert result.id == 2
    assert result.title == "Formation Test Direct"
    assert result.target_department == "RH"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_function_update_training(mock_db_session):
    """Test la fonction update_training directement"""
    # Préparation des données
    training_id = 3
    updated_data = TrainingCreate(
        title="Formation Mise à Jour Direct",
        description="Description mise à jour",
        domain="Test Mise à Jour",
        level="Débutant",
        start_date=TEST_DATE,
        end_date=TEST_DATE + timedelta(days=3),
        target_department="Finance"
    )
    
    # Mock de formation existante
    mock_training = MagicMock(spec=Training)
    mock_training.id = training_id
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_training
    
    # Appel de la fonction
    result = update_training(training_id=training_id, updated=updated_data, db=mock_db_session)
    
    # Vérifications
    assert result == mock_training
    assert mock_training.title == "Formation Mise à Jour Direct"
    assert mock_training.target_department == "Finance"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_training)


def test_function_delete_training(mock_db_session):
    """Test la fonction delete_training directement"""
    # Préparation
    training_id = 4
    mock_training = MagicMock(spec=Training)
    mock_training.id = training_id
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_training
    
    # Appel de la fonction
    result = delete_training(training_id=training_id, db=mock_db_session)
    
    # Vérifications
    assert result is None  # La fonction retourne None
    mock_db_session.delete.assert_called_once_with(mock_training)
    mock_db_session.commit.assert_called_once() 