import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.dashboard_controller import DashboardController
from app.services.employee_service import EmployeeService
from app.models.employee import Employee

class TestDashboardController:
    
    def setup_method(self):
        """Configuration initiale avant chaque test"""
        self.mock_db = MagicMock(spec=Session)
        self.mock_employee = Employee(
            id=1,
            name="John Doe",
            email="john.doe@example.com",
            password="password123",
            role="employee",
            status=True
        )
    
    @patch('app.services.employee_service.EmployeeService.get_employee_by_email')
    def test_get_employee_dashboard_success(self, mock_get_employee):
        """Test le cas où l'employé est trouvé avec succès"""
        # Arrangement
        email = "john.doe@example.com"
        mock_get_employee.return_value = self.mock_employee
        
        # Action
        result = DashboardController.get_employee_dashboard(self.mock_db, email)
        
        # Assertion
        assert result is not None
        assert result.id == 1
        assert result.name == "John Doe"
        assert result.email == email
        mock_get_employee.assert_called_once_with(self.mock_db, email)
    
    @patch('app.services.employee_service.EmployeeService.get_employee_by_email')
    def test_get_employee_dashboard_not_found(self, mock_get_employee):
        """Test le cas où l'employé n'est pas trouvé"""
        # Arrangement
        email = "nonexistent@example.com"
        mock_get_employee.return_value = None
        
        # Action & Assertion
        with pytest.raises(HTTPException) as exc_info:
            DashboardController.get_employee_dashboard(self.mock_db, email)
        
        # Vérifier que l'exception a le bon statut et message
        assert exc_info.value.status_code == 404
        assert "Utilisateur introuvable" in exc_info.value.detail
        mock_get_employee.assert_called_once_with(self.mock_db, email)
    
    @patch('app.services.employee_service.EmployeeService.get_employee_by_email')
    def test_get_employee_dashboard_validation(self, mock_get_employee):
        """Test la validation des paramètres d'entrée"""
        # Arrangement
        email = ""  # Email vide
        mock_get_employee.return_value = None
        
        # Action & Assertion
        with pytest.raises(HTTPException) as exc_info:
            DashboardController.get_employee_dashboard(self.mock_db, email)
        
        # Vérifier que l'exception a le bon statut
        assert exc_info.value.status_code == 404
        mock_get_employee.assert_called_once_with(self.mock_db, email)
    
    @patch('app.services.employee_service.EmployeeService.get_employee_by_email', side_effect=Exception("Database error"))
    def test_get_employee_dashboard_exception(self, mock_get_employee):
        """Test le comportement en cas d'exception dans le service sous-jacent"""
        # Arrangement
        email = "john.doe@example.com"
        
        # Action & Assertion
        with pytest.raises(Exception) as exc_info:
            DashboardController.get_employee_dashboard(self.mock_db, email)
        
        # Vérifier que l'exception est bien propagée
        assert "Database error" in str(exc_info.value)
        mock_get_employee.assert_called_once_with(self.mock_db, email) 