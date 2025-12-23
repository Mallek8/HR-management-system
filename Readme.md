# 🏢 HR Management System

A modern, scalable Human Resources Management System built with FastAPI and PostgreSQL. Features comprehensive employee management, leave tracking, training administration, performance evaluations, and automated notifications.

## ✨ Features

- **Employee Management**: Complete CRUD operations for employee records with role-based access control
- **Leave Management**: Request, approve, and track employee leave with state machine workflow
- **Training Management**: Create training plans, track employee training, and manage training requests
- **Performance Evaluation**: Employee evaluation and objective tracking
- **Notifications**: Multi-channel notification system (Email, SMS, Database) with Strategy pattern
- **Dashboard**: Role-specific dashboards for Admin, Supervisor, and Employee
- **Authentication & Authorization**: JWT-based authentication with role-based permissions
- **Automated Workflows**: Event-driven architecture with Observer pattern for reactive notifications

## 🏗️ Architecture

Built following **Clean Architecture** principles and **SOLID** design principles:

- **API Layer**: FastAPI REST endpoints with request validation
- **Service Layer**: Business logic and orchestration
- **Repository Layer**: Data access abstraction
- **Data Layer**: SQLAlchemy ORM models

### Design Patterns

- **Factory Pattern**: Service creation and employee factory
- **Repository Pattern**: Data access abstraction
- **Strategy Pattern**: Notification channel selection
- **Observer Pattern**: Event-driven notifications
- **State Pattern**: Leave request state transitions
- **Facade Pattern**: Workflow simplification
- **Dependency Injection**: FastAPI-based DI

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL 12+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mallek8/HR-management-system.git
   cd HR-management-system
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`

7. **Access the API documentation**
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

## 📁 Project Structure

```
HR-management-system/
├── app/
│   ├── api/              # REST API endpoints
│   ├── core/             # Configuration and security
│   ├── models/           # SQLAlchemy ORM models
│   ├── repositories/     # Data access layer
│   ├── services/         # Business logic layer
│   ├── factories/        # Factory patterns
│   ├── strategies/       # Strategy patterns
│   ├── observers/        # Observer patterns
│   └── states/           # State patterns
├── tests/                # Automated tests
│   ├── integration/      # Integration tests
│   └── e2e_test/         # End-to-end tests
├── alembic/              # Database migrations
├── frontend/             # Web interface (templates)
└── requirements.txt      # Python dependencies
```

## 🧪 Testing

The project includes comprehensive test coverage:

```bash
# Run all tests
pytest --maxfail=1 --disable-warnings -v

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # On Windows: start htmlcov/index.html
```

### Test Types

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **E2E Tests**: Complete workflow testing

## 🔐 Default Credentials

**Administrator**
- Username: `admin`
- Password: `admin123`

> ⚠️ **Important**: Change default credentials in production!

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with psycopg v3
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **Migration Tool**: Alembic
- **Testing**: pytest
- **Validation**: Pydantic

## 📊 Key Features in Detail

### Employee Management
- Create, update, and manage employee profiles
- Role-based access control (Admin, Supervisor, Employee)
- Department and role assignment
- Employee search and filtering

### Leave Management
- Request leave with approval workflow
- Leave balance tracking
- Leave history and statistics
- Automated leave balance initialization

### Training Management
- Training catalog management
- Employee training requests
- Training plan assignment
- Training completion tracking

### Notifications
- Multi-channel notifications (Email, SMS, Database)
- Event-driven notification system
- Configurable notification strategies

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Mallek Hannachi**

- GitHub: [@Mallek8](https://github.com/Mallek8)

## 🙏 Acknowledgments

- FastAPI community for the excellent framework
- SQLAlchemy team for the powerful ORM
- All contributors and users of this project

---

⭐ If you find this project helpful, please consider giving it a star!
