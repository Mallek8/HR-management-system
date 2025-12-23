import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models.employee import Employee

# Base de données SQLite pour les tests
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Fixture qui crée une session de base de données pour les tests"""
    Base.metadata.create_all(bind=engine)  # Création des tables
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)  # Supprime les tables après chaque test
