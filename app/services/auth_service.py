"""
auth_service.py - Service d'authentification pour l'application RH.

Responsabilités :
- Authentifier et déconnecter les utilisateurs.
- Créer les comptes initiaux (admin et employé de test).
- Gérer les redirections et cookies liés à la session utilisateur.

Design Patterns :
- Singleton (par usage de classmethods)
- Service Layer (encapsulation logique d'authentification)

SOLID :
- SRP : AuthService gère uniquement l'authentification.
- OCP : Les méthodes peuvent être étendues sans être modifiées.
- DIP : Les routes dépendent de cette abstraction métier, pas directement de SQLAlchemy.
"""

from datetime import date, datetime, UTC, timedelta
from fastapi import HTTPException, Request, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.database import get_db
from app.core.config import settings
from typing import Optional, Dict, Any, Union
import logging

templates = Jinja2Templates(directory="frontend/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


def ensure_utf8_string(value: str) -> str:
    """
    Ensure a string is valid UTF-8.
    
    This function sanitizes strings to prevent UnicodeDecodeError when
    passing them to database operations.
    
    Note: With psycopg v3, UTF-8 handling is automatic, but this function
    is kept for safety and backward compatibility.
    
    Args:
        value: Input string (may contain non-UTF-8 bytes)
        
    Returns:
        Valid UTF-8 string with non-UTF-8 bytes replaced safely
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Try to encode as UTF-8 to detect invalid bytes
    try:
        # If it can be encoded, it's valid UTF-8
        value.encode('utf-8')
        return value
    except UnicodeEncodeError:
        # If encoding fails, decode from latin-1 (which can represent any byte)
        # then encode to UTF-8 with error handling
        try:
            return value.encode('latin-1', errors='replace').decode('utf-8', errors='replace')
        except (UnicodeDecodeError, UnicodeEncodeError):
            # Last resort: use ASCII with replacement
            return value.encode('ascii', errors='replace').decode('ascii')


def sanitize_admin_data(admin_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize all admin-related strings to ensure UTF-8 compatibility.
    
    Args:
        admin_data: Dictionary containing admin user data
        
    Returns:
        Dictionary with all string values sanitized to UTF-8
    """
    sanitized = {}
    for key, value in admin_data.items():
        if isinstance(value, str):
            sanitized[key] = ensure_utf8_string(value)
        else:
            sanitized[key] = value
    return sanitized


class AuthService:
    # Utilisateur admin par défaut (utilisé si la base est vide)
    USERS_DB = {
        "admin": {
            "password": "admin123",
            "role": "admin",
            "name": "Administrateur",
            "email": "admin@example.com",
            "hire_date": "2023-01-01",
            "status": True,
        }
    }

    @classmethod
    def render_login_page(cls, request: Request):
        """
        Affiche la page de connexion HTML.
        """
        return templates.TemplateResponse("login.html", {"request": request})

    @classmethod
    def login_user(cls, request: Request, db: Session, username: str, password: str):
        """
        Authentifie un utilisateur et redirige vers son tableau de bord.

        - Si admin : redirection vers dashboard_admin
        - Si employé ou superviseur : redirection adaptée
        """
        # Cas spécial : admin défini dans USERS_DB
        if username == "admin" and cls.USERS_DB["admin"]["password"] == password:
            user = cls.USERS_DB["admin"]
            role = user["role"]
            redirect_url = "/dashboard_admin"

        else:
            # Sanitize username before database query
            username_safe = ensure_utf8_string(username)
            user = db.query(Employee).filter(Employee.email == username_safe).first()
            if not user or user.password != password:
                return templates.TemplateResponse("login.html", {
                    "request": request,
                    "error": "Identifiants invalides"
                })

            is_supervisor = db.query(Employee).filter(Employee.supervisor_id == user.id).count() > 0
            role = user.role
            redirect_url = "/dashboard_supervisor" if is_supervisor else "/dashboard_employee"

        response = RedirectResponse(url=redirect_url, status_code=303)
        response.set_cookie("user_email", username)
        response.set_cookie("user_role", role)
        return response

    @classmethod
    def logout_user(cls):
        """
        Déconnecte l'utilisateur (suppression des cookies).
        """
        response = RedirectResponse(url="/")
        response.delete_cookie("user_email")
        response.delete_cookie("user_role")
        return response

    @classmethod
    def create_default_test_user(cls):
        """
        Crée un employé de test par défaut si inexistant.
        
        This method is fully non-blocking and handles all errors gracefully.
        """
        from app.database import SessionLocal, Base, engine
        
        if engine is None or SessionLocal is None:
            logger.warning("Admin Init: Base de données non disponible - création employé test ignorée")
            return
        
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            logger.warning(f"Admin Init: Erreur lors de la création des tables (ignorée): {e}")
            return
        
        db = None
        try:
            db = SessionLocal()
            
            # Sanitize email before database query
            test_email = ensure_utf8_string("employee1@example.com")
            existing_user = db.query(Employee).filter(Employee.email == test_email).first()
            
            if not existing_user:
                employee = Employee(
                    name=ensure_utf8_string("Employé Test"),
                    email=test_email,
                    role="employee",
                    hire_date=date(2024, 2, 1),
                    status=True,
                    password=ensure_utf8_string("pass123")
                )
                db.add(employee)
                db.commit()
                logger.info("Admin Init: Employé test créé avec succès")
        except Exception as e:
            logger.warning(f"Admin Init: Erreur lors de la création de l'employé test (ignorée): {e}")
            if db:
                try:
                    db.rollback()
                except Exception:
                    pass
        finally:
            if db:
                try:
                    db.close()
                except Exception:
                    pass

    @classmethod
    def ensure_admin_exists(cls):
        """
        Vérifie si l'administrateur existe déjà. Sinon, le crée automatiquement.
        Appelée automatiquement au démarrage (dans app_factory).
        
        Cette fonction est TOTALEMENT NON-BLOQUANTE :
        - Ne bloque jamais le démarrage de l'application
        - Toutes les erreurs sont loggées mais ne sont pas propagées
        - Sanitise tous les strings UTF-8 avant toute opération de base de données
        - Continue même si la base de données est indisponible
        
        Returns:
            bool: True si l'admin a été créé ou existe déjà, False sinon
        """
        from app.database import SessionLocal, Base, engine
        
        # Early return if database is not available - DO NOT CRASH
        if SessionLocal is None or engine is None:
            logger.warning("Admin Init: Base de données non disponible - initialisation admin ignorée")
            logger.info("Admin Init: L'application continuera sans initialiser l'admin")
            return False
        
        # Sanitize admin data BEFORE any database operations
        try:
            admin_data_raw = cls.USERS_DB["admin"]
            admin_data = sanitize_admin_data(admin_data_raw)
            admin_email_safe = ensure_utf8_string(admin_data["email"])
        except Exception as e:
            logger.error(f"Admin Init: Erreur lors de la sanitisation des données admin: {e}")
            logger.info("Admin Init: Initialisation admin ignorée")
            return False
        
        db = None
        try:
            # Ensure tables exist (non-blocking)
            try:
                Base.metadata.create_all(bind=engine)
            except Exception as e:
                logger.warning(f"Admin Init: Erreur lors de la création des tables (ignorée): {e}")
                # Continue anyway - tables might already exist
            
            db = SessionLocal()
            
            # Query with sanitized email - this should never crash
            try:
                admin = db.query(Employee).filter(Employee.email == admin_email_safe).first()
            except Exception as e:
                logger.error(f"Admin Init: Erreur lors de la requête admin (ignorée): {e}")
                logger.info("Admin Init: Initialisation admin ignorée")
                return False

            if not admin:
                # Create admin with all sanitized strings
                try:
                    admin = Employee(
                        name=ensure_utf8_string(admin_data["name"]),
                        email=admin_email_safe,
                        password=ensure_utf8_string(admin_data["password"]),
                        role=ensure_utf8_string(admin_data["role"]),
                        hire_date=datetime.strptime(admin_data["hire_date"], "%Y-%m-%d").date(),
                        status=bool(admin_data["status"])
                    )
                    db.add(admin)
                    db.commit()
                    logger.info("Admin Init: Administrateur créé avec succès")
                except Exception as e:
                    logger.error(f"Admin Init: Erreur lors de la création de l'admin (ignorée): {e}")
                    try:
                        db.rollback()
                    except Exception:
                        pass
                    return False
            else:
                logger.info("Admin Init: Administrateur existe déjà")

            # Crée également un employé test (non-blocking)
            try:
                cls.create_default_test_user()
            except Exception as e:
                logger.warning(f"Admin Init: Erreur lors de la création de l'employé test (ignorée): {e}")
            
            return True

        except Exception as e:
            # CATCH ALL EXCEPTIONS - NEVER CRASH THE APP
            logger.error(f"Admin Init: Erreur inattendue (ignorée): {e}")
            logger.info("Admin Init: L'application continuera sans initialiser l'admin")
            if db:
                try:
                    db.rollback()
                except Exception:
                    pass
            return False
        finally:
            if db:
                try:
                    db.close()
                except Exception:
                    pass

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[Employee]:
        """
        Authentifie un utilisateur par son nom d'utilisateur et mot de passe.
        
        Args:
            db: Session de base de données
            username: Nom d'utilisateur (email)
            password: Mot de passe
            
        Returns:
            Optional[Employee]: Utilisateur authentifié ou None si authentification échouée
        """
        # Sanitize username before database query
        username_safe = ensure_utf8_string(username)
        user = db.query(Employee).filter(Employee.email == username_safe).first()
        if not user:
            return None
        if not AuthService.check_password(password, user.password):
            return None
        if not user.status:
            return None
        return user

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Crée un token JWT pour l'authentification.
        
        Args:
            data: Données à encoder dans le token
            expires_delta: Durée de validité du token
            
        Returns:
            str: Token JWT encodé
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Employee:
        """
        Récupère l'utilisateur actuel à partir du token JWT.
        
        Args:
            token: Token JWT
            db: Session de base de données
            
        Returns:
            Employee: Utilisateur actuel
            
        Raises:
            HTTPException: Si le token est invalide ou l'utilisateur n'existe pas
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossible de valider les informations d'identification",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            # Sanitize username before database query
            username_safe = ensure_utf8_string(username)
        except JWTError:
            raise credentials_exception
        user = db.query(Employee).filter(Employee.email == username_safe).first()
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    async def get_current_active_user(current_user: Employee = Depends(get_current_user)) -> Employee:
        """
        Vérifie que l'utilisateur actuel est actif.
        
        Args:
            current_user: Utilisateur actuel
            
        Returns:
            Employee: Utilisateur actuel actif
            
        Raises:
            HTTPException: Si l'utilisateur est inactif
        """
        if not current_user.status:
            raise HTTPException(status_code=400, detail="Utilisateur inactif")
        return current_user

    @staticmethod
    def check_password(plain_password: str, hashed_password: str) -> bool:
        """
        Vérifie si le mot de passe en clair correspond au mot de passe hashé.
        
        Args:
            plain_password: Mot de passe en clair
            hashed_password: Mot de passe hashé
            
        Returns:
            bool: True si les mots de passe correspondent, False sinon
        """
        # Si le mot de passe est déjà hashé, on utilise le contexte de hash pour vérifier
        if hashed_password.startswith('$2b$'):
            return pwd_context.verify(plain_password, hashed_password)
        # Sinon, on compare directement (pour compatibilité avec les mots de passe non hashés)
        return plain_password == hashed_password

    @staticmethod
    def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change le mot de passe d'un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            current_password: Mot de passe actuel
            new_password: Nouveau mot de passe
            
        Returns:
            bool: True si le changement a réussi, False sinon
        """
        user = db.query(Employee).filter(Employee.id == user_id).first()
        if not user:
            return False
        
        if not AuthService.check_password(current_password, user.password):
            return False
        
        hashed_password = pwd_context.hash(new_password)
        user.password = hashed_password
        db.commit()
        return True

    @staticmethod
    def reset_password(db: Session, email: str, new_password: str) -> bool:
        """
        Réinitialise le mot de passe d'un utilisateur.
        
        Args:
            db: Session de base de données
            email: Email de l'utilisateur
            new_password: Nouveau mot de passe
            
        Returns:
            bool: True si la réinitialisation a réussi, False sinon
        """
        # Sanitize email before database query
        email_safe = ensure_utf8_string(email)
        user = db.query(Employee).filter(Employee.email == email_safe).first()
        if not user:
            return False
        
        hashed_password = pwd_context.hash(new_password)
        user.password = hashed_password
        db.commit()
        return True


# ====================
# Utils
# ====================

def get_current_user(request: Request):
    """
    Récupère l'utilisateur connecté à partir du cookie.
    """
    user_email = request.cookies.get("user_email")
    if not user_email:
        raise HTTPException(status_code=403, detail="Accès refusé.")
    return user_email


def notify_employee(db: Session, employee_id: int, message: str):
    """
    Crée une notification dans la base pour un employé donné.
    """
    from app.models.notification import Notification
    # Sanitize message before database operation
    message_safe = ensure_utf8_string(message)
    notif = Notification(
        employee_id=employee_id,
        message=message_safe,
        created_at=datetime.now(UTC)
    )
    db.add(notif)
    db.commit()
