import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.strategies.notifications.notification_context import NotificationContext
from app.strategies.notifications.notification_strategy import (
    NotificationStrategy,
    InAppNotificationStrategy,
    EmailNotificationStrategy,
    SMSNotificationStrategy
)


@pytest.fixture
def mock_db_session():
    """Fixture for mocked database session"""
    mock_session = MagicMock(spec=Session)
    return mock_session


def test_notification_context_initialization(mock_db_session):
    """Test initializing the notification context"""
    context = NotificationContext(mock_db_session)
    
    # By default, the context should use InAppNotificationStrategy
    assert isinstance(context._current_strategy, InAppNotificationStrategy)
    assert context.db == mock_db_session


def test_notification_context_set_strategy(mock_db_session):
    """Test setting different strategies"""
    context = NotificationContext(mock_db_session)
    
    # Test setting each strategy type
    context.set_strategy("in-app")
    assert isinstance(context._current_strategy, InAppNotificationStrategy)
    
    context.set_strategy("email")
    assert isinstance(context._current_strategy, EmailNotificationStrategy)
    
    context.set_strategy("sms")
    assert isinstance(context._current_strategy, SMSNotificationStrategy)


def test_notification_context_set_strategy_invalid(mock_db_session):
    """Test setting an invalid strategy"""
    context = NotificationContext(mock_db_session)
    
    # Should fallback to default strategy (in-app) if invalid strategy is provided
    context.set_strategy("invalid-channel")
    assert isinstance(context._current_strategy, InAppNotificationStrategy)


@patch.object(InAppNotificationStrategy, 'send')
def test_notification_context_send_notification(mock_send, mock_db_session):
    """Test sending notification through context"""
    # Setup
    context = NotificationContext(mock_db_session)
    employee_id = 1
    message = "Test notification"
    
    # Mock return value
    mock_send.return_value = True
    
    # Execute
    result = context.send_notification(employee_id, message)
    
    # Assert
    assert result is True
    mock_send.assert_called_once_with(employee_id, message)


def test_notification_context_get_available_strategies(mock_db_session):
    """Test getting available strategies"""
    context = NotificationContext(mock_db_session)
    strategies = context.get_available_strategies()
    
    # Assert we get the expected strategies
    assert "in-app" in strategies
    assert "email" in strategies
    assert "sms" in strategies
    assert len(strategies) == 3


@patch.object(InAppNotificationStrategy, 'send')
@patch.object(EmailNotificationStrategy, 'send')
@patch.object(SMSNotificationStrategy, 'send')
def test_notification_context_send_multi_channel(
    mock_sms_send, mock_email_send, mock_inapp_send, mock_db_session
):
    """Test sending through multiple channels"""
    # Setup
    context = NotificationContext(mock_db_session)
    employee_id = 1
    message = "Test notification"
    channels = ["in-app", "email"]
    
    # Mock return values
    mock_inapp_send.return_value = True
    mock_email_send.return_value = True
    mock_sms_send.return_value = False
    
    # Execute
    result = context.send_multi_channel(employee_id, message, channels)
    
    # Assert
    assert "in-app" in result and result["in-app"] is True
    assert "email" in result and result["email"] is True
    
    # SMS should not have been called since it's not in the channels list
    mock_inapp_send.assert_called_once_with(employee_id, message)
    mock_email_send.assert_called_once_with(employee_id, message)
    mock_sms_send.assert_not_called()


@patch.object(InAppNotificationStrategy, 'send')
@patch.object(EmailNotificationStrategy, 'send')
@patch.object(SMSNotificationStrategy, 'send')
def test_notification_context_send_multi_channel_all(
    mock_sms_send, mock_email_send, mock_inapp_send, mock_db_session
):
    """Test sending through all channels (None specified)"""
    # Setup
    context = NotificationContext(mock_db_session)
    employee_id = 1
    message = "Test notification"
    
    # Mock return values
    mock_inapp_send.return_value = True
    mock_email_send.return_value = True
    mock_sms_send.return_value = False
    
    # Execute
    result = context.send_multi_channel(employee_id, message, None)
    
    # Assert
    assert "in-app" in result and result["in-app"] is True
    assert "email" in result and result["email"] is True
    assert "sms" in result and result["sms"] is False
    
    # All strategies should have been called
    mock_inapp_send.assert_called_once_with(employee_id, message)
    mock_email_send.assert_called_once_with(employee_id, message)
    mock_sms_send.assert_called_once_with(employee_id, message)


# Tests for strategy implementations

@patch('app.services.notification_service.NotificationService.send_notification')
def test_inapp_notification_strategy_send(mock_send, mock_db_session):
    """Test sending using in-app strategy"""
    # Setup
    strategy = InAppNotificationStrategy(mock_db_session)
    employee_id = 1
    message = "Test notification"
    
    # Mock return values
    mock_notification = MagicMock()
    mock_send.return_value = mock_notification
    
    # Execute
    result = strategy.send(employee_id, message)
    
    # Assert
    assert result is True
    mock_send.assert_called_once_with(mock_db_session, employee_id, message)


@patch('app.services.notification_service.NotificationService.send_notification')
def test_inapp_notification_strategy_send_error(mock_send, mock_db_session):
    """Test sending using in-app strategy with error"""
    # Setup
    strategy = InAppNotificationStrategy(mock_db_session)
    employee_id = 1
    message = "Test notification"
    
    # Mock return values to simulate failure
    mock_send.side_effect = Exception("Error")
    
    # Execute
    result = strategy.send(employee_id, message)
    
    # Assert
    assert result is False
    mock_send.assert_called_once()


@patch('logging.info')
def test_email_notification_strategy_send(mock_log, mock_db_session):
    """Test sending using email strategy"""
    # Setup
    strategy = EmailNotificationStrategy()
    employee_id = 1
    message = "Test notification"
    
    # Execute
    result = strategy.send(employee_id, message)
    
    # Assert - this is a simulation so it should always succeed
    assert result is True


@patch('logging.info')
def test_sms_notification_strategy_send(mock_log, mock_db_session):
    """Test sending using SMS strategy"""
    # Setup
    strategy = SMSNotificationStrategy()
    employee_id = 1
    message = "Test notification"
    
    # Execute
    result = strategy.send(employee_id, message)
    
    # Assert - this is a simulation so it should always succeed
    assert result is True


class TestNotificationStrategyBase(NotificationStrategy):
    """Test implementation of NotificationStrategy for abstract method testing"""
    def send(self, recipient_id, message, **kwargs):
        pass
    
    def get_channel_name(self):
        pass

def test_notification_strategy_abstract_send():
    """Test the abstract send method"""
    strategy = TestNotificationStrategyBase()
    # This should not raise NotImplementedError now because we've implemented the methods
    assert strategy is not None 