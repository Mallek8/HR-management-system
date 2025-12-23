import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.models.employee import Employee
from app.models.notification import Notification
from app.models.leave_balance import LeaveBalance
from app.models.training_request import TrainingRequest


@pytest.fixture
def client():
    """Fixture pour créer un client de test"""
    with TestClient(app) as client:
        yield client


def test_create_employee_and_api_integration(client):
    """Test d'intégration de l'API pour créer un employé"""
    
    # Générer un email unique pour éviter les erreurs de doublon
    timestamp = int(time.time())
    unique_email = f"testuser{timestamp}@example.com"
    
    # 1. Créer un employé via l'API
    employee_data = {
        "name": "Test User",
        "email": unique_email,
        "password": "password123",
        "role": "employee",
        "department": "IT",
        "salary": 50000,
        "experience": 5,
        "hire_date": "2023-01-01",
        "birth_date": "1990-01-01",
        "supervisor_id": None  # Ajouter le champ supervisor_id qui est requis par l'API
    }
    
    response = client.post("/api/employees", json=employee_data)
    
    # Si la validation échoue, afficher les détails de l'erreur
    if response.status_code == 422:
        error_details = response.json()
        print(f"Erreur de validation 422: {error_details}")
        # Afficher la réponse complète pour le débogage
        for error in error_details.get("detail", []):
            print(f"- Champ: {error.get('loc', [])} - Message: {error.get('msg', '')}")
    
    # Vérifier que la réponse est correcte
    assert response.status_code == 200, f"Réponse attendue: 200, Reçue: {response.status_code} - {response.text}"
    data = response.json()
    assert data["email"] == unique_email  # Vérification de l'email
    assert data["name"] == "Test User"  # Vérification du nom
    assert data["role"] == "employee"  # Vérification du rôle
    assert "id" in data  # Vérifier que l'id a été généré
    assert data["id"] > 0  # Vérifier que l'id est valide
    
    # Tester d'autres aspects de l'API si nécessaire
    employee_id = data["id"]
    
    # 2. Récupérer l'employé créé via l'API
    response = client.get(f"/api/employees/{employee_id}")
    assert response.status_code == 200
    get_data = response.json()
    assert get_data["id"] == employee_id
    assert get_data["email"] == unique_email
    
    # 3. Mettre à jour l'employé via l'API
    update_data = {
        "name": "Updated User",
        "email": unique_email,
        "role": "employee",
        "department": "HR",  # Changer le département
        "hire_date": "2023-01-01",
        "birth_date": "1990-01-01"
    }
    
    response = client.put(f"/api/employees/{employee_id}", json=update_data)
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["department"] == "HR"  # Vérifier que la mise à jour a été appliquée
