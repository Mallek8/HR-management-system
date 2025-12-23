from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Objective(Base):
    """
    Représente un objectif de performance pour un employé.
    """
    __tablename__ = "objectives"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    progress = Column(Integer, default=0)  # Progrès en pourcentage (0 à 100)

    employee = relationship("Employee", back_populates="objectives")
