import pytest
import hashlib
from passlib.context import CryptContext

from app.core.security import verify_password, get_password_hash, get_simple_hash

# Tests pour la fonction verify_password
def test_verify_password_with_bcrypt_hash():
    """Vérifie que la fonction verify_password fonctionne avec un hash bcrypt valide"""
    # Créer un context CryptContext comme celui utilisé dans security.py
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Générer un hash bcrypt pour un mot de passe test
    plain_password = "testpassword123"
    hashed_password = pwd_context.hash(plain_password)
    
    # Vérifier que notre fonction reconnaît le hash et valide le mot de passe
    assert verify_password(plain_password, hashed_password) is True
    
    # Vérifier qu'un mauvais mot de passe est rejeté
    assert verify_password("wrong_password", hashed_password) is False

def test_verify_password_with_plain_comparison():
    """Vérifie que la fonction verify_password fonctionne en comparaison directe (pour les tests)"""
    # Test avec un mot de passe simple (non hashé)
    plain_password = "testpassword123"
    
    # Quand le mot de passe stocké n'est pas hashé, une comparaison directe est faite
    assert verify_password(plain_password, plain_password) is True
    assert verify_password("wrong_password", plain_password) is False

def test_verify_password_with_none_hash():
    """Vérifie que la fonction verify_password gère correctement un hash None"""
    # Si le hash est None, la vérification devrait échouer
    assert verify_password("testpassword123", None) is False

def test_verify_password_with_empty_hash():
    """Vérifie que la fonction verify_password gère correctement un hash vide"""
    # Si le hash est une chaîne vide, la vérification directe est faite
    assert verify_password("", "") is True
    assert verify_password("something", "") is False

# Tests pour la fonction get_password_hash
def test_get_password_hash_generates_bcrypt():
    """Vérifie que get_password_hash génère un hash bcrypt valide"""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    # Vérifier que le hash commence par le préfixe bcrypt
    assert hashed.startswith("$2b$")
    
    # Vérifier que le hash est valide en l'utilisant pour vérifier le mot de passe
    assert verify_password(password, hashed) is True

def test_get_password_hash_different_for_same_password():
    """Vérifie que get_password_hash génère des hash différents pour le même mot de passe"""
    password = "testpassword123"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Les hash doivent être différents même pour le même mot de passe (sel différent)
    assert hash1 != hash2
    
    # Mais les deux hash doivent valider le mot de passe
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True

def test_get_password_hash_with_empty_password():
    """Vérifie que get_password_hash fonctionne avec une chaîne vide"""
    empty_password = ""
    hashed = get_password_hash(empty_password)
    
    # Même une chaîne vide doit produire un hash bcrypt
    assert hashed.startswith("$2b$")
    assert verify_password(empty_password, hashed) is True

# Tests pour la fonction get_simple_hash
def test_get_simple_hash_generates_sha256():
    """Vérifie que get_simple_hash génère un hash SHA-256 correct"""
    text = "test_text"
    hashed = get_simple_hash(text)
    
    # Vérifier que la longueur correspond à un hash SHA-256 (64 caractères)
    assert len(hashed) == 64
    
    # Vérifier que c'est bien un hash SHA-256
    expected_hash = hashlib.sha256(text.encode()).hexdigest()
    assert hashed == expected_hash

def test_get_simple_hash_consistent():
    """Vérifie que get_simple_hash est déterministe (même entrée = même sortie)"""
    text = "test_text"
    hash1 = get_simple_hash(text)
    hash2 = get_simple_hash(text)
    
    # Les hash doivent être identiques pour la même entrée
    assert hash1 == hash2

def test_get_simple_hash_different_inputs():
    """Vérifie que get_simple_hash génère des hash différents pour des entrées différentes"""
    hash1 = get_simple_hash("text1")
    hash2 = get_simple_hash("text2")
    
    # Les hash doivent être différents pour des entrées différentes
    assert hash1 != hash2

def test_get_simple_hash_with_empty_string():
    """Vérifie que get_simple_hash fonctionne avec une chaîne vide"""
    empty_text = ""
    hashed = get_simple_hash(empty_text)
    
    # Vérifier que c'est le bon hash SHA-256 pour une chaîne vide
    expected_hash = hashlib.sha256(empty_text.encode()).hexdigest()
    assert hashed == expected_hash 