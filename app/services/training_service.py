import logging
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.models.training import Training
from app.models.training_request import TrainingRequest
from app.models.employee import Employee
from sqlalchemy.exc import SQLAlchemyError

class TrainingService:
    @staticmethod
    def create_training(db: Session, training_data: dict):
        """
        Crée une nouvelle formation
        """
        try:
            training = Training(**training_data)
            db.add(training)
            db.commit()
            db.refresh(training)
            return training
        except Exception as e:
            db.rollback()
            logging.error(f"Erreur lors de la création de la formation: {e}")
            return None

    @staticmethod
    def get_all_trainings(db: Session):
        """
        Récupère toutes les formations
        """
        return db.query(Training).all()

    @staticmethod
    def get_trainings(db: Session):
        """
        Alias pour get_all_trainings
        """
        return TrainingService.get_all_trainings(db)

    @staticmethod
    def get_training_by_id(db: Session, training_id: int):
        """
        Récupère une formation par son ID
        """
        return db.query(Training).filter(Training.id == training_id).first()

    @staticmethod
    def get_training(db: Session, training_id: int):
        """
        Alias pour get_training_by_id
        """
        return TrainingService.get_training_by_id(db, training_id)

    @staticmethod
    def update_training(db: Session, training_id: int, training_data: dict):
        """
        Met à jour une formation existante
        """
        try:
            training = db.query(Training).filter(Training.id == training_id).first()
            if not training:
                return None
            
            for key, value in training_data.items():
                setattr(training, key, value)
            
            db.commit()
            db.refresh(training)
            return training
        except Exception as e:
            db.rollback()
            logging.error(f"Erreur lors de la mise à jour de la formation: {e}")
            return None

    @staticmethod
    def delete_training(db: Session, training_id: int):
        """
        Supprime une formation
        """
        try:
            training = db.query(Training).filter(Training.id == training_id).first()
            if not training:
                return False
            
            db.delete(training)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logging.error(f"Erreur lors de la suppression de la formation: {e}")
            return False

    @staticmethod
    def create_training_request(db: Session, request_data: dict):
        """
        Crée une nouvelle demande de formation
        """
        try:
            request = TrainingRequest(**request_data)
            db.add(request)
            db.commit()
            db.refresh(request)
            return request
        except Exception as e:
            db.rollback()
            logging.error(f"Erreur lors de la création de la demande de formation: {e}")
            return None

    @staticmethod
    def get_training_requests_for_employee(db: Session, employee_id: int):
        """
        Récupère toutes les demandes de formation pour un employé
        """
        return db.query(TrainingRequest).filter(TrainingRequest.employee_id == employee_id).all()

    @staticmethod
    def get_trainings_by_employee(db: Session, employee_id: int) -> List[Training]:
        """
        Récupère toutes les formations suivies par un employé donné.
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé
            
        Returns:
            List[Training]: Liste des formations
        """
        try:
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                return []
            return employee.trainings
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la récupération des formations de l'employé {employee_id}: {e}")
            return []

    @staticmethod
    def register_employee_to_training(db: Session, employee_id: int, training_id: int) -> Dict:
        """
        Inscrit un employé à une formation.
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé à inscrire
            training_id: ID de la formation
            
        Returns:
            Dict: Résultat de l'opération avec succès et message
        """
        try:
            # Récupérer l'employé et la formation
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            training = db.query(Training).filter(Training.id == training_id).first()
            
            # Vérifications
            if not employee:
                return {"success": False, "message": "Employé non trouvé"}
            if not training:
                return {"success": False, "message": "Formation non trouvée"}
                
            # Vérifier si la formation n'est pas complète
            if training.max_participants and len(training.employees) >= training.max_participants:
                return {"success": False, "message": "Formation complète, plus de places disponibles"}
                
            # Vérifier si l'employé n'est pas déjà inscrit
            if training in employee.trainings:
                return {"success": False, "message": "Employé déjà inscrit à cette formation"}
                
            # Inscrire l'employé
            employee.trainings.append(training)
            db.commit()
            
            return {"success": True, "message": f"Employé {employee.name} inscrit à la formation {training.title}"}
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de l'inscription à la formation: {e}")
            return {"success": False, "message": f"Erreur: {str(e)}"}

    @staticmethod
    def unregister_employee_from_training(db: Session, employee_id: int, training_id: int) -> Dict:
        """
        Désinscrit un employé d'une formation.
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé à désinscrire
            training_id: ID de la formation
            
        Returns:
            Dict: Résultat de l'opération avec succès et message
        """
        try:
            # Récupérer l'employé et la formation
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            training = db.query(Training).filter(Training.id == training_id).first()
            
            # Vérifications
            if not employee:
                return {"success": False, "message": "Employé non trouvé"}
            if not training:
                return {"success": False, "message": "Formation non trouvée"}
                
            # Vérifier si l'employé est inscrit
            if training not in employee.trainings:
                return {"success": False, "message": "Employé non inscrit à cette formation"}
                
            # Désinscrire l'employé
            employee.trainings.remove(training)
            db.commit()
            
            return {"success": True, "message": f"Employé {employee.name} désinscrit de la formation {training.title}"}
        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Erreur lors de la désinscription de la formation: {e}")
            return {"success": False, "message": f"Erreur: {str(e)}"}

    @staticmethod
    def get_training_stats_for_employee(db: Session, employee_id: int) -> Dict:
        """
        Récupère les statistiques de formation pour un employé spécifique.
        
        Args:
            db: Session de base de données
            employee_id: Identifiant de l'employé
            
        Returns:
            Dict: Statistiques de formation (total, sent, approved, rejected)
        """
        try:
            # Récupérer toutes les demandes de formation de l'employé
            requests = db.query(TrainingRequest).filter(TrainingRequest.employee_id == employee_id).all()
            
            # Compter les demandes par statut
            sent = sum(1 for request in requests if request.status == 'en attente')
            approved = sum(1 for request in requests if request.status == 'approuvé')
            rejected = sum(1 for request in requests if request.status == 'refusé')
            
            return {
                "total": len(requests),
                "sent": sent,
                "approved": approved,
                "rejected": rejected
            }
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des statistiques de formation pour l'employé {employee_id}: {str(e)}")
            return {"total": 0, "sent": 0, "approved": 0, "rejected": 0} 