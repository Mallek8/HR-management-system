from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.leave_service import LeaveService
from app.models.employee import Employee  # Import Employee model
from fastapi.templating import Jinja2Templates
import logging

router = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="frontend/templates")
logger = logging.getLogger(__name__)

# Route for the supervisor dashboard
@router.get("/dashboard_supervisor")
async def dashboard_supervisor(request: Request, db: Session = Depends(get_db)):
    """
    Route to display the supervisor's dashboard.
    """
    try:
        user_email = request.cookies.get("user_email")
        if not user_email:
            raise HTTPException(status_code=403, detail="Access denied")

        # Fetch the user (employee) data
        user = db.query(Employee).filter(Employee.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch notifications for the supervisor
        notifications = LeaveService.get_notifications(db, user_email)

        # Fetch leave requests for the supervisor
        leave_requests = LeaveService.get_leave_requests_for_supervisor(db, user_email)

        # Fetch employees currently on leave under the supervisor
        employees_on_leave = LeaveService.get_employees_on_leave(db, user_email)

        # Pass user data to the template
        return templates.TemplateResponse("dashboard_supervisor.html", {
            "request": request,
            "user": user,  # Pass the user data here
            "notifications": notifications,
            "leave_requests": leave_requests,
            "employees_on_leave": employees_on_leave
        })
    except HTTPException:
        # Re-raise HTTP exceptions directly
        raise
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Error in dashboard_supervisor: {str(e)}")
        # Return a generic error to the client
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
