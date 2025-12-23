"""
abstract_factory.py - Implémentation du Design Pattern Factory pour la création d'entités métier.

Responsabilités :
- Encapsule la création d’objets `Employee` pour éviter la duplication de logique dans les services.
- Fournit un point unique pour ajouter des règles métier liées à l’instanciation.

Design Pattern :
- Factory Method : encapsule l’instanciation des objets `Employee`.

Conformité SOLID :
- SRP (Single Responsibility Principle) : une seule responsabilité, créer des objets Employee.
- OCP (Open-Closed Principle) : permet d'étendre la logique de création sans modifier la structure du code.

Utilisation :
    employee = EmployeeFactory.create_employee(employee_create_schema)
"""

from app.models.employee import Employee
from app.schemas import EmployeeCreate

class EmployeeFactory:
    """
    Classe usine pour la création d'objets `Employee` à partir des schémas `EmployeeCreate`.
    """

    @staticmethod
    def create_employee(data: EmployeeCreate) -> Employee:
        """
        Crée une instance de Employee à partir d’un schéma `EmployeeCreate`.

        Args:
            data (EmployeeCreate): Données de l’employé à créer.

        Returns:
            Employee: Instance ORM prête à être ajoutée à la base de données.

        Raises:
            ValueError: En cas d'erreur de transformation.
        """
        try:
            
            return Employee(**data.model_dump())
        except Exception as e:
            raise ValueError(f"Erreur lors de la création de l'employé : {str(e)}")
