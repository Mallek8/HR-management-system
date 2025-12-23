import pytest
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models.leave import Leave
from app.models.employee import Employee
from app.models.leave_balance import LeaveBalance
from app.models.training_request import TrainingRequest
from app.repositories.leave_repository import LeaveRepository
from datetime import datetime, timedelta

# Configuration de la base de données en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"  # Base de données en mémoire pour les tests

# Créer une session et une base de données pour les tests
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création des tables
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def db_session():
    """Fixture pour obtenir une session de base de données pour les tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture
def create_employee(db_session):
    """Fixture pour créer un employé pour les tests."""
    # Génère un email unique avec un timestamp
    timestamp = int(time.time() * 1000)
    email = f"testemployee{timestamp}@example.com"
    
    employee = Employee(
        name="Test Employee",
        email=email,
        role="employee",
        department="IT",
        password="password123",
        hire_date=datetime.now().date(),
        birth_date=datetime.now().date(),
        status=True,
        supervisor_id=None
    )
    
    # Créer un LeaveBalance pour l'employé
    leave_balance = LeaveBalance(balance=20.0)
    employee.leave_balances = leave_balance
    
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee

def test_create_leave(db_session, create_employee):
    """Test de création d'une demande de congé."""
    leave_data = {
        "employee_id": create_employee.id,
        "start_date": datetime.today() + timedelta(days=1),
        "end_date": datetime.today() + timedelta(days=3),
        "status": "en attente",
        "admin_approved": False
    }
    
    # Correction pour créer l'objet Leave correctement
    leave = Leave(
        employee_id=leave_data["employee_id"],
        start_date=leave_data["start_date"],
        end_date=leave_data["end_date"],
        status=leave_data["status"],
        admin_approved=leave_data["admin_approved"]
    )
    db_session.add(leave)
    db_session.commit()
    db_session.refresh(leave)

    # Vérification que le congé a bien été créé
    assert leave.id is not None
    assert leave.employee_id == create_employee.id
    assert leave.status == "en attente"

def test_get_leave_by_id(db_session, create_employee):
    """Test de récupération d'une demande de congé par son identifiant."""
    leave = Leave(
        employee_id=create_employee.id,
        start_date=datetime.today() + timedelta(days=1),
        end_date=datetime.today() + timedelta(days=3),
        status="en attente",
        admin_approved=False
    )
    db_session.add(leave)
    db_session.commit()
    db_session.refresh(leave)
    
    retrieved_leave = db_session.query(Leave).filter(Leave.id == leave.id).first()
    
    # Vérification que la demande de congé est correctement récupérée
    assert retrieved_leave is not None
    assert retrieved_leave.id == leave.id
    assert retrieved_leave.employee_id == create_employee.id

def test_get_all_leaves(db_session, create_employee):
    """Test de récupération de toutes les demandes de congé."""
    leave = Leave(
        employee_id=create_employee.id,
        start_date=datetime.today() + timedelta(days=1),
        end_date=datetime.today() + timedelta(days=3),
        status="en attente",
        admin_approved=False
    )
    db_session.add(leave)
    db_session.commit()
    
    leave_requests = db_session.query(Leave).all()
    
    # Vérification que la liste des congés n'est pas vide
    assert len(leave_requests) > 0
    assert all(isinstance(leave_req, Leave) for leave_req in leave_requests)

def test_update_leave_status(db_session, create_employee):
    """Test de mise à jour du statut d'une demande de congé."""
    leave = Leave(
        employee_id=create_employee.id,
        start_date=datetime.today() + timedelta(days=1),
        end_date=datetime.today() + timedelta(days=3),
        status="en attente",
        admin_approved=False
    )
    db_session.add(leave)
    db_session.commit()
    db_session.refresh(leave)
    
    # Mise à jour du statut
    leave.status = "approuvé"
    db_session.commit()
    db_session.refresh(leave)
    
    # Vérification que le statut a bien été mis à jour
    assert leave.status == "approuvé"

def test_delete_leave(db_session, create_employee):
    """Test de suppression d'une demande de congé."""
    leave = Leave(
        employee_id=create_employee.id,
        start_date=datetime.today() + timedelta(days=1),
        end_date=datetime.today() + timedelta(days=3),
        status="en attente",
        admin_approved=False
    )
    db_session.add(leave)
    db_session.commit()
    db_session.refresh(leave)
    
    # Suppression du congé
    db_session.delete(leave)
    db_session.commit()
    
    # Vérification que la suppression a bien été effectuée
    deleted_leave = db_session.query(Leave).filter(Leave.id == leave.id).first()
    assert deleted_leave is None

def test_create_test_leave(db_session, create_employee):
    """Test de création d'un congé de test."""
    leave = Leave(
        employee_id=create_employee.id,
        start_date=datetime.today() + timedelta(days=1),
        end_date=datetime.today() + timedelta(days=3),
        status="en attente",
        type="Congé de test pour débogage"
    )
    db_session.add(leave)
    db_session.commit()
    db_session.refresh(leave)
    
    # Vérifier que le congé est correctement créé
    assert leave.id is not None
    assert leave.employee_id == create_employee.id
    assert leave.status == "en attente"
    assert leave.type == "Congé de test pour débogage"
