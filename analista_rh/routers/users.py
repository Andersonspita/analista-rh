import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from auth import get_current_user, get_current_admin
from models import UserProfile, UserUpdate
from database import get_db_connection, get_password_hash

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["Usuários"])

@router.get("/me", response_model=UserProfile, summary="Consulta o perfil logado")
async def get_my_profile(current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, telefone, role, status FROM users WHERE username = ?", (current_user,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        return UserProfile(
            username=row["username"], 
            email=row["email"], 
            telefone=row["telefone"],
            role=row["role"],
            status=row["status"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar perfil: {e}")
        raise HTTPException(status_code=500, detail="Erro ao consultar perfil.")
    finally:
        conn.close()

# ──────────────────────────────────────────────
# ROTAS DE ADMINISTRAÇÃO
# ──────────────────────────────────────────────
@router.get("/admin/list", summary="Lista todos os usuários (Apenas Admin)")
async def list_users(admin_user: str = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, role, status FROM users ORDER BY status DESC")
        rows = cursor.fetchall()
        return [{"username": r["username"], "email": r["email"], "role": r["role"], "status": r["status"]} for r in rows]
    finally:
        conn.close()

class StatusUpdate(BaseModel):
    status: str

@router.put("/admin/status/{username}", summary="Atualiza o status de um usuário (Apenas Admin)")
async def update_user_status(username: str, data: StatusUpdate, admin_user: str = Depends(get_current_admin)):
    if data.status not in ["active", "pending", "blocked"]:
        raise HTTPException(status_code=400, detail="Status inválido")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET status = ? WHERE username = ?", (data.status, username))
        conn.commit()
        return {"msg": f"Status de {username} alterado para {data.status}"}
    finally:
        conn.close()

@router.put("/me", response_model=UserProfile, summary="Atualiza o perfil logado")
async def update_my_profile(data: UserUpdate, current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Updates parciais baseados no body
        if data.email is not None:
            cursor.execute("UPDATE users SET email = ? WHERE username = ?", (data.email, current_user))
        if data.telefone is not None:
            cursor.execute("UPDATE users SET telefone = ? WHERE username = ?", (data.telefone, current_user))
        if data.nova_senha:
            hashed = get_password_hash(data.nova_senha)
            cursor.execute("UPDATE users SET hashed_password = ? WHERE username = ?", (hashed, current_user))
            
        conn.commit()
        
        # Retorna atualizado
        cursor.execute("SELECT username, email, telefone FROM users WHERE username = ?", (current_user,))
        row = cursor.fetchone()
        return UserProfile(username=row["username"], email=row["email"], telefone=row["telefone"])
        
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar perfil.")
    finally:
        conn.close()
