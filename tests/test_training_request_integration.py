import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.models.employee import Employee
from app.models.training_request import TrainingRequest
from app.models.training_plan import TrainingPlan
from datetime import datetime, date

@pytest.fixture
def client():
    """Fixture pour créer un client de test"""
    with TestClient(app) as client:
        yield client

def test_training_request_simplified(client):
    """
    Test d'intégration simplifié pour la création d'un employé, d'une formation
    et d'une demande de formation.
    """
    
    # Générer des emails uniques pour éviter les erreurs de doublon
    timestamp = int(time.time() * 1000)  # Utiliser des millisecondes pour plus d'unicité
    employee_email = f"testemployee{timestamp}@example.com"
    
    # 1. Créer un employé via l'API
    employee_data = {
        "name": "Employee Test",
        "email": employee_email,
        "password": "password123",
        "role": "employee",
        "department": "HR",
        "salary": 40000,
        "experience": 2,
        "hire_date": "2021-05-10",
        "birth_date": "1990-08-15",
        "supervisor_id": None,
        "status": True
    }

    response = client.post("/api/employees", json=employee_data)
    assert response.status_code == 200, f"Réponse attendue: 200, Reçue: {response.status_code} - {response.text}"  # Employé créé
    employee_id = response.json()["id"]
    
    # 2. Créer une formation de test
    training_data = {
        "title": f"Formation Test {timestamp}",
        "description": "Description de la formation de test",
        "domain": "Test Domain",
        "level": "Débutant",
        "start_date": str(date.today()),
        "end_date": str(date.today()),
        "target_department": "HR"
    }
    
    response = client.post("/api/trainings", json=training_data)
    assert response.status_code == 200, f"Réponse attendue: 200, Reçue: {response.status_code} - {response.text}"  # Formation créée
    training_id = response.json()["id"]
    
    # 3. Créer une demande de formation pour cet employé
    training_request_data = {
        "employee_id": employee_id,
        "training_id": training_id,  # Utiliser l'ID de la formation créée
        "status": "en attente",
        "training_type": "Leadership Development"
    }

    response = client.post("/api/training-requests", json=training_request_data)
    assert response.status_code == 200, f"Réponse attendue: 200, Reçue: {response.status_code} - {response.text}"  # Demande de formation créée
    training_request_id = response.json()["id"]
    
    # 4. Vérifier que les demandes de formation sont accessibles via l'endpoint "full"
    response = client.get("/api/training-requests/full")
    assert response.status_code == 200, f"Réponse attendue: 200, Reçue: {response.status_code} - {response.text}"
    
    # Vérifier que notre demande existe dans la liste
    found = False
    for request in response.json():
        if request["id"] == training_request_id:
            found = True
            assert request["status"] == "en attente"  # La demande est en attente
            break
    
    assert found, f"La demande de formation avec l'ID {training_request_id} n'a pas été trouvée dans la liste"
    
    print(f"Test réussi - Employé {employee_id}, Formation {training_id}, Demande de formation {training_request_id} créés avec succès")

def test_create_and_approve_training_request(client):
    """
    Test d'intégration pour la création et l'approbation d'une demande de formation.
    """
    
    # Générer des emails uniques pour éviter les erreurs de doublon
    timestamp = int(time.time() * 1000)  # Utiliser des millisecondes pour plus d'unicité
    employee_email = f"emp{timestamp}@example.com"
    supervisor_email = f"sup{timestamp}@example.com"
    
    # 1. Créer un employé via l'API
    employee_data = {
        "name": "Employee Test",
        "email": employee_email,
        "password": "password123",
        "role": "employee",
        "department": "HR",
        "salary": 40000,
        "experience": 2,
        "hire_date": "2021-05-10",
        "birth_date": "1990-08-15",
        "supervisor_id": None,
        "status": True
    }

    response = client.post("/api/employees", json=employee_data)
    assert response.status_code == 200, f"Réponse attendue: 200, Reçue: {response.status_code} - {response.text}"
    employee_id = response.json()["id"]
    
    # 2. Créer un superviseur
    supervisor_data = {
        "name": "Supervisor Test",
        "email": supervisor_email,
        "password": "password123",
        "role": "supervisor",
        "department": "HR",
        "salary": 60000,
        "experience": 5,
        "hire_date": "2018-03-12",
        "birth_date": "1985-11-02",
        "supervisor_id": None,
        "status": True
    }

    response = client.post("/api/employees", json=supervisor_data)
    assert response.status_code == 200, f"Réponse attendue: 200, Reçue: {response.status_code} - {response.text}"
    supervisor_id = response.json()["id"]
    
    # 3. Créer une formation de test
    training_data = {
        "title": f"Formation Test {timestamp}",
        "description": "Description de la formation de test",
        "domain": "Test Domain",
        "level": "Débutant",
        "start_date": str(date.today()),
        "end_date": str(date.today()),
        "target_department": "HR"
    }
    
    response = client.post("/api/trainings", json=training_data)
    assert response.status_code == 200, f"Réponse attendue: 200, Reçue: {response.status_code} - {response.text}"
    training_id = response.json()["id"]
    
    # 4. Créer une demande de formation
    training_request_data = {
        "employee_id": employee_id,
        "training_id": training_id,
        "status": "en attente",
        "training_type": "Leadership Development"
    }

    response = client.post("/api/training-requests", json=training_request_data)
    assert response.status_code == 200, f"Réponse attendue: 200, Reçue: {response.status_code} - {response.text}"
    training_request_id = response.json()["id"]
    
    # 5. Vérifier que la demande apparaît dans la liste complète
    response = client.get("/api/training-requests/full")
    assert response.status_code == 200, f"Réponse attendue: 200, Reçue: {response.status_code} - {response.text}"
    
    request_found = False
    for req in response.json():
        if req["id"] == training_request_id:
            request_found = True
            assert req["status"] == "en attente"
            break
    
    assert request_found, "La demande de formation n'a pas été trouvée dans la liste complète"
    
    print(f"Test réussi - Employé, superviseur, formation et demande de formation créés avec succès")
