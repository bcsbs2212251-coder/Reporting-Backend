from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models_mysql.report import Report, ReportCreate, ReportUpdate, ReportResponse
from models_mysql.user import User
from utils.mysql_db import get_db
from utils.auth import get_current_user
from typing import List
import json

router = APIRouter()

@router.post("/")
@router.post("")
def create_report(report: ReportCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user_id = int(current_user.get("user_id"))
        
        # Get user info
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create report
        db_report = Report(
            user_id=user_id,
            user_name=user.full_name,
            project_name=report.project_name,
            project_code=report.project_code,
            description=report.description,
            attachments=json.dumps(report.attachments) if report.attachments else json.dumps([]),
            voice_notes=json.dumps(report.voice_notes) if report.voice_notes else json.dumps([]),
            status="pending"
        )
        
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        return {
            "success": True,
            "message": "Report created successfully",
            "data": {
                "report_id": db_report.id
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Create Report Error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/")
@router.get("")
def get_reports(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user_id = int(current_user.get("user_id"))
        user_role = current_user.get("role")
        
        # Admins see all reports, employees see only their own
        if user_role == "admin":
            reports = db.query(Report).order_by(desc(Report.created_at)).all()
        else:
            reports = db.query(Report).filter(Report.user_id == user_id).order_by(desc(Report.created_at)).all()
        
        # Convert to dict format
        reports_list = []
        for report in reports:
            reports_list.append({
                "_id": str(report.id),
                "user_id": str(report.user_id),
                "user_name": report.user_name,
                "project_name": report.project_name,
                "project_code": report.project_code,
                "description": report.description,
                "status": report.status.value if hasattr(report.status, 'value') else report.status,
                "attachments": json.loads(report.attachments) if isinstance(report.attachments, str) else report.attachments,
                "voice_notes": json.loads(report.voice_notes) if isinstance(report.voice_notes, str) else report.voice_notes,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "updated_at": report.updated_at.isoformat() if report.updated_at else None
            })
        
        return {
            "success": True,
            "data": {
                "reports": reports_list
            }
        }
    except Exception as e:
        print(f"❌ Get Reports Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{report_id}")
def get_report_by_id(report_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Check authorization
        user_id = int(current_user.get("user_id"))
        user_role = current_user.get("role")
        
        if user_role != "admin" and report.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this report"
            )
        
        return {
            "success": True,
            "data": {
                "_id": str(report.id),
                "user_id": str(report.user_id),
                "user_name": report.user_name,
                "project_name": report.project_name,
                "project_code": report.project_code,
                "description": report.description,
                "status": report.status.value if hasattr(report.status, 'value') else report.status,
                "attachments": json.loads(report.attachments) if isinstance(report.attachments, str) else report.attachments,
                "voice_notes": json.loads(report.voice_notes) if isinstance(report.voice_notes, str) else report.voice_notes,
                "created_at": report.created_at.isoformat() if report.created_at else None
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{report_id}")
def update_report(report_id: int, report_update: ReportUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Check authorization
        user_id = int(current_user.get("user_id"))
        user_role = current_user.get("role")
        
        if user_role != "admin" and report.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this report"
            )
        
        # Update fields
        if report_update.project_name:
            report.project_name = report_update.project_name
        if report_update.project_code:
            report.project_code = report_update.project_code
        if report_update.description:
            report.description = report_update.description
        if report_update.status:
            report.status = report_update.status
        
        db.commit()
        db.refresh(report)
        
        return {
            "success": True,
            "message": "Report updated successfully"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Only admins or report owner can delete
        user_id = int(current_user.get("user_id"))
        user_role = current_user.get("role")
        
        if user_role != "admin" and report.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this report"
            )
        
        db.delete(report)
        db.commit()
        
        return {
            "success": True,
            "message": "Report deleted successfully"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
