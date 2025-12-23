from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from sqlalchemy.orm import Session
from app.models.evaluation import Evaluation
from app.models.objective import Objective
from app.models.employee import Employee


class ReportService:
    @staticmethod
    def generate_performance_report(db: Session, employee_id: int):
        """
        Génère un rapport PDF contenant les évaluations et objectifs d'un employé.
        
        Args:
            db: Session de base de données
            employee_id: ID de l'employé
            
        Returns:
            bytes: Contenu du PDF généré
        """
        # Récupérer l'employé
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return None
            
        # Récupérer les évaluations
        evaluations = db.query(Evaluation).filter(Evaluation.employee_id == employee_id).all()
        
        # Récupérer les objectifs
        objectives = db.query(Objective).filter(Objective.employee_id == employee_id).all()
        
        # Créer un buffer pour stocker le PDF
        buffer = BytesIO()
        
        # Créer le PDF
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Ajouter l'en-tête
        c.setFont("Helvetica-Bold", 16)
        c.drawString(width/2 - 150, height - 50, f"Rapport de Performance")
        
        # Informations de l'employé
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 100, "Informations de l'employé:")
        c.setFont("Helvetica", 12)
        c.drawString(70, height - 120, f"Nom: {employee.name}")
        c.drawString(70, height - 140, f"Email: {employee.email}")
        if hasattr(employee, 'hire_date'):
            c.drawString(70, height - 160, f"Date d'embauche: {employee.hire_date}")
        
        # Évaluations
        y_position = height - 200
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Évaluations:")
        y_position -= 20
        
        if evaluations:
            for evaluation in evaluations:
                c.setFont("Helvetica", 12)
                date_str = evaluation.date.strftime("%d/%m/%Y") if evaluation.date else "N/A"
                c.drawString(70, y_position, f"Date: {date_str}")
                y_position -= 20
                c.drawString(70, y_position, f"Score: {evaluation.score}")
                y_position -= 20
                feedback = evaluation.feedback if evaluation.feedback else "Aucun commentaire"
                c.drawString(70, y_position, f"Commentaire: {feedback}")
                y_position -= 40
        else:
            c.setFont("Helvetica", 12)
            c.drawString(70, y_position, "Aucune évaluation disponible")
            y_position -= 40
        
        # Objectifs
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Objectifs:")
        y_position -= 20
        
        if objectives:
            for objective in objectives:
                c.setFont("Helvetica", 12)
                c.drawString(70, y_position, f"Description: {objective.description}")
                y_position -= 20
                
                start_date = objective.start_date.strftime("%d/%m/%Y") if objective.start_date else "N/A"
                end_date = objective.end_date.strftime("%d/%m/%Y") if objective.end_date else "N/A"
                
                c.drawString(70, y_position, f"Période: {start_date} - {end_date}")
                y_position -= 20
                
                status = objective.status if hasattr(objective, 'status') else "En cours"
                c.drawString(70, y_position, f"Statut: {status}")
                y_position -= 40
                
                # Si on arrive en bas de page, créer une nouvelle page
                if y_position < 100:
                    c.showPage()
                    y_position = height - 50
        else:
            c.setFont("Helvetica", 12)
            c.drawString(70, y_position, "Aucun objectif disponible")
        
        # Finaliser le PDF
        c.showPage()
        c.save()
        
        # Retourner le contenu PDF
        buffer.seek(0)
        return buffer.getvalue() 