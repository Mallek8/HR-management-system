import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from datetime import date


@pytest.fixture
def client():
    """Fixture pour créer un client de test"""
    with TestClient(app) as client:
        yield client


def test_create_leave_request_api(client):
    """Test d'intégration pour les API de demande de congé"""
    
    # Générer des emails uniques pour éviter les erreurs de doublon
    timestamp = int(time.time())
    employee_email = f"employee{timestamp}@example.com"
    supervisor_email = f"supervisor{timestamp}@example.com"
    
    # 1. Créer un employé via l'API
    response = client.post("/api/employees", json={
        "name": "Test Employee",
        "email": employee_email,
        "password": "password123",
        "role": "employee",
        "department": "HR",
        "salary": 45000,
        "experience": 3,
        "hire_date": "2022-01-01",
        "birth_date": "1990-01-01",
        "supervisor_id": None
    })
    
    # Vérifier que l'employé a été créé correctement
    assert response.status_code == 200, f"Réponse attendue: 200, Reçue: {response.status_code} - {response.text}"
    employee_data = response.json()
    employee_id = employee_data["id"]
    assert employee_data["email"] == employee_email
    
    # 2. Créer un superviseur via l'API
    response = client.post("/api/employees", json={
        "name": "Test Supervisor",
        "email": supervisor_email,
        "password": "password123",
        "role": "supervisor",
        "department": "HR",
        "salary": 60000,
        "experience": 5,
        "hire_date": "2020-01-01",
        "birth_date": "1985-01-01",
        "supervisor_id": None
    })
    
    # Vérifier que le superviseur a été créé correctement
    assert response.status_code == 200
    supervisor_data = response.json()
    supervisor_id = supervisor_data["id"]
    assert supervisor_data["email"] == supervisor_email
    
    # Tester la récupération de l'employé
    response = client.get(f"/api/employees/{employee_id}")
    assert response.status_code == 200
    assert response.json()["id"] == employee_id
    
    # Tester la récupération du superviseur
    response = client.get(f"/api/employees/{supervisor_id}")
    assert response.status_code == 200
    assert response.json()["id"] == supervisor_id
    
    # 3. Tester la récupération de tous les employés
    response = client.get("/api/employees")
    assert response.status_code == 200
    employees = response.json()
    assert len(employees) > 0
    
    # Vérifier que nos employés se trouvent dans la liste
    employee_found = False
    supervisor_found = False
    
    for emp in employees:
        if emp["id"] == employee_id:
            employee_found = True
        if emp["id"] == supervisor_id:
            supervisor_found = True
    
    assert employee_found, "L'employé créé n'a pas été trouvé dans la liste des employés"
    assert supervisor_found, "Le superviseur créé n'a pas été trouvé dans la liste des employés"
