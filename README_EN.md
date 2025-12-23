# 📌 Human Resources Management System

> 📖 This document contains **all the information** about the project: configuration, architecture, design patterns, tests, structure, and execution instructions.

> 🇫🇷 **Version française** : Voir [Readme.md](Readme.md)

## 📚 Academic Context

This project was developed as part of the **"Object-Oriented Approaches"** course as a personal academic project. It demonstrates the practical application of object-oriented design principles, design patterns, and clean software architecture.

**Author**: Mallek Hannachi  
**Year**: March 2025  
**Type**: Personal academic project

> ⚠️ **Note**: All data used in this project (names, emails, identifiers) are **fictional** and are used solely for demonstration and testing purposes.

---

## 📄 Project Report

👉 [Download the report (PDF)](projetift785_2_.pdf)

---

## 🎯 SOLID Principles and Software Quality

This project adheres to **SOLID principles** and implements **clean architecture**:

### SOLID Principles

- **S - Single Responsibility Principle**: Each class/module has a single, clear responsibility
  - `AuthService`: Authentication only
  - `EmployeeService`: Employee management only
  - `LeaveService`: Leave management only

- **O - Open/Closed Principle**: Open for extension, closed for modification
  - Use of design patterns (Strategy, Factory) for extensibility
  - New notification types can be added without modifying existing code

- **L - Liskov Substitution Principle**: Subtypes are substitutable for their base types
  - Interfaces and abstractions respect substitution

- **I - Interface Segregation Principle**: Specific interfaces rather than general ones
  - Separation of interfaces by responsibility (repositories, services)

- **D - Dependency Inversion Principle**: Depend on abstractions, not implementations
  - Dependency injection via FastAPI
  - Abstract repositories for data access

### Clean Architecture

