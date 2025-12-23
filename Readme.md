# 📌 Projet de gestion des ressources humaines

> 📖 Ce document contient **l'intégralité des informations** relatives au projet : configuration, architecture, design patterns, tests, structure, et instructions d'exécution.

> 🌐 **English version**: See [README_EN.md](README_EN.md)

## 📚 Contexte académique

Ce projet a été développé dans le cadre du cours **"Approches Orientées Objet"** comme projet académique personnel. Il démontre l'application pratique des principes de conception orientée objet, des design patterns et de l'architecture logicielle propre.

**Auteur** : Mallek Hannachi  
**Année** : Mars 2025  
**Type** : Projet personnel académique

> ⚠️ **Note** : Toutes les données utilisées dans ce projet (noms, emails, identifiants) sont **fictives** et servent uniquement à des fins de démonstration et de test.

---

## 📄 Rapport du projet

👉 [Télécharger le rapport (PDF)](projetift785_2_.pdf)

---

## 🎯 Principes SOLID et qualité logicielle

Ce projet respecte les **principes SOLID** et applique une **architecture propre** (Clean Architecture) :

### Principes SOLID

- **S - Single Responsibility Principle** : Chaque classe/module a une seule responsabilité claire
  - `AuthService` : Authentification uniquement
  - `EmployeeService` : Gestion des employés uniquement
  - `LeaveService` : Gestion des congés uniquement

- **O - Open/Closed Principle** : Ouvert à l'extension, fermé à la modification
  - Utilisation de design patterns (Strategy, Factory) pour l'extensibilité
  - Nouveaux types de notifications ajoutables sans modifier le code existant

- **L - Liskov Substitution Principle** : Les sous-types sont substituables à leurs types de base
  - Interfaces et abstractions respectent la substitution

- **I - Interface Segregation Principle** : Interfaces spécifiques plutôt qu'interfaces générales
  - Séparation des interfaces par responsabilité (repositories, services)

- **D - Dependency Inversion Principle** : Dépendre des abstractions, pas des implémentations
  - Injection de dépendances via FastAPI
  - Repositories abstraits pour l'accès aux données

### Architecture propre (Clean Architecture)

