from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/{employee_id}")
async def generate_employee_report(employee_id: int, db: Session = Depends(get_db)):
    """
    Génère un rapport PDF pour un employé spécifique contenant ses évaluations et objectifs.
    
    Args:
        employee_id: ID de l'employé
        db: Session de base de données
        
    Returns:
        StreamingResponse: Fichier PDF à télécharger
    """
    # Générer le PDF avec le service
    pdf_content = ReportService.generate_performance_report(db, employee_id)
    
    if not pdf_content:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Retourner le fichier PDF en streaming pour téléchargement
    return StreamingResponse(
        BytesIO(pdf_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rapport_performance_{employee_id}.pdf"}
    )

report_router = router 