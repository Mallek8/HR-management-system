# app/dependencies.py

from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get a database session.
    
    This function should be used as a dependency in FastAPI route handlers.
    It yields a database session and ensures it's closed after use.
    
    Raises:
        RuntimeError: If the database is not available (SessionLocal is None)
    """
    if SessionLocal is None:
        raise RuntimeError("Base de données non disponible. Veuillez vérifier la configuration.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
