"""
AirfareX India — User Account & Profile Router
Handles client configuration, profile inspection, and profile updates.
Enforces zero-trust: uses get_current_user dependency.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from backend.database import get_db_connection
from backend.auth import AuthUser, get_current_user
from backend.supabase_client import SUPABASE_URL, SUPABASE_ANON_KEY

router = APIRouter(prefix="/auth", tags=["Authentication & User Accounts"])

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    gstin: Optional[str] = None
    company_name: Optional[str] = None

class ProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    gstin: Optional[str] = None
    company_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@router.get("/config")
def get_auth_config():
    """
    Returns public Supabase configuration for client-side authentication.
    CRITICAL SECURITY: NEVER exposes SUPABASE_SERVICE_ROLE_KEY.
    """
    return {
        "supabase_url": SUPABASE_URL,
        "supabase_anon_key": SUPABASE_ANON_KEY,
        "configured": bool(SUPABASE_URL and SUPABASE_ANON_KEY and len(SUPABASE_ANON_KEY) > 10)
    }

@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(current_user: AuthUser = Depends(get_current_user)):
    """
    Protected: Returns the authenticated user's profile.
    Strict ownership: Derived directly from verified JWT user ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE id = ?", (current_user.id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return ProfileResponse(
            id=row["id"],
            email=row["email"],
            full_name=row["full_name"],
            phone=row["phone"],
            gstin=row["gstin"],
            company_name=row["company_name"],
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"])
        )

    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone
    )

@router.put("/profile", response_model=ProfileResponse)
async def update_my_profile(
    req: ProfileUpdateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Protected: Updates the authenticated user's travel profile.
    Strict ownership: Only updates profile matching current_user.id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM profiles WHERE id = ?", (current_user.id,))
    existing = cursor.fetchone()

    new_name = req.full_name.strip() if req.full_name else (existing["full_name"] if existing else current_user.full_name)
    new_phone = req.phone.strip() if req.phone is not None else (existing["phone"] if existing else current_user.phone)
    new_gstin = req.gstin.strip().upper() if req.gstin is not None else (existing["gstin"] if existing else None)
    new_company = req.company_name.strip() if req.company_name is not None else (existing["company_name"] if existing else None)

    cursor.execute("""
        INSERT INTO profiles (id, email, full_name, phone, gstin, company_name, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            full_name = excluded.full_name,
            phone = excluded.phone,
            gstin = excluded.gstin,
            company_name = excluded.company_name,
            updated_at = CURRENT_TIMESTAMP
    """, (current_user.id, current_user.email, new_name, new_phone, new_gstin, new_company))
    conn.commit()

    cursor.execute("SELECT * FROM profiles WHERE id = ?", (current_user.id,))
    updated_row = cursor.fetchone()
    conn.close()

    return ProfileResponse(
        id=updated_row["id"],
        email=updated_row["email"],
        full_name=updated_row["full_name"],
        phone=updated_row["phone"],
        gstin=updated_row["gstin"],
        company_name=updated_row["company_name"],
        created_at=str(updated_row["created_at"]),
        updated_at=str(updated_row["updated_at"])
    )

@router.post("/sync-session")
async def sync_session(current_user: AuthUser = Depends(get_current_user)):
    """Idempotently syncs an active authenticated session into the local profiles table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO profiles (id, email, full_name, phone, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            email = excluded.email,
            full_name = excluded.full_name,
            updated_at = CURRENT_TIMESTAMP
    """, (current_user.id, current_user.email, current_user.full_name, current_user.phone))
    conn.commit()
    conn.close()
    return {"status": "synced", "user_id": current_user.id, "email": current_user.email}
