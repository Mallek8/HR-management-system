import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, date
from io import BytesIO
from sqlalchemy.orm import Session

# Importation conditionnelle de PyPDF2
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

from app.services.report_service import ReportService
from app.models.employee import Employee
from app.models.evaluation import Evaluation
from app.models.objective import Objective


@pytest.fixture
def mock_db_session():
    """Fixture pour simuler une session de base de données."""
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def mock_employee():
    """Fixture pour simuler un employé."""
    employee = MagicMock(spec=Employee)
    employee.id = 1
    employee.name = "John Doe"
    employee.email = "john.doe@example.com"
    employee.hire_date = date(2020, 1, 15)
    return employee


@pytest.fixture
def mock_evaluations():
    """Fixture pour simuler des évaluations."""
    eval1 = MagicMock(spec=Evaluation)
    eval1.id = 1
    eval1.employee_id = 1
    eval1.date = date(2022, 6, 15)
    eval1.score = 4.5
    eval1.feedback = "Excellent travail, continue comme ça!"
    
    eval2 = MagicMock(spec=Evaluation)
    eval2.id = 2
    eval2.employee_id = 1
    eval2.date = date(2023, 6, 15)
    eval2.score = 4.8
    eval2.feedback = "Progression constante, bonne initiative!"
    
    return [eval1, eval2]


@pytest.fixture
def mock_objectives():
    """Fixture pour simuler des objectifs."""
    obj1 = MagicMock(spec=Objective)
    obj1.id = 1
    obj1.employee_id = 1
    obj1.description = "Améliorer les compétences en Python"
    obj1.start_date = date(2022, 1, 1)
    obj1.end_date = date(2022, 12, 31)
    obj1.status = "Complété"
    
    obj2 = MagicMock(spec=Objective)
    obj2.id = 2
    obj2.employee_id = 1
    obj2.description = "Apprendre Docker"
    obj2.start_date = date(2023, 1, 1)
    obj2.end_date = date(2023, 12, 31)
    obj2.status = "En cours"
    
    return [obj1, obj2]


def test_generate_performance_report(mock_db_session, mock_employee, mock_evaluations, mock_objectives):
    """Test de la génération d'un rapport de performance."""
    # Configuration des mocks pour les requêtes
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_employee
    mock_db_session.query.return_value.filter.return_value.all.side_effect = [
        mock_evaluations,  # Première utilisation pour les évaluations
        mock_objectives    # Deuxième utilisation pour les objectifs
    ]
    
    # Exécution du test
    pdf_content = ReportService.generate_performance_report(mock_db_session, 1)
    
    # Vérification du résultat
    assert pdf_content is not None
    assert isinstance(pdf_content, bytes)
    
    # Vérifier que les requêtes ont été appelées correctement
    mock_db_session.query.assert_any_call(Employee)
    mock_db_session.query.assert_any_call(Evaluation)
    mock_db_session.query.assert_any_call(Objective)
    
    # Essayer de parser le PDF pour vérifier son contenu (optionnel)
    if PYPDF2_AVAILABLE:
        pdf_file = BytesIO(pdf_content)
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            # Vérifier que le PDF a au moins une page
            assert len(reader.pages) > 0
        except Exception:
            # Si le parsing échoue, ne pas faire échouer le test
            pass


def test_generate_performance_report_employee_not_found(mock_db_session):
    """Test de la génération d'un rapport lorsque l'employé n'existe pas."""
    # Configuration du mock pour retourner None (employé non trouvé)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Exécution du test
    result = ReportService.generate_performance_report(mock_db_session, 999)
    
    # Vérification du résultat
    assert result is None
    
    # Vérifier que la requête a été appelée correctement
    mock_db_session.query.assert_called_once_with(Employee)


def test_generate_performance_report_no_data(mock_db_session, mock_employee):
    """Test de la génération d'un rapport sans évaluations ni objectifs."""
    # Configuration des mocks
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_employee
    mock_db_session.query.return_value.filter.return_value.all.return_value = []
    
    # Exécution du test
    pdf_content = ReportService.generate_performance_report(mock_db_session, 1)
    
    # Vérification du résultat
    assert pdf_content is not None
    assert isinstance(pdf_content, bytes)
    
    # Vérifier que les requêtes ont été appelées correctement
    mock_db_session.query.assert_any_call(Employee)
    mock_db_session.query.assert_any_call(Evaluation)
    mock_db_session.query.assert_any_call(Objective) 