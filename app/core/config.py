"""
config.py - Configuration de l'application

Responsabilités :
- Centraliser les paramètres de configuration
- Charger les variables d'environnement
- Définir les constantes de l'application
"""

from pydantic_settings import BaseSettings
from datetime import timedelta

class Settings(BaseSettings):
    """Configuration de l'application."""
    
    # Authentification
    # IMPORTANT: Utilisez une variable d'environnement SECRET_KEY en production
    SECRET_KEY: str = "dev-secret-key-change-in-production-via-env-var"  # Valeur par défaut pour développement
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 jours
    
    # Base de données
    # IMPORTANT: Configurez DATABASE_URL via variable d'environnement ou fichier .env
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/database_name"
    
    # Serveur
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # Email
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "user@example.com"
    SMTP_PASSWORD: str = "password"
    
    # Tokens
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48
    
    # Divers
    LOGS_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instance globale
settings = Settings() 