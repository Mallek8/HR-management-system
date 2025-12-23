"""
Module de configuration de la base de données PostgreSQL avec SQLAlchemy.

Responsabilités :
- Définir l'URL de connexion à la base de données
- Initialiser l'engine SQLAlchemy avec psycopg (v3)
- Fournir une session de base de données (SessionLocal)
- Fournir une fonction génératrice `get_db()` pour injecter les sessions dans les endpoints FastAPI

Design Pattern :
- Factory Pattern : pour créer dynamiquement des sessions DB via `sessionmaker`

Note: This module uses psycopg (v3) instead of psycopg2 for better UTF-8 handling
and Python 3.13 compatibility. psycopg v3 has native UTF-8 support and doesn't
require special encoding handling.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
import logging
from typing import Generator
from urllib.parse import quote_plus, urlparse, urlunparse
from app.core.config import settings

# Configuration du logger
logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """
    Construit l'URL de connexion à la base de données avec le driver psycopg (v3).
    
    Returns:
        PostgreSQL connection URL using postgresql+psycopg:// scheme
        
    The URL is automatically converted to use psycopg (v3) driver if it's
    using postgresql:// or postgresql+psycopg2:// scheme.
    """
    db_url = settings.DATABASE_URL
    
    # Parse and rebuild URL with proper encoding and psycopg driver
    if db_url.startswith("postgresql://") or db_url.startswith("postgresql+psycopg2://"):
        try:
            parsed = urlparse(db_url)
            
            # URL-encode username and password to handle special characters
            username = quote_plus(parsed.username or "")
            password = quote_plus(parsed.password or "")
            
            # Rebuild URL with encoded credentials and psycopg driver
            netloc = f"{username}:{password}@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            
            # Use postgresql+psycopg:// scheme for psycopg v3
            encoded_url = urlunparse((
                "postgresql+psycopg",  # Use psycopg (v3) driver
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            return encoded_url
        except Exception as e:
            logger.warning(f"Erreur lors de l'encodage de l'URL de base de données: {e}")
            # Fallback: just replace the scheme
            if db_url.startswith("postgresql://"):
                return db_url.replace("postgresql://", "postgresql+psycopg://", 1)
            elif db_url.startswith("postgresql+psycopg2://"):
                return db_url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
            return db_url
    elif db_url.startswith("postgresql+psycopg://"):
        # Already using psycopg, just ensure encoding
        try:
            parsed = urlparse(db_url)
            username = quote_plus(parsed.username or "")
            password = quote_plus(parsed.password or "")
            netloc = f"{username}:{password}@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            encoded_url = urlunparse((
                "postgresql+psycopg",
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            return encoded_url
        except Exception as e:
            logger.warning(f"Erreur lors de l'encodage de l'URL: {e}")
            return db_url
    
    return db_url


# Get database URL
DATABASE_URL = get_database_url()

# Log connection configuration (mask password)
safe_url_for_logging = DATABASE_URL.split('@')[0] + '@***' if '@' in DATABASE_URL else '***'
logger.info(f"Configuration de la connexion à la base de données PostgreSQL (URL: {safe_url_for_logging})...")
logger.info("Utilisation du driver psycopg (v3) pour une meilleure compatibilité UTF-8 et Python 3.13")


# ============================================
# Initialisation de l'engine SQLAlchemy
# ============================================

# Create SQLAlchemy engine with psycopg (v3)
# psycopg v3 has native UTF-8 support and doesn't require special encoding handling
# No custom connection creator needed - SQLAlchemy handles it automatically
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        poolclass=QueuePool,  # Use connection pooling for better performance
        pool_size=5,  # Number of connections to maintain in the pool
        max_overflow=10,  # Maximum overflow connections
        echo=False,  # Set to True for SQL query logging
        future=True,  # Use SQLAlchemy 2.0 style
        # psycopg v3 handles UTF-8 automatically - no connect_args needed
    )
    logger.info("Engine SQLAlchemy créé avec succès (driver: psycopg v3)")
    
except Exception as e:
    logger.error(f"Erreur lors de la création de l'engine SQLAlchemy: {e}")
    logger.warning("L'application continuera sans base de données - certaines fonctionnalités ne seront pas disponibles")
    # Don't raise - let the app start and fail gracefully on first DB access
    engine = None


# ============================================
# Test de connexion (optionnel, non bloquant)
# ============================================

def test_connection() -> bool:
    """
    Teste la connexion à la base de données.
    
    Returns:
        True si la connexion réussit, False sinon
        
    Cette fonction ne bloque pas le démarrage de l'application si la connexion échoue.
    """
    if engine is None:
        logger.warning("Engine SQLAlchemy non initialisé - la base de données n'est pas disponible")
        return False
        
    try:
        with engine.connect() as conn:
            # Execute a simple query to verify connection
            # In SQLAlchemy 2.0, we need to use text() for raw SQL
            result = conn.execute(text("SELECT 1"))
            # For SELECT queries, no commit needed - just fetch the result
            result.fetchone()
            logger.info("Connexion à la base de données établie avec succès (psycopg v3).")
            return True
    except Exception as e:
        logger.error(f"Erreur lors de la connexion à la base de données: {str(e)}")
        return False


# ============================================
# Création d'une session de base de données
# ============================================

# Base utilisée pour déclarer les modèles ORM
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Create session factory (only if engine is available)
if engine is not None:
    try:
        # SQLAlchemy 2.0 style
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            future=True  # SQLAlchemy 2.0 style (deprecated in 2.0 but works)
        )
        logger.info("SessionLocal créé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la création de SessionLocal: {e}")
        SessionLocal = None
else:
    # Create a dummy session maker that will fail gracefully
    SessionLocal = None
    logger.warning("SessionLocal non initialisé - la base de données n'est pas disponible")


# ============================================
# Fournisseur de sessions pour FastAPI
# ============================================

def get_db() -> Generator:
    """
    Fonction qui retourne une session de base de données active.
    Utilisée par FastAPI pour l'injection de dépendance.
    
    Yields:
        Session: Une session SQLAlchemy active.
        
    Raises:
        RuntimeError: Si la base de données n'est pas disponible
    """
    if SessionLocal is None:
        raise RuntimeError("Base de données non disponible. Veuillez vérifier la configuration.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
