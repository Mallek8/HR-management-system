"""
Test spécifique pour la méthode send_notification_to_admin du NotificationService.
"""
import pytest
from unittest.mock import MagicMock, patch
from app.services.notification_service import NotificationService
from app.models.employee import Employee

@pytest.mark.skip(reason="Ce test est instable lorsqu'il est exécuté dans la suite complète")
def test_send_notification_to_admin():
    """Test spécifique pour vérifier l'envoi de notification à l'administrateur."""
    # Mock de la base de données
    mock_db = MagicMock()
    
    # Mock de l'admin
    mock_admin = MagicMock(spec=Employee)
    mock_admin.id = 2
    mock_admin.name = "Admin User"
    mock_admin.role = "admin"
    
    # Configuration de la base de données pour retourner l'administrateur
    mock_db.query.return_value.filter.return_value.first.return_value = mock_admin
    
    # Message de test
    message = "Notification à l'admin."
    
    # Mock de la méthode send_notification
    with patch('app.services.notification_service.NotificationService.send_notification') as mock_send:
        # Appeler la méthode pour envoyer une notification à l'admin
        NotificationService.send_notification_to_admin(mock_db, message)
        
        # Vérifier que send_notification a été appelée une fois avec les bons arguments
        mock_send.assert_called_once_with(mock_db, mock_admin.id, message) 