Le projet suit une architecture en couches clairement séparées :

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │  ← Points d'entrée HTTP/REST
│      app/api/*.py                   │
├─────────────────────────────────────┤
│      Service Layer                  │  ← Logique métier
│      app/services/*.py              │
├─────────────────────────────────────┤
│      Repository Layer               │  ← Abstraction d'accès aux données
│      app/repositories/*.py          │
├─────────────────────────────────────┤
│      Data Layer (SQLAlchemy)        │  ← Modèles ORM et base de données
│      app/models/*.py                │
└─────────────────────────────────────┘
```

**Séparation des responsabilités** :
- **API Layer** : Validation des requêtes HTTP, gestion des réponses
- **Service Layer** : Logique métier, règles de gestion, orchestration
- **Repository Layer** : Abstraction de l'accès aux données, isolation de la base
- **Data Layer** : Modèles de données, mapping ORM

Cette architecture assure :
- **Faible couplage** : Chaque couche dépend uniquement de l'inférieure
- **Haute cohésion** : Chaque module a une responsabilité bien définie
- **Testabilité** : Chaque couche peut être testée indépendamment
- **Maintenabilité** : Modifications isolées à une couche spécifique

---

## 🔐 Identifiants de connexion

### 👩‍💼 Administrateur
- **Email / identifiant** : `admin`
- **Mot de passe** : `admin123`

### 👨‍💻 Employé (exemple)
- **Email / identifiant** : `hannachimallek8@gmail.com`
- **Mot de passe** : `default_password`

### 👨‍💻 Employé (Superviseur)
- **Email / identifiant** : `faroukhan@gmail.com`
- **Mot de passe** : `default_password`

> ⚠️ **Note** : Ces identifiants sont fictifs et destinés uniquement à des fins de test.

---

## 🛠 Installation

1. **Cloner le projet**
   ```sh
   git clone <URL_DU_REPO>
   cd <NOM_DU_REPO>
   ```

2. **Créer un environnement virtuel et l'activer**
   ```sh
   python -m venv venv
   venv\Scripts\activate     # Sur Windows
   source venv/bin/activate  # Sur Linux/Mac
   ```

3. **Installer les dépendances**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configurer la base de données**
   ```
   Pour la configuration de la base de données, assurez-vous que
   vous utilisez une base de données PostgreSQL, SQLite ou une autre que vous avez
   configurée. Assurez-vous de bien définir vos variables d'environnement ou de configurer le fichier de configuration avec les bonnes informations de connexion.
   ```
   **Exécutez les migrations pour préparer la base de données :**
   ```sh
   alembic upgrade head
   ```

---

## 🚀 Exécution de l'application

**Lancer l'application FastAPI**

```sh
uvicorn app.main:app --reload
```

**Port** : L'application sera accessible par défaut sur http://127.0.0.1:8000

**Pour d'autres ports :**
```sh
python -m uvicorn app.main:app --reload --port 8080
```

---

## 🧪 Tests automatisés

Le projet inclut une suite complète de tests automatisés couvrant différents niveaux de test :

### 🔧 Tests unitaires

Testent les composants individuels (services, repositories, modèles) de manière isolée.

**Exécuter les tests unitaires :**
```sh
pytest tests/ -v
```

**Exemples de tests unitaires :**
- `test_leave_requests.py` : Test de création de demande de congé
- `test_leave_repository_additional.py` : Test du repository Leave
- `test_objectives_api.py`, `test_leave_state_api.py`

### 🌀 Tests d'intégration

Testent l'interaction entre plusieurs composants (services, repositories, API).

**Exemples de tests d'intégration :**
- `test_integration_employee.py` : Création, mise à jour, récupération d'un employé via API
- Tests des workflows complets entre services

### 🚤 Tests end-to-end (E2E)

Testent des scénarios complets depuis l'API jusqu'à la base de données.

**Exemples de tests E2E :**
- `test_e2e_training_request.py` : Création, approbation, plan de formation (workflow complet)
- `test_end_to_end_leave_request.py` : Demande de congé de A à Z

### 📊 Rapport de couverture de code

**Exécuter tous les tests avec couverture :**
```sh
pytest --maxfail=1 --disable-warnings -v
```

**Générer un rapport de couverture :**
```sh
python -m pytest --cov=app --cov-report=term-missing
```

**Rapport de couverture en HTML :**
```sh
pytest --cov=app --cov-report=html
```
Ouvrez `htmlcov/index.html` dans un navigateur pour visualiser le rapport.

---

## 📂 Structure du projet

```
📁PROJET_GRH_MALLEK/
├── .pytest_cache/
├── alembic/              # Migrations de base de données
├── app/
│   ├── api/              # Couche API REST (endpoints FastAPI)
│   │   ├── auth.py
│   │   ├── dashboard_admin.py
│   │   ├── dashboard_employee.py
│   │   ├── dashboard_supervisor.py
│   │   ├── employees.py
│   │   ├── evaluations.py
│   │   ├── leave_api.py
│   │   ├── leave_requests.py
│   │   ├── objectives.py
│   │   ├── profile.py
│   │   ├── reports.py
│   │   ├── training_requests.py
│   │   ├── trainings.py
│   ├── factories/        # Design Pattern: Factory
│   │   ├── app_factory.py
│   │   ├── employee_factory.py
│   ├── models/           # Modèles SQLAlchemy (couche données)
│   │   ├── department.py
│   │   ├── employee_role.py
│   │   ├── employee_training.py
│   │   ├── employee.py
│   │   ├── evaluation.py
│   │   ├── leave_balance.py
│   │   ├── leave.py
│   │   ├── notification.py
│   │   ├── objective.py
│   │   ├── role.py
│   │   ├── training_plan.py
│   │   ├── training_request.py
│   │   ├── training.py
│   ├── repositories/     # Design Pattern: Repository
│   │   ├── employee_repository.py
│   │   ├── leave_repository.py
│   ├── routes/
│   ├── services/         # Couche service (logique métier)
│   │   ├── abstract_factory.py
│   │   ├── auth_service.py
│   │   ├── dashboard_controller.py
│   │   ├── employee_service.py
│   │   ├── evaluation_service.py
│   │   ├── leave_service.py
│   │   ├── leave_workflow_facade.py
│   │   ├── notification_service.py
│   │   ├── report_service.py
│   │   ├── training_plan_service.py
│   ├── strategies/       # Design Pattern: Strategy
│   │   └── notifications/
│   ├── states/           # Design Pattern: State
│   │   └── leave_request/
│   ├── observers/        # Design Pattern: Observer
├── frontend/
│   ├── static/           # Fichiers statiques (CSS, JS, images)
│   ├── templates/        # Templates Jinja2
├── migrations/
├── scripts/
├── tests/                # Tests automatisés
│   ├── conftest.py
│   ├── test_report_service.py
│   ├── test_database.py
│   ├── test_authentication.py
├── requirements.txt      # Dépendances Python
├── .gitignore
├── alembic.ini
├── LICENSE               # Licence MIT
├── documentation/
│   ├── projet_doc.txt
└── README.md
```

---

## ✨ Design Patterns et architecture

### 📄 Design Patterns utilisés

- **Factory (Abstract Factory)**  
  *Fichier* : `app/services/abstract_factory.py`, `app/factories/`  
  Utilisation : Création abstraite des services (EmployeeService, LeaveService).

- **Facade**  
  *Fichier* : `app/services/leave_workflow_facade.py`  
  Utilisation : Encapsulation du workflow de gestion des congés.

- **Repository**  
  *Dossier* : `app/repositories/`  
  Utilisation : Abstraction de l'accès aux données (employés, congés, formations).

- **Strategy**  
  *Dossier* : `app/strategies/notifications/`  
  Utilisation : Système de notification. Choix dynamique du canal (email, SMS, base de données).

- **Observer**  
  *Dossier* : `app/observers/`  
  Utilisation : Notifications liées à des événements, gestion d'observateurs.

- **State Pattern**  
  *Dossier* : `app/states/leave_request/`  
  Utilisation : Transitions d'état des demandes de congé (pending, approved, rejected).

- **Singleton**  
  *Classe* : `EventSubject`  
  Utilisation : Une instance unique pour gérer les observateurs.

- **Service Layer**  
  *Dossier* : `app/services/`  
  Utilisation : Encapsulation de la logique métier (LeaveService, NotificationService).

- **Dependency Injection**  
  Utilisation : Injection des sessions DB, services, stratégies via FastAPI.

### Avantages dans le projet

- ✅ **Faible couplage** : Composants indépendants et réutilisables
- ✅ **Haute cohésion** : Chaque module a une responsabilité claire
- ✅ **Extensibilité** : Facile d'ajouter de nouvelles fonctionnalités
- ✅ **Maintenabilité** : Architecture propre et bien organisée
- ✅ **Testabilité** : Chaque couche peut être testée indépendamment

---

## 📜 Architecture en couches

Le projet suit une architecture en couches (Clean Architecture) :

| Couche | Responsabilité | Localisation |
|--------|---------------|--------------|
| **API Layer** | Points d'accès REST, validation des requêtes | `app/api/*.py` |
| **Service Layer** | Logique métier, règles de gestion | `app/services/*.py` |
| **Repository Layer** | Abstraction de l'accès aux données | `app/repositories/*.py` |
| **Data Layer** | Modèles ORM, mapping base de données | `app/models/*.py` |
| **Schemas** | Validation des entrées/sorties (Pydantic) | `app/schemas/` |
| **Observers** | Notifications réactives | `app/observers/` |
| **Strategies** | Choix de comportements dynamiques | `app/strategies/` |
| **Tests** | Tests automatisés (unitaire, intégration, E2E) | `tests/` |

---

## 📁 Documentation

- La documentation détaillée du projet est disponible dans `documentation/projet_doc.txt`

---

## 📔 Auteur et licence

**Auteur** : Mallek Hannachi  
**Année** : Mars 2025  
**Type** : Projet personnel académique

Ce projet est un projet personnel développé dans un contexte académique. Tous les droits sont réservés.

### Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## ⚠️ Avertissement

Toutes les données présentes dans ce projet (noms d'utilisateurs, emails, identifiants, etc.) sont **entièrement fictives** et sont utilisées uniquement à des fins de démonstration, de test et d'apprentissage. Ce projet ne traite aucune donnée réelle.

---

## 🤝 Contribution

Ce projet est un projet académique personnel. Les contributions externes ne sont pas acceptées pour le moment.