The project follows a clearly separated layered architecture:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │  ← HTTP/REST entry points
│      app/api/*.py                   │
├─────────────────────────────────────┤
│      Service Layer                  │  ← Business logic
│      app/services/*.py              │
├─────────────────────────────────────┤
│      Repository Layer               │  ← Data access abstraction
│      app/repositories/*.py          │
├─────────────────────────────────────┤
│      Data Layer (SQLAlchemy)        │  ← ORM models and database
│      app/models/*.py                │
└─────────────────────────────────────┘
```

**Separation of responsibilities**:
- **API Layer**: HTTP request validation, response handling
- **Service Layer**: Business logic, business rules, orchestration
- **Repository Layer**: Data access abstraction, database isolation
- **Data Layer**: Data models, ORM mapping

This architecture ensures:
- **Low coupling**: Each layer depends only on the layer below
- **High cohesion**: Each module has a well-defined responsibility
- **Testability**: Each layer can be tested independently
- **Maintainability**: Changes are isolated to specific layers

---

## 🔐 Login Credentials

### 👩‍💼 Administrator
- **Email / username**: `admin`
- **Password**: `admin123`

### 👨‍💻 Employee (example)
- **Email / username**: `hannachimallek8@gmail.com`
- **Password**: `default_password`

### 👨‍💻 Employee (Supervisor)
- **Email / username**: `faroukhan@gmail.com`
- **Password**: `default_password`

> ⚠️ **Note**: These credentials are fictional and intended for testing purposes only.

---

## 🛠 Installation

1. **Clone the project**
   ```sh
   git clone <REPO_URL>
   cd <REPO_NAME>
   ```

2. **Create and activate a virtual environment**
   ```sh
   python -m venv venv
   venv\Scripts\activate     # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure the database**
   ```
   For database configuration, make sure you use
   a PostgreSQL, SQLite, or other database that you have
   configured. Ensure you properly define your environment variables or configure
   the configuration file with the correct connection information.
   ```
   **Run migrations to prepare the database:**
   ```sh
   alembic upgrade head
   ```

---

## 🚀 Running the Application

**Start the FastAPI application**

```sh
uvicorn app.main:app --reload
```

**Port**: The application will be accessible by default on http://127.0.0.1:8000

**For other ports:**
```sh
python -m uvicorn app.main:app --reload --port 8080
```

---

## 🧪 Automated Tests

The project includes a comprehensive suite of automated tests covering different testing levels:

### 🔧 Unit Tests

Test individual components (services, repositories, models) in isolation.

**Run unit tests:**
```sh
pytest tests/ -v
```

**Unit test examples:**
- `test_leave_requests.py`: Leave request creation test
- `test_leave_repository_additional.py`: Leave repository test
- `test_objectives_api.py`, `test_leave_state_api.py`

### 🌀 Integration Tests

Test the interaction between multiple components (services, repositories, API).

**Integration test examples:**
- `test_integration_employee.py`: Create, update, retrieve an employee via API
- Complete workflow tests between services

### 🚤 End-to-End (E2E) Tests

Test complete scenarios from API to database.

**E2E test examples:**
- `test_e2e_training_request.py`: Creation, approval, training plan (complete workflow)
- `test_end_to_end_leave_request.py`: Leave request from A to Z

### 📊 Code Coverage Report

**Run all tests with coverage:**
```sh
pytest --maxfail=1 --disable-warnings -v
```

**Generate a coverage report:**
```sh
python -m pytest --cov=app --cov-report=term-missing
```

**Coverage report in HTML:**
```sh
pytest --cov=app --cov-report=html
```
Open `htmlcov/index.html` in a browser to view the report.

---

## 📂 Project Structure

```
📁PROJET_GRH_MALLEK/
├── .pytest_cache/
├── alembic/              # Database migrations
├── app/
│   ├── api/              # REST API layer (FastAPI endpoints)
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
│   ├── models/           # SQLAlchemy models (data layer)
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
│   ├── services/         # Service layer (business logic)
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
│   ├── static/           # Static files (CSS, JS, images)
│   ├── templates/        # Jinja2 templates
├── migrations/
├── scripts/
├── tests/                # Automated tests
│   ├── conftest.py
│   ├── test_report_service.py
│   ├── test_database.py
│   ├── test_authentication.py
├── requirements.txt      # Python dependencies
├── .gitignore
├── alembic.ini
├── LICENSE               # MIT License
├── documentation/
│   ├── projet_doc.txt
└── README.md
```

---

## ✨ Design Patterns and Architecture

### 📄 Design Patterns Used

- **Factory (Abstract Factory)**  
  *Files*: `app/services/abstract_factory.py`, `app/factories/`  
  Usage: Abstract creation of services (EmployeeService, LeaveService).

- **Facade**  
  *File*: `app/services/leave_workflow_facade.py`  
  Usage: Encapsulation of leave management workflow.

- **Repository**  
  *Directory*: `app/repositories/`  
  Usage: Data access abstraction (employees, leaves, training).

- **Strategy**  
  *Directory*: `app/strategies/notifications/`  
  Usage: Notification system. Dynamic choice of channel (email, SMS, database).

- **Observer**  
  *Directory*: `app/observers/`  
  Usage: Event-related notifications, observer management.

- **State Pattern**  
  *Directory*: `app/states/leave_request/`  
  Usage: Leave request state transitions (pending, approved, rejected).

- **Singleton**  
  *Class*: `EventSubject`  
  Usage: Single instance to manage observers.

- **Service Layer**  
  *Directory*: `app/services/`  
  Usage: Business logic encapsulation (LeaveService, NotificationService).

- **Dependency Injection**  
  Usage: Injection of DB sessions, services, strategies via FastAPI.

### Benefits in the Project

- ✅ **Low coupling**: Independent and reusable components
- ✅ **High cohesion**: Each module has a clear responsibility
- ✅ **Extensibility**: Easy to add new features
- ✅ **Maintainability**: Clean and well-organized architecture
- ✅ **Testability**: Each layer can be tested independently

---

## 📜 Layered Architecture

The project follows a layered architecture (Clean Architecture):

| Layer | Responsibility | Location |
|-------|---------------|----------|
| **API Layer** | REST entry points, request validation | `app/api/*.py` |
| **Service Layer** | Business logic, business rules | `app/services/*.py` |
| **Repository Layer** | Data access abstraction | `app/repositories/*.py` |
| **Data Layer** | ORM models, database mapping | `app/models/*.py` |
| **Schemas** | Input/output validation (Pydantic) | `app/schemas/` |
| **Observers** | Reactive notifications | `app/observers/` |
| **Strategies** | Dynamic behavior choices | `app/strategies/` |
| **Tests** | Automated tests (unit, integration, E2E) | `tests/` |

---

## 📁 Documentation

- Detailed project documentation is available in `documentation/projet_doc.txt`

---

## 📔 Author and License

**Author**: Mallek Hannachi  
**Year**: March 2025  
**Type**: Personal academic project

This is a personal project developed in an academic context. All rights reserved.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

All data in this project (usernames, emails, identifiers, etc.) is **entirely fictional** and is used solely for demonstration, testing, and learning purposes. This project does not process any real data.

---

## 🤝 Contributing

This is a personal academic project. External contributions are not accepted at this time.

