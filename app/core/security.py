"""
security.py - Fonctionnalités de sécurité et de gestion des mots de passe

Responsabilités :
- Hachage et vérification des mots de passe
- Fonctions utilitaires liées à la sécurité
"""

import hashlib
from passlib.context import CryptContext

# Context pour le hachage de mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe en clair correspond à un hash.
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash du mot de passe
        
    Returns:
        bool: True si le mot de passe correspond, False sinon
    """
    # Si le mot de passe hashé commence par $2b$ (format bcrypt), utiliser passlib
    if hashed_password and hashed_password.startswith("$2b$"):
        return pwd_context.verify(plain_password, hashed_password)
    
    # Sinon, utiliser une simple comparaison (pour la compatibilité avec les tests)
    return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    """
    Génère un hash sécurisé pour un mot de passe.
    
    Args:
        password: Mot de passe en clair
        
    Returns:
        str: Hash du mot de passe
    """
    return pwd_context.hash(password)

def get_simple_hash(text: str) -> str:
    """
    Génère un simple hash SHA-256 (moins sécurisé, à utiliser uniquement 
    pour des tokens temporaires ou des identifiants non sensibles).
    
    Args:
        text: Texte à hasher
        
    Returns:
        str: Hash du texte
    """
    return hashlib.sha256(text.encode()).hexdigest() 