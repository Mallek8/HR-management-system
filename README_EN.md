# 🏢 Système de Gestion des Ressources Humaines

Un système moderne et scalable de gestion des ressources humaines construit avec FastAPI et PostgreSQL. Comprend la gestion complète des employés, le suivi des congés, l'administration de la formation, les évaluations de performance et les notifications automatisées.

## ✨ Fonctionnalités

- **Gestion des Employés**: Opérations CRUD complètes pour les dossiers des employés avec contrôle d'accès basé sur les rôles
- **Gestion des Congés**: Demandes, approbations et suivi des congés des employés avec workflow à machine d'états
- **Gestion de la Formation**: Création de plans de formation, suivi de la formation des employés et gestion des demandes de formation
- **Évaluation de Performance**: Évaluation des employés et suivi des objectifs
- **Notifications**: Système de notification multi-canal (Email, SMS, Base de données) avec pattern Strategy
- **Tableau de Bord**: Tableaux de bord spécifiques par rôle pour Admin, Superviseur et Employé
- **Authentification & Autorisation**: Authentification basée sur JWT avec permissions basées sur les rôles
- **Workflows Automatisés**: Architecture orientée événements avec pattern Observer pour des notifications réactives

## 🏗️ Architecture

Construit en suivant les principes de **Clean Architecture** et les principes de conception **SOLID** :

- **Couche API**: Endpoints REST FastAPI avec validation des requêtes
- **Couche Service**: Logique métier et orchestration
- **Couche Repository**: Abstraction d'accès aux données
- **Couche Données**: Modèles ORM SQLAlchemy

### Patterns de Conception

- **Pattern Factory**: Création de services et factory d'employés
- **Pattern Repository**: Abstraction d'accès aux données
- **Pattern Strategy**: Sélection du canal de notification
- **Pattern Observer**: Notifications orientées événements
- **Pattern State**: Transitions d'état des demandes de congé
- **Pattern Facade**: Simplification des workflows
- **Injection de Dépendances**: DI basée sur FastAPI

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.13+
- PostgreSQL 12+
- pip

### Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/Mallek8/HR-management-system.git
   cd HR-management-system
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   ```bash
   cp env.example .env
   # Modifiez .env avec vos identifiants de base de données
   ```

5. **Exécuter les migrations de base de données**
   ```bash
   alembic upgrade head
   ```

6. **Démarrer l'application**
   ```bash
   uvicorn app.main:app --reload
   ```

   L'API sera disponible sur `http://127.0.0.1:8000`

7. **Accéder à la documentation de l'API**
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

## 📁 Structure du Projet

```
HR-management-system/
├── app/
│   ├── api/              # Endpoints API REST
│   ├── core/             # Configuration et sécurité
│   ├── models/           # Modèles ORM SQLAlchemy
│   ├── repositories/     # Couche d'accès aux données
│   ├── services/         # Couche de logique métier
│   ├── factories/        # Patterns Factory
│   ├── strategies/       # Patterns Strategy
│   ├── observers/        # Patterns Observer
│   └── states/           # Patterns State
├── tests/                # Tests automatisés
│   ├── integration/      # Tests d'intégration
│   └── e2e_test/         # Tests end-to-end
├── alembic/              # Migrations de base de données
├── frontend/             # Interface web (templates)
└── requirements.txt      # Dépendances Python
```

## 🧪 Tests

Le projet inclut une couverture de tests complète :

```bash
# Exécuter tous les tests
pytest --maxfail=1 --disable-warnings -v

# Exécuter avec couverture
pytest --cov=app --cov-report=html

# Voir le rapport de couverture
open htmlcov/index.html  # Sur Windows: start htmlcov/index.html
```

### Types de Tests

- **Tests Unitaires**: Test de composants individuels
- **Tests d'Intégration**: Test d'interaction entre composants
- **Tests E2E**: Test de workflows complets

## 🔐 Identifiants par Défaut

**Administrateur**
- Nom d'utilisateur: `admin`
- Mot de passe: `admin123`

> ⚠️ **Important**: Changez les identifiants par défaut en production !

## 🛠️ Stack Technologique

- **Framework**: FastAPI
- **Base de données**: PostgreSQL avec psycopg v3
- **ORM**: SQLAlchemy 2.0
- **Authentification**: JWT (JSON Web Tokens)
- **Hachage de mots de passe**: bcrypt
- **Outil de migration**: Alembic
- **Tests**: pytest
- **Validation**: Pydantic

## 📊 Fonctionnalités Clés en Détail

### Gestion des Employés
- Créer, mettre à jour et gérer les profils des employés
- Contrôle d'accès basé sur les rôles (Admin, Superviseur, Employé)
- Attribution de département et de rôle
- Recherche et filtrage des employés

### Gestion des Congés
- Demander des congés avec workflow d'approbation
- Suivi du solde de congés
- Historique et statistiques des congés
- Initialisation automatique du solde de congés

### Gestion de la Formation
- Gestion du catalogue de formations
- Demandes de formation des employés
- Attribution de plans de formation
- Suivi de la complétion des formations

### Notifications
- Notifications multi-canal (Email, SMS, Base de données)
- Système de notifications orienté événements
- Stratégies de notification configurables

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à soumettre une Pull Request.

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👤 Auteur

**Mallek Hannachi**

- GitHub: [@Mallek8](https://github.com/Mallek8)

## 🙏 Remerciements

- La communauté FastAPI pour l'excellent framework
- L'équipe SQLAlchemy pour l'ORM puissant
- Tous les contributeurs et utilisateurs de ce projet

---

⭐ Si vous trouvez ce projet utile, pensez à lui donner une étoile !
