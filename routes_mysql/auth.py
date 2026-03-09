from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models_mysql.user import User, UserCreate, UserLogin, UserResponse, UserRole, UserStatus
from utils.auth import get_password_hash, verify_password, create_access_token
from utils.mysql_db import get_db
from datetime import datetime

router = APIRouter()

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        db_user = User(
            full_name=user.full_name,
            email=user.email,
            password=get_password_hash(user.password),
            role=UserRole(user.role),  # Convert string to enum
            status=UserStatus.active
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {
            "success": True,
            "message": "User created successfully",
            "data": {
                "user_id": db_user.id
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Signup Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        # Find user by email
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = create_access_token(
            data={
                "user_id": str(user.id),
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else user.role
            }
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "token": access_token,
                "user": {
                    "_id": str(user.id),
                    "full_name": user.full_name,
                    "email": user.email,
                    "role": user.role.value if hasattr(user.role, 'value') else user.role,
                    "status": user.status.value if hasattr(user.status, 'value') else user.status
                }
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Login Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/me")
def get_current_user_info():
    try:
        return {
            "success": True,
            "data": {
                "message": "User info endpoint"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
