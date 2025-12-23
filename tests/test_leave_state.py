import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session

from app.models.leave import Leave
from app.models.employee import Employee
from app.states.leave_request.pending_state import PendingState
from app.states.leave_request.approved_state import ApprovedState
from app.states.leave_request.rejected_state import RejectedState
from app.states.leave_request.cancelled_state import CancelledState
from app.states.leave_request.leave_context import LeaveContext

# =============================
# Test PendingState
# =============================

def test_pending_state_can_approve():
    """Test that PendingState.can_approve returns True."""
    state = PendingState()
    assert state.can_approve() is True

def test_pending_state_can_reject():
    """Test that PendingState.can_reject returns True."""
    state = PendingState()
    assert state.can_reject() is True

def test_pending_state_can_cancel():
    """Test that PendingState.can_cancel returns True."""
    state = PendingState()
    assert state.can_cancel() is True

def test_pending_state_approve():
    """Test PendingState.approve method successfully changes state to ApprovedState."""
    # Setup
    state = PendingState()
    leave = MagicMock(spec=Leave)
    leave.employee_id = 1
    leave.start_date = datetime.now(UTC)
    leave.end_date = datetime.now(UTC) + timedelta(days=1)
    
    context = MagicMock(spec=LeaveContext)
    context.get_request.return_value = leave
    
    db = MagicMock(spec=Session)
    
    # Create a patch for EnhancedNotificationService
    with patch('app.states.leave_request.pending_state.EnhancedNotificationService') as mock_notification:
        # Act
        result = state.approve(context, db, 2, "Approved")
        
        # Assert
        assert result["success"] is True
        assert "Demande approuvée avec succès" in result["message"]
        assert leave.status == "approuvé"
        assert leave.approved_by == 2
        assert leave.supervisor_comment == "Approved"
        context.change_state.assert_called_once()
        assert isinstance(context.change_state.call_args[0][0], ApprovedState)
        db.commit.assert_called_once()
        mock_notification.send_multi_channel_notification.assert_called_once()

def test_pending_state_reject():
    """Test PendingState.reject method successfully changes state to RejectedState."""
    # Setup
    state = PendingState()
    leave = MagicMock(spec=Leave)
    leave.employee_id = 1
    leave.start_date = datetime.now(UTC)
    leave.end_date = datetime.now(UTC) + timedelta(days=1)
    
    context = MagicMock(spec=LeaveContext)
    context.get_request.return_value = leave
    
    db = MagicMock(spec=Session)
    
    # Create a patch for EnhancedNotificationService
    with patch('app.states.leave_request.pending_state.EnhancedNotificationService') as mock_notification:
        # Act
        result = state.reject(context, db, 2, "Rejected for valid reason")
        
        # Assert
        assert result["success"] is True
        assert "Demande rejetée avec succès" in result["message"]
        assert leave.status == "refusé"
        assert leave.rejected_by == 2
        assert leave.rejection_reason == "Rejected for valid reason"
        context.change_state.assert_called_once()
        assert isinstance(context.change_state.call_args[0][0], RejectedState)
        db.commit.assert_called_once()
        mock_notification.send_multi_channel_notification.assert_called_once()

def test_pending_state_cancel():
    """Test PendingState.cancel method successfully changes state to CancelledState."""
    # Setup
    state = PendingState()
    leave = MagicMock(spec=Leave)
    leave.employee_id = 1
    leave.start_date = datetime.now(UTC)
    leave.end_date = datetime.now(UTC) + timedelta(days=1)
    
    context = MagicMock(spec=LeaveContext)
    context.get_request.return_value = leave
    
    db = MagicMock(spec=Session)
    
    # Create a patch for EnhancedNotificationService
    with patch('app.states.leave_request.pending_state.EnhancedNotificationService') as mock_notification:
        # Act
        result = state.cancel(context, db, 1, "Cancelled by employee")
        
        # Assert
        assert result["success"] is True
        assert "Demande annulée avec succès" in result["message"]
        assert leave.status == "annulé"
        assert leave.cancelled_by == 1
        assert leave.cancellation_reason == "Cancelled by employee"
        context.change_state.assert_called_once()
        assert isinstance(context.change_state.call_args[0][0], CancelledState)
        db.commit.assert_called_once()
        mock_notification.send_notification.assert_not_called()  # Employee cancelling their own request

