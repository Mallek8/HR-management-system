import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.employee import Employee
from app.models.leave import Leave

client = TestClient(app)

# Test dashboard_supervisor endpoint (HTML page)
def test_dashboard_supervisor_html():
    """Test the dashboard_supervisor HTML endpoint with authentication bypass."""
    # Mock the templates.TemplateResponse
    with patch('app.main.templates.TemplateResponse') as mock_template_response:
        # Create a proper mock response for HTML
        html_content = "<html><body>Dashboard</body></html>"
        mock_template_response.return_value = html_content
        
        # Send a request
        response = client.get("/dashboard_supervisor")
        
        # Verify the response was successful
        assert response.status_code == 200

# Test API dashboard_supervisor endpoint 
@pytest.mark.asyncio
async def test_dashboard_supervisor_api():
    """Test the dashboard_supervisor API directly by calling the view function."""
    from app.api.dashboard_supervisor import dashboard_supervisor
    
    # Mock the request, db, and services
    request = MagicMock()
    request.cookies = {"user_email": "supervisor@example.com"}
    
    db = MagicMock()
    
    # Setup user mock
    mock_user = MagicMock(spec=Employee)
    mock_user.id = 1
    mock_user.name = "Supervisor"
    mock_user.email = "supervisor@example.com"
    mock_user.role = "supervisor"
    db.query().filter().first.return_value = mock_user
    
    # Setup service mocks
    with patch('app.api.dashboard_supervisor.LeaveService') as mock_leave_service:
        mock_leave_service.get_notifications.return_value = [
            {"id": 1, "message": "Test notification", "created_at": "2023-01-01"}
        ]
        mock_leave_service.get_leave_requests_for_supervisor.return_value = [
            {"id": 1, "employee_name": "Employee 1", "start_date": "2023-01-02", "end_date": "2023-01-03", "status": "en attente"}
        ]
        mock_leave_service.get_employees_on_leave.return_value = [
            {"id": 2, "name": "Employee 2", "start_date": "2023-01-04", "end_date": "2023-01-05"}
        ]
        
        # Setup template response mock
        with patch('app.api.dashboard_supervisor.templates.TemplateResponse') as mock_template_response:
            # Call the async function with await
            response = await dashboard_supervisor(request, db)
            
            # Verify the template was called with correct data
            mock_template_response.assert_called_once()
            
            # Check first positional argument (template name)
            assert mock_template_response.call_args[0][0] == "dashboard_supervisor.html"
            
            # Check context dictionary (second positional argument)
            context = mock_template_response.call_args[0][1]  # This is the context dict
            assert context["request"] == request
            assert context["user"] == mock_user
            assert context["notifications"] == mock_leave_service.get_notifications.return_value
            assert context["leave_requests"] == mock_leave_service.get_leave_requests_for_supervisor.return_value
            assert context["employees_on_leave"] == mock_leave_service.get_employees_on_leave.return_value

@pytest.mark.asyncio
async def test_dashboard_supervisor_no_cookie():
    """Test the dashboard_supervisor endpoint without a user cookie."""
    from app.api.dashboard_supervisor import dashboard_supervisor
    from fastapi import HTTPException
    
    # Mock request with no cookies
    request = MagicMock()
    request.cookies = {}
    
    db = MagicMock()
    
    # The function should raise an HTTPException
    with pytest.raises(HTTPException) as excinfo:
        await dashboard_supervisor(request, db)
    
    # Verify the exception
    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Access denied"

@pytest.mark.asyncio
async def test_dashboard_supervisor_user_not_found():
    """Test the dashboard_supervisor endpoint with a cookie but no matching user."""
    from app.api.dashboard_supervisor import dashboard_supervisor
    from fastapi import HTTPException
    
    # Mock request with a cookie
    request = MagicMock()
    request.cookies = {"user_email": "nonexistent@example.com"}
    
    # Setup DB to return None for the user
    db = MagicMock()
    db.query().filter().first.return_value = None
    
    # The function should raise an HTTPException
    with pytest.raises(HTTPException) as excinfo:
        await dashboard_supervisor(request, db)
    
    # Verify the exception
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "User not found"

@pytest.mark.asyncio
async def test_dashboard_supervisor_exception_handling():
    """Test error handling in dashboard_supervisor endpoint."""
    from app.api.dashboard_supervisor import dashboard_supervisor
    from fastapi import HTTPException
    
    # Mock request with a cookie
    request = MagicMock()
    request.cookies = {"user_email": "supervisor@example.com"}
    
    # Setup user mock
    db = MagicMock()
    mock_user = MagicMock(spec=Employee)
    db.query().filter().first.return_value = mock_user
    
    # Set up LeaveService to raise an exception
    with patch('app.api.dashboard_supervisor.LeaveService') as mock_leave_service:
        mock_leave_service.get_notifications.side_effect = Exception("Database error")
        
        # The function should raise an HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await dashboard_supervisor(request, db)
        
        # Verify the exception
        assert excinfo.value.status_code == 500
        assert "Internal server error" in excinfo.value.detail 