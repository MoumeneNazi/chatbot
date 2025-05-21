from fastapi import APIRouter, Depends, HTTPException, status, Body, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from database import get_db
from dependencies import get_current_user, get_current_admin, get_current_therapist, get_therapist_or_admin
from models import User, ProblemReportModel, ProblemReportCreate, ProblemReport, ProblemReportUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/problems",
    tags=["problem_reports"]
)

@router.post("/", response_model=ProblemReport)
async def create_problem_report(
    problem: ProblemReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new problem report. Available to all authenticated users."""
    try:
        new_report = ProblemReportModel(
            user_id=current_user.id,
            title=problem.title,
            description=problem.description,
            category=problem.category,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        
        logger.info(f"Problem report created by user {current_user.username}, ID: {new_report.id}")
        return new_report
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating problem report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create problem report: {str(e)}"
        )

@router.get("/my-reports", response_model=List[ProblemReport])
async def get_my_problem_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all problem reports submitted by the current user."""
    try:
        reports = db.query(ProblemReportModel).filter(
            ProblemReportModel.user_id == current_user.id
        ).order_by(ProblemReportModel.created_at.desc()).all()
        
        return reports
    except Exception as e:
        logger.error(f"Error fetching user problem reports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch problem reports: {str(e)}"
        )

@router.get("/", response_model=List[ProblemReport])
async def get_all_problem_reports(
    status: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_therapist_or_admin),
    db: Session = Depends(get_db)
):
    """Get all problem reports. Only accessible by therapists and admins."""
    try:
        query = db.query(ProblemReportModel)
        
        if status:
            query = query.filter(ProblemReportModel.status == status)
            
        if category:
            query = query.filter(ProblemReportModel.category == category)
            
        reports = query.order_by(
            ProblemReportModel.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return reports
    except Exception as e:
        logger.error(f"Error fetching all problem reports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch problem reports: {str(e)}"
        )

@router.get("/{report_id}", response_model=ProblemReport)
async def get_problem_report(
    report_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific problem report.
    Users can only access their own reports, while therapists and admins can access any report.
    """
    try:
        report = db.query(ProblemReportModel).filter(
            ProblemReportModel.id == report_id
        ).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem report not found"
            )
            
        # Check if user is authorized to view this report
        if current_user.role not in ["therapist", "admin"] and report.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this report"
            )
            
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching problem report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch problem report: {str(e)}"
        )

@router.put("/{report_id}/status", response_model=ProblemReport)
async def update_problem_report_status(
    report_id: int = Path(..., gt=0),
    status_update: ProblemReportUpdate = Body(...),
    current_user: User = Depends(get_therapist_or_admin),
    db: Session = Depends(get_db)
):
    """Update the status of a problem report. Only accessible by therapists and admins."""
    try:
        if status_update.status not in ["pending", "in_progress", "resolved", "closed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be 'pending', 'in_progress', 'resolved', or 'closed'"
            )
            
        report = db.query(ProblemReportModel).filter(
            ProblemReportModel.id == report_id
        ).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem report not found"
            )
            
        report.status = status_update.status
        report.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(report)
        
        logger.info(f"Problem report {report_id} status updated to {status_update.status} by {current_user.username}")
        return report
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating problem report status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update problem report status: {str(e)}"
        ) 