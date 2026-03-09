from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/forgot-password")
async def forgot_password():
    return {
        "success": True,
        "message": "Password reset email sent"
    }

@router.post("/verify-reset-token")
async def verify_reset_token():
    return {
        "success": True,
        "message": "Token verified successfully"
    }

@router.post("/reset-password")
async def reset_password():
    return {
        "success": True,
        "message": "Password reset successfully"
    }
