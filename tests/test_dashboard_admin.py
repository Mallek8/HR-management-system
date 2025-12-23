import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

# Crée une instance de TestClient
client = TestClient(app)

# Test pour la route du tableau de bord de l'administrateur RH
def test_dashboard_admin():
    response = client.get("/dashboard_admin")
    assert response.status_code == 200
    assert "Tableau de Bord" in response.text
    assert "EMPLOYÉS ACTIFS" in response.text
    assert "CONGÉS EN ATTENTE" in response.text
    assert "FORMATIONS VALIDÉES" in response.text
    assert "OBJECTIFS ATTEINTS" in response.text

# Test pour la page des employés
def test_employees_page():
    response = client.get("/employees")
    assert response.status_code == 200
    assert (
        "Liste des employés" in response.text
        or "Ajouter un employé" in response.text
        or "Nom" in response.text
    )

# Test pour la page des congés
def test_leaves_page():
    response = client.get("/leaves")
    assert response.status_code == 200
    assert (
        "Liste des demandes de congés" in response.text
        or "Panneau d'administration des congés" in response.text
        or "Calendrier des absences" in response.text
    )

# Test pour la page des évaluations
def test_evaluations_page():
    response = client.get("/evaluations")
    assert response.status_code == 200
    assert "Évaluations" in response.text or "Performance" in response.text

# Test pour l'API des statistiques admin
def test_api_admin_stats():
    response = client.get("/api/admin/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_employees" in stats
    assert "pending_leaves" in stats
    assert "approved_trainings" in stats
    assert "achieved_goals" in stats
    assert "timestamp" in stats

# Test pour l'API des notifications administrateur
@patch("app.services.notification_service.NotificationService.get_admin_notifications")
def test_get_admin_notifications(mock_get_admin_notifications):
    mock_get_admin_notifications.return_value = {"message": "Notification admin test"}
    response = client.get("/api/admin/notifications")
    assert response.status_code == 200
    assert response.json() == {"message": "Notification admin test"}

# Test pour l'API des notifications générales
@patch("app.services.notification_service.NotificationService.get_general_notifications")
def test_get_general_notifications(mock_get_general_notifications):
    mock_get_general_notifications.return_value = {"message": "Notification générale test"}
    response = client.get("/api/notifications")
    assert response.status_code == 200
    assert response.json() == {"message": "Notification générale test"}
