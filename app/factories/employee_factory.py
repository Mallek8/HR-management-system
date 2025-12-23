"""
abstract_factory.py — Fabrique abstraite pour la création d'employés

Responsabilités :
- Fournit un point central pour instancier des objets `Employee`
- Facilite l'extension ou modification du processus de création sans modifier l'appelant

Design Patterns :
- Factory Method : permet de déléguer l'instanciation à une méthode dédiée
- SRP : chaque classe a une seule responsabilité (ici, créer des objets Employee)

Avantages :
- Centralisation de la logique d'instanciation
- Réutilisable, testable, et facilement modifiable
"""

from app.models.employee import Employee
from app.schemas import EmployeeCreate


class EmployeeFactory:
    """
    Classe utilitaire (statique) pour créer des objets Employee à partir de schémas.
    """

    @staticmethod
    def create_employee(data: EmployeeCreate) -> Employee:
        """
        Crée une instance de Employee à partir d'un objet EmployeeCreate.

        Args:
            data (EmployeeCreate): Les données de l'employé à créer.

        Returns:
            Employee: Une instance prête à être ajoutée à la base de données.

        Raises:
            ValueError: Si la création échoue.
        """
        try:
            # Pré-traitement ou logique personnalisée possible ici (ex: validation avancée)
            return Employee(**data.model_dump())
        except Exception as e:
            raise ValueError(f"Erreur lors de la création de l'employé : {str(e)}")
