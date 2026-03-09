from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models_mysql.report import Report
from models_mysql.task import Task
from models_mysql.leave import Leave
from utils.mysql_db import get_db
from utils.auth import get_current_user

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user_id = int(current_user.get("user_id"))
        user_role = current_user.get("role")
        
        if user_role == "admin":
            total_reports = db.query(Report).count()
            total_tasks = db.query(Task).count()
            pending_reports = db.query(Report).filter(Report.status == "pending").count()
            pending_tasks = db.query(Task).filter(Task.status == "pending").count()
        else:
            total_reports = db.query(Report).filter(Report.user_id == user_id).count()
            total_tasks = db.query(Task).filter(Task.user_id == user_id).count()
            pending_reports = db.query(Report).filter(Report.user_id == user_id, Report.status == "pending").count()
            pending_tasks = db.query(Task).filter(Task.user_id == user_id, Task.status == "pending").count()
        
        return {
            "success": True,
            "data": {
                "my_reports": total_reports,
                "my_tasks": total_tasks,
                "pending_reports": pending_reports,
                "pending_tasks": pending_tasks
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user_id = int(current_user.get("user_id"))
        user_role = current_user.get("role")
        
        if user_role == "admin":
            # Admin analytics - all data
            total_reports = db.query(Report).count()
            total_tasks = db.query(Task).count()
            total_leaves = db.query(Leave).count()
            
            pending_reports = db.query(Report).filter(Report.status == "pending").count()
            approved_reports = db.query(Report).filter(Report.status == "approved").count()
            rejected_reports = db.query(Report).filter(Report.status == "rejected").count()
            
            pending_tasks = db.query(Task).filter(Task.status == "pending").count()
            in_progress_tasks = db.query(Task).filter(Task.status == "in_progress").count()
            completed_tasks = db.query(Task).filter(Task.status == "completed").count()
            
            pending_leaves = db.query(Leave).filter(Leave.status == "pending").count()
            approved_leaves = db.query(Leave).filter(Leave.status == "approved").count()
            rejected_leaves = db.query(Leave).filter(Leave.status == "rejected").count()
            
            return {
                "success": True,
                "data": {
                    "reports": {
                        "total": total_reports,
                        "pending": pending_reports,
                        "approved": approved_reports,
                        "rejected": rejected_reports
                    },
                    "tasks": {
                        "total": total_tasks,
                        "pending": pending_tasks,
                        "in_progress": in_progress_tasks,
                        "completed": completed_tasks
                    },
                    "leaves": {
                        "total": total_leaves,
                        "pending": pending_leaves,
                        "approved": approved_leaves,
                        "rejected": rejected_leaves
                    }
                }
            }
        else:
            # Employee analytics - only their data
            total_reports = db.query(Report).filter(Report.user_id == user_id).count()
            total_tasks = db.query(Task).filter(Task.user_id == user_id).count()
            total_leaves = db.query(Leave).filter(Leave.user_id == user_id).count()
            
            pending_reports = db.query(Report).filter(Report.user_id == user_id, Report.status == "pending").count()
            approved_reports = db.query(Report).filter(Report.user_id == user_id, Report.status == "approved").count()
            rejected_reports = db.query(Report).filter(Report.user_id == user_id, Report.status == "rejected").count()
            
            pending_tasks = db.query(Task).filter(Task.user_id == user_id, Task.status == "pending").count()
            in_progress_tasks = db.query(Task).filter(Task.user_id == user_id, Task.status == "in_progress").count()
            completed_tasks = db.query(Task).filter(Task.user_id == user_id, Task.status == "completed").count()
            
            pending_leaves = db.query(Leave).filter(Leave.user_id == user_id, Leave.status == "pending").count()
            approved_leaves = db.query(Leave).filter(Leave.user_id == user_id, Leave.status == "approved").count()
            rejected_leaves = db.query(Leave).filter(Leave.user_id == user_id, Leave.status == "rejected").count()
            
            return {
                "success": True,
                "data": {
                    "reports": {
                        "total": total_reports,
                        "pending": pending_reports,
                        "approved": approved_reports,
                        "rejected": rejected_reports
                    },
                    "tasks": {
                        "total": total_tasks,
                        "pending": pending_tasks,
                        "in_progress": in_progress_tasks,
                        "completed": completed_tasks
                    },
                    "leaves": {
                        "total": total_leaves,
                        "pending": pending_leaves,
                        "approved": approved_leaves,
                        "rejected": rejected_leaves
                    }
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