def test_pending_state_cancel_by_other():
    """Test PendingState.cancel method when cancelled by someone other than employee."""
    # Setup
    state = PendingState()
    employee = MagicMock(spec=Employee)
    employee.name = "John Doe"
    
    leave = MagicMock(spec=Leave)
    leave.employee_id = 1
    leave.employee = employee
    leave.start_date = datetime.now(UTC)
    leave.end_date = datetime.now(UTC) + timedelta(days=1)
    
    context = MagicMock(spec=LeaveContext)
    context.get_request.return_value = leave
    
    db = MagicMock(spec=Session)
    
    # Create a patch for EnhancedNotificationService
    with patch('app.states.leave_request.pending_state.EnhancedNotificationService') as mock_notification:
        # Act
        result = state.cancel(context, db, 2, "Cancelled by supervisor")
        
        # Assert
        assert result["success"] is True
        assert "Demande annulée avec succès" in result["message"]
        assert leave.status == "annulé"
        assert leave.cancelled_by == 2
        assert leave.cancellation_reason == "Cancelled by supervisor"
        context.change_state.assert_called_once()
        assert isinstance(context.change_state.call_args[0][0], CancelledState)
        db.commit.assert_called_once()
        mock_notification.send_notification.assert_called_once()  # Notification should be sent to employee

def test_pending_state_submit():
    """Test PendingState.submit method does nothing as request is already submitted."""
    # Setup
    state = PendingState()
    context = MagicMock()
    db = MagicMock()
    
    # Act
    result = state.submit(context, db)
    
    # Assert - PendingState.submit returns False because the request is already submitted
    assert result is False

def test_pending_state_exception_handling_approve():
    """Test exception handling in the approve method."""
    # Setup
    state = PendingState()
    leave = MagicMock(spec=Leave)
    
    context = MagicMock(spec=LeaveContext)
    context.get_request.return_value = leave
    
    db = MagicMock(spec=Session)
    db.commit.side_effect = Exception("Database error")
    
    # Act
    result = state.approve(context, db, 2)
    
    # Assert
    assert result["success"] is False
    assert "Erreur lors de l'approbation" in result["message"]
    db.rollback.assert_called_once()

def test_pending_state_exception_handling_reject():
    """Test exception handling in the reject method."""
    # Setup
    state = PendingState()
    leave = MagicMock(spec=Leave)
    
    context = MagicMock(spec=LeaveContext)
    context.get_request.return_value = leave
    
    db = MagicMock(spec=Session)
    db.commit.side_effect = Exception("Database error")
    
    # Act
    result = state.reject(context, db, 2)
    
    # Assert
    assert result["success"] is False
    assert "Erreur lors du rejet" in result["message"]
    db.rollback.assert_called_once()

def test_pending_state_exception_handling_cancel():
    """Test exception handling in the cancel method."""
    # Setup
    state = PendingState()
    leave = MagicMock(spec=Leave)
    
    context = MagicMock(spec=LeaveContext)
    context.get_request.return_value = leave
    
    db = MagicMock(spec=Session)
    db.commit.side_effect = Exception("Database error")
    
    # Act
    result = state.cancel(context, db, 2)
    
    # Assert
    assert result["success"] is False
    assert "Erreur lors de l'annulation" in result["message"]
    db.rollback.assert_called_once()

def test_pending_state_get_allowed_transitions():
    """Test that PendingState.get_allowed_transitions returns the correct transitions."""
    state = PendingState()
    transitions = state.get_allowed_transitions()
    
    assert transitions == {
        "approve": "approuvé",
        "reject": "refusé",
        "cancel": "annulé"
    }

def test_pending_state_get_state_name():
    """Test that PendingState.get_state_name returns 'en attente'."""
    state = PendingState()
    assert state.get_state_name() == "en attente"

# =============================
# Test ApprovedState
# =============================

