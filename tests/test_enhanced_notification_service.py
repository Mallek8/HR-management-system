import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.services.enhanced_notification_service import EnhancedNotificationService
from app.strategies.notifications.notification_context import NotificationContext


@pytest.fixture
def mock_db_session():
    """Fixture for mocked database session"""
    mock_session = MagicMock(spec=Session)
    return mock_session


@patch.object(NotificationContext, 'set_strategy')
@patch.object(NotificationContext, 'send_notification')
def test_send_notification(mock_send, mock_set, mock_db_session):
    """Test sending a notification using EnhancedNotificationService"""
    # Setup
    employee_id = 1
    message = "Test notification"
    channel = "email"
    
    # Mock return value
    mock_send.return_value = True
    
    # Execute
    result = EnhancedNotificationService.send_notification(
        mock_db_session, employee_id, message, channel
    )
    
    # Assert
    assert result is True
    mock_set.assert_called_once_with(channel)
    mock_send.assert_called_once_with(employee_id, message)


@patch.object(NotificationContext, 'set_strategy')
@patch.object(NotificationContext, 'send_notification')
def test_send_notification_default_channel(mock_send, mock_set, mock_db_session):
    """Test sending a notification with default channel"""
    # Setup
    employee_id = 1
    message = "Test notification"
    
    # Mock return value
    mock_send.return_value = True
    
    # Execute
    result = EnhancedNotificationService.send_notification(
        mock_db_session, employee_id, message
    )
    
    # Assert
    assert result is True
    mock_set.assert_called_once_with("in-app")
    mock_send.assert_called_once_with(employee_id, message)


@patch.object(NotificationContext, 'send_multi_channel')
def test_send_multi_channel_notification(mock_send_multi, mock_db_session):
    """Test sending a notification through multiple channels"""
    # Setup
    employee_id = 1
    message = "Test notification"
    channels = ["in-app", "email"]
    
    # Mock return value
    mock_send_multi.return_value = {
        "in-app": True,
        "email": True,
        "sms": False
    }
    
    # Execute
    result = EnhancedNotificationService.send_multi_channel_notification(
        mock_db_session, employee_id, message, channels
    )
    
    # Assert
    assert result == mock_send_multi.return_value
    mock_send_multi.assert_called_once_with(employee_id, message, channels)


@patch.object(NotificationContext, 'send_multi_channel')
def test_send_multi_channel_notification_no_channels(mock_send_multi, mock_db_session):
    """Test sending a notification through all channels (None specified)"""
    # Setup
    employee_id = 1
    message = "Test notification"
    
    # Mock return value
    mock_send_multi.return_value = {
        "in-app": True,
        "email": True,
        "sms": True
    }
    
    # Execute
    result = EnhancedNotificationService.send_multi_channel_notification(
        mock_db_session, employee_id, message
    )
    
    # Assert
    assert result == mock_send_multi.return_value
    mock_send_multi.assert_called_once_with(employee_id, message, None)


@patch('app.database.SessionLocal')
@patch.object(NotificationContext, 'get_available_strategies')
def test_get_available_channels(mock_get_strategies, mock_session_local, mock_db_session):
    """Test getting available notification channels"""
    # Setup
    mock_session_instance = MagicMock()
    mock_session_local.return_value = mock_session_instance
    
    # Mock return value
    mock_get_strategies.return_value = ["in-app", "email", "sms"]
    
    # Execute
    result = EnhancedNotificationService.get_available_channels()
    
    # Assert
    assert result == ["in-app", "email", "sms"]
    mock_get_strategies.assert_called_once()
    mock_session_instance.close.assert_called_once()


@patch.object(NotificationContext, 'set_strategy')
@patch.object(NotificationContext, 'send_notification')
def test_send_notification_to_admin(mock_send, mock_set, mock_db_session):
    """Test sending a notification to admin"""
    # Setup
    message = "Test admin notification"
    channel = "email"
    
    # Mock admin query
    mock_admin = MagicMock()
    mock_admin.id = 5
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_admin
    
    # Mock return value
    mock_send.return_value = True
    
    # Execute
    result = EnhancedNotificationService.send_notification_to_admin(
        mock_db_session, message, channel
    )
    
    # Assert
    assert result is True
    mock_set.assert_called_once_with(channel)
    mock_send.assert_called_once_with(5, message)
    mock_db_session.query.assert_called_once()


@patch.object(NotificationContext, 'set_strategy')
@patch.object(NotificationContext, 'send_notification')
def test_send_notification_to_admin_no_admin(mock_send, mock_set, mock_db_session):
    """Test sending a notification when no admin is found"""
    # Setup
    message = "Test admin notification"
    
    # Mock admin query returns None
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Execute
    result = EnhancedNotificationService.send_notification_to_admin(
        mock_db_session, message
    )
    
    # Assert
    assert result is False
    mock_set.assert_not_called()
    mock_send.assert_not_called()
    mock_db_session.query.assert_called_once() 