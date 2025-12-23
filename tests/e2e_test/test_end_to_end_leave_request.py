import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

@pytest.fixture
def client():
    """Fixture pour créer un client de test"""
    with TestClient(app) as client:
        yield client


def test_e2e_leave_request(client):
    """Test End-to-End de base pour la création d'une demande de congé"""

    # Générer des emails uniques pour éviter les erreurs de doublon
    timestamp = int(time.time())
    employee_email = f"testemployee{timestamp}@example.com"

    # 1. Créer un employé via l'API
    employee_data = {
        "name": "Test Employee",
        "email": employee_email,
        "password": "password123",
        "role": "employee",
        "department": "HR",
        "salary": 45000,
        "experience": 3,
        "hire_date": "2022-01-01",
        "birth_date": "1990-01-01",
        "supervisor_id": None,
        "status": True
    }

    response = client.post("/api/employees", json=employee_data)
    assert response.status_code == 200, f"Réponse attendue: 200, Reçue: {response.status_code} - {response.text}"  # Employé créé
    employee_id = response.json()["id"]
    
    # 2. Vérifier si l'employé existe
    response = client.get(f"/api/employees/{employee_id}")
    assert response.status_code == 200, f"L'employé n'a pas été correctement créé: {response.text}"
    
    # 3. Créer une demande de congé pour l'employé
    leave_data = {
        "employee_id": employee_id,
        "type": "Vacances",
        "start_date": "2025-06-01T00:00:00",
        "end_date": "2025-06-10T00:00:00"
    }
    response = client.post("/request-leave/", json=leave_data)
    assert response.status_code == 200, f"Erreur lors de la création de la demande de congé: {response.text}"
    leave_request_id = response.json().get("id")
    assert leave_request_id is not None, "L'ID de la demande de congé n'a pas été retourné"
    
    # Test réussi
    print(f"Test réussi - Demande de congé {leave_request_id} créée pour l'employé {employee_id}")
