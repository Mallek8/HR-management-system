# 🗂️ Documentation Technique du Projet RH - HannaWork

## 🎯 Objectif du Projet

Ce fichier présente le développement d’une application de gestion des ressources humaines, réalisée dans le cadre du cours IFT785 : Approches orientées objet.

### Objectifs principaux :
- Appliquer les principes SOLID
- Utiliser des design patterns adaptés
- Mettre en œuvre les bonnes pratiques de développement
- Assurer une couverture de tests suffisante pour garantir la robustesse du système

---

## 🏗️ Architecture de l’Application

### 🔁 Architecture en Couches

L’architecture suit une approche modulaire à quatre couches :

#### 1. Couche API
- Gère les requêtes HTTP via FastAPI
- Valide les entrées et délègue à la couche service
- Exemples :
  - `app/api/employees.py`
  - `app/api/leave_api.py`

#### 2. Couche Service
- Contient la logique métier et les règles de gestion
- Exemples :
  - `app/services/employee_service.py`
  - `app/services/leave_service.py`

#### 3. Couche Repository
- Gère les accès aux données et les opérations CRUD
- Exemples :
  - `app/repositories/employee_repository.py`
  - `app/repositories/leave_repository.py`

#### 4. Couche Modèle
- Représente les entités avec SQLAlchemy
- Exemples :
  - `app/models/employee.py`
  - `app/models/leave.py`

Cette architecture assure une séparation claire des responsabilités, une forte maintenabilité et une extension facilitée.

---

## 🧱 Modélisation des Entités

Des exempels des principales entités du système RH :

- `Employee` : informations personnelles et professionnelles
- `Role`, `Department` : structuration de l'organisation
- `EmployeeRole` : liaison employé ↔ rôles
- `Leave`, `LeaveBalance` : gestion des congés et supervision
- `Evaluation`, `Objective` : suivi de la performance
- `Notification` : communication liée aux actions RH
- `Training`, `TrainingRequest`, `TrainingPlan`, `EmployeeTraining` : gestion de la formation

---

## 🧩 Design Patterns Utilisés

| Pattern                | Emplacement principal                            | Rôle principal                                                           |
|------------------------|--------------------------------------------------|-------------------------------------------------------------------------|
| Abstract Factory       | `services/abstract_factory.py`                  | Créer dynamiquement les services métier                                |
| Facade                 | `services/leave_workflow_facade.py`             | Simplifier les appels complexes dans le traitement des congés          |
| Repository             | `repositories/`                                  | Encapsuler l’accès aux données                                          |
| Observer               | `observers/event_subject.py`                    | Notifier les observateurs en cas d’événement                           |
| Strategy               | `strategies/notification/`                      | Gérer dynamiquement les canaux de notification                         |
| Singleton              | `observers/event_subject.py`                    | Maintenir une instance unique du sujet d’événements                    |
| State                  | `services/state/leave_state_service.py`         | Gérer les transitions d’états des congés                                |
| Factory (App Factory)  | `factories/app_factory.py`                     | Centraliser l’initialisation de l’application                          |
| Service Layer          | `services/`                                     | Encapsuler la logique métier                                            |
| Dependency Injection   | `api/`, via `Depends(get_db)`                   | Injecter les dépendances (DB, services, etc.)                           |

---

## 📚 Documentation de l’API

L’API suit les conventions REST et est documentée automatiquement via Swagger.

### Principaux Endpoints :
- `GET /api/employees` : Récupère la liste des employés
- `POST /api/employees` : Crée un nouvel employé
- `PUT /api/employees/{id}` : Modifie un employé
- `DELETE /api/employees/{id}` : Supprime un employé

Les données sont validées avec Pydantic.

---

## 🧪 Stratégie de Tests et Couverture

Les tests sont organisés en trois niveaux :

### 1. Tests Unitaires exemple
- Objectif : tester des fonctions isolées sans dépendance externe
- Fichiers :
  - `test_leave_service.py`
  - `test_evaluation_service.py`

### 2. Tests d’Intégration exemple 
- Objectif : tester l’interaction entre services, base de données et API
- Fichier : `test_integration_leave_request.py`

### 3. Tests End-to-End (E2E) exemple 
- Objectif : simuler le comportement utilisateur complet
- Fichier : `test_e2e_training_request.py`

### Résumé de la couverture (pytest-cov)

| Fichier                                | Couverture |
|----------------------------------------|------------|
| `leave_service.py`                     | 68 %       |
| `evaluation_service.py`                | 52 %       |
| `employee_repository.py`               | 61 %       |
| `leave_repository.py`                  | 34 %       |
| `dashboard_admin.py`                   | 100 %      |
| `main.py`                              | 81 %       |
| **Total global**                       | **76 %**   |

> La couverture est mesurée automatiquement dans GitLab CI via `pytest-cov`

---

## ✅ Exemples Concrets d’Utilisation

### Gestion des Congés
- Vérification automatique du solde
- Consultation du calendrier de l’équipe
- Transmission automatique au superviseur
- Notification à l’employé de la décision
- Mise à jour du planning en cas d’approbation

### Système de Formation
- Catalogue de formations affiché dynamiquement
- Suggestions personnalisées
- Soumission et approbation de demandes
- Génération automatique de plans de formation

### Évaluations Annuelles
- Génération des formulaires d’évaluation
- Rappel des objectifs assignés
- Centralisation des retours
- Création d’un rapport de synthèse final

---

## 🧾 Conclusion

Le projet HannaWork constitue une base fonctionnelle solide pour une solution RH académique.

### Forces identifiées :
- Architecture modulaire, claire et extensible
- Application rigoureuse des principes SOLID
- Intégration de nombreux design patterns adaptés
- Tests de différents niveaux avec couverture adéquate

### Axes d’amélioration :
- Ergonomie de l’interface utilisateur
- Gestion avancée des rôles et permissions
- Sécurité des accès et scalabilité