def test_approved_state_can_operations():
    """Test various can_* operations on ApprovedState."""
    from app.states.leave_request.approved_state import ApprovedState
    
    state = ApprovedState()
    # In approved state, we can't approve again, reject, or submit
    assert state.can_approve() is False
    assert state.can_reject() is False
    assert state.can_submit() is False
    # But we can cancel an approved request
    assert state.can_cancel() is True

def test_approved_state_approve():
    """Test that approve operation fails in ApprovedState."""
    from app.states.leave_request.approved_state import ApprovedState
    
    state = ApprovedState()
    context = MagicMock()
    db = MagicMock()
    
    result = state.approve(context, db, 1)
    
    assert result["success"] is False
    assert "ne peut pas être approuvée" in result["message"]
    # Ensure state didn't change
    context.change_state.assert_not_called()
    
def test_approved_state_reject():
    """Test that reject operation fails in ApprovedState."""
    from app.states.leave_request.approved_state import ApprovedState
    
    state = ApprovedState()
    context = MagicMock()
    db = MagicMock()
    
    result = state.reject(context, db, 1)
    
    assert result["success"] is False
    assert "ne peut pas être rejetée" in result["message"]
    # Ensure state didn't change
    context.change_state.assert_not_called()
    
def test_approved_state_cancel():
    """Test cancel operation in ApprovedState."""
    from app.states.leave_request.approved_state import ApprovedState
    
    state = ApprovedState()
    leave = MagicMock(spec=Leave)
    leave.employee_id = 1
    leave.start_date = datetime.now(UTC)
    leave.end_date = datetime.now(UTC) + timedelta(days=1)
    
    context = MagicMock(spec=LeaveContext)
    context.get_request.return_value = leave
    
    db = MagicMock(spec=Session)
    
    # Create a patch for EnhancedNotificationService
    with patch('app.states.leave_request.approved_state.EnhancedNotificationService') as mock_notification:
        result = state.cancel(context, db, 2, "Cancelled after approval")
        
        # Verify result
        assert result["success"] is True
        assert "Demande annulée avec succès" in result["message"]
        
        # Verify leave request was updated
        assert leave.status == "annulé"
        assert leave.cancelled_by == 2
        assert leave.cancellation_reason == "Cancelled after approval"
        
        # Verify state change
        context.change_state.assert_called_once()
        assert isinstance(context.change_state.call_args[0][0], CancelledState)
        
        # Verify notification
        mock_notification.send_notification.assert_called_once()
        
def test_approved_state_cancel_exception():
    """Test exception handling in cancel operation in ApprovedState."""
    from app.states.leave_request.approved_state import ApprovedState
    
    state = ApprovedState()
    leave = MagicMock(spec=Leave)
    
    context = MagicMock(spec=LeaveContext)
    context.get_request.return_value = leave
    
    db = MagicMock(spec=Session)
    db.commit.side_effect = Exception("Database error")
    
    result = state.cancel(context, db, 2)
    
    # Verify result
    assert result["success"] is False
    assert "Erreur lors de l'annulation" in result["message"]
    
    # Verify rollback was called
    db.rollback.assert_called_once()
    
def test_approved_state_submit():
    """Test that submit operation fails in ApprovedState."""
    from app.states.leave_request.approved_state import ApprovedState
    
    state = ApprovedState()
    context = MagicMock()
    db = MagicMock()
    
    result = state.submit(context, db)
    
    assert result["success"] is False
    assert "ne peut pas être soumise à nouveau" in result["message"]
    
def test_approved_state_get_allowed_transitions():
    """Test that ApprovedState.get_allowed_transitions returns the correct transitions."""
    from app.states.leave_request.approved_state import ApprovedState
    
    state = ApprovedState()
    transitions = state.get_allowed_transitions()
    
    assert transitions == {"cancel": "annulé"}
    
def test_approved_state_get_state_name():
    """Test that ApprovedState.get_state_name returns 'approuvé'."""
    from app.states.leave_request.approved_state import ApprovedState
    
    state = ApprovedState()
    assert state.get_state_name() == "approuvé" 