from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models_mysql.leave import Leave, LeaveCreate, LeaveUpdate
from models_mysql.user import User
from utils.mysql_db import get_db
from utils.auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/leaves")
def create_leave(leave: LeaveCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user_id = int(current_user.get("user_id"))
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_leave = Leave(
            user_id=user_id,
            user_name=user.full_name,
            user_email=user.email,
            leave_type=leave.leave_type,
            half_day_type=leave.half_day_type,
            reason=leave.reason,
            start_date=datetime.fromisoformat(leave.start_date).date(),
            end_date=datetime.fromisoformat(leave.end_date).date() if leave.end_date else None,
            voice_note_url=leave.voice_note_url,
            attachment_url=leave.attachment_url,
            status="pending"
        )
        
        db.add(db_leave)
        db.commit()
        db.refresh(db_leave)
        
        return {
            "success": True,
            "message": "Leave request submitted successfully",
            "data": {"leave_id": db_leave.id}
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaves")
def get_leaves(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user_id = int(current_user.get("user_id"))
        user_role = current_user.get("role")
        
        if user_role == "admin":
            leaves = db.query(Leave).order_by(desc(Leave.created_at)).all()
        else:
            leaves = db.query(Leave).filter(Leave.user_id == user_id).order_by(desc(Leave.created_at)).all()
        
        leaves_list = []
        for leave in leaves:
            leaves_list.append({
                "_id": str(leave.id),
                "user_id": str(leave.user_id),
                "user_name": leave.user_name,
                "user_email": leave.user_email,
                "leave_type": leave.leave_type,
                "half_day_type": leave.half_day_type,
                "reason": leave.reason,
                "start_date": leave.start_date.isoformat() if leave.start_date else None,
                "end_date": leave.end_date.isoformat() if leave.end_date else None,
                "status": leave.status.value if hasattr(leave.status, 'value') else leave.status,
                "admin_comment": leave.admin_comment,
                "created_at": leave.created_at.isoformat() if leave.created_at else None
            })
        
        return {
            "success": True,
            "data": {"leaves": leaves_list}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaves/my")
def get_my_leaves(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user_id = int(current_user.get("user_id"))
        
        leaves = db.query(Leave).filter(Leave.user_id == user_id).order_by(desc(Leave.created_at)).all()
        
        leaves_list = []
        for leave in leaves:
            leaves_list.append({
                "_id": str(leave.id),
                "user_id": str(leave.user_id),
                "user_name": leave.user_name,
                "user_email": leave.user_email,
                "leave_type": leave.leave_type,
                "half_day_type": leave.half_day_type,
                "reason": leave.reason,
                "start_date": leave.start_date.isoformat() if leave.start_date else None,
                "end_date": leave.end_date.isoformat() if leave.end_date else None,
                "status": leave.status.value if hasattr leave.status, 'value') else leave.status,
                "admin_comment": leave.admin_comment,
                "created_at": leave.created_at.isoformat() if leave.created_at else None
            })
        
        return {
            "success": True,
            "data": {"leaves": leaves_list}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/leaves/{leave_id}")
def update_leave(leave_id: int, leave_update: LeaveUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        
        if not leave:
            raise HTTPException(status_code=404, detail="Leave not found")
        
        if leave_update.status:
            leave.status = leave_update.status
        if leave_update.admin_comment:
            leave.admin_comment = leave_update.admin_comment
        
        db.commit()
        
        return {
            "success": True,
            "message": "Leave updated successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaves/stats/summary")
def get_leave_stats(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user_role = current_user.get("role")
        
        if user_role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        total_leaves = db.query(Leave).count()
        pending_leaves = db.query(Leave).filter(Leave.status == "pending").count()
        approved_leaves = db.query(Leave).filter(Leave.status == "approved").count()
        rejected_leaves = db.query(Leave).filter(Leave.status == "rejected").count()
        
        return {
            "success": True,
            "data": {
                "total": total_leaves,
                "pending": pending_leaves,
                "approved": approved_leaves,
                "rejected": rejected_leaves
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
