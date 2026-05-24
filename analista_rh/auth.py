"""
Autenticação JWT para o Horizon ATS API.

Fluxo:
    POST /api/v1/auth/login  →  {access_token, token_type, expires_in}
    Todas as demais rotas exigem: Authorization: Bearer <token>

Configuração (.env):
    API_USERNAME=admin
    API_PASSWORD=sua_senha_aqui
    JWT_SECRET_KEY=chave_secreta_aleatoria
    JWT_EXPIRE_HOURS=8
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from models import LoginRequest, TokenResponse
from database import get_db_connection, verify_password

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# CONFIGURAÇÃO
# ──────────────────────────────────────────────
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
ALGORITHM = "HS256"
EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "8"))

API_USERNAME = os.getenv("API_USERNAME", "admin")
API_PASSWORD = os.getenv("API_PASSWORD", "")

# Scheme para extrair o Bearer token do header
bearer_scheme = HTTPBearer(auto_error=False)


# ──────────────────────────────────────────────
# FUNÇÕES INTERNAS
# ──────────────────────────────────────────────
def _verificar_credenciais(username: str, password: str) -> bool:
    """
    Valida username e senha no banco de dados SQLite.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT hashed_password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return False
        return verify_password(password, row["hashed_password"])
    except Exception as e:
        logger.error(f"Erro ao acessar banco de dados no login: {e}")
        return False
    finally:
        conn.close()


def _criar_token(dados: dict, expire_hours: int = EXPIRE_HOURS) -> str:
    payload = dados.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=expire_hours)
    payload.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from models import GoogleLoginRequest

# ──────────────────────────────────────────────
# ENDPOINT DE LOGIN
# ──────────────────────────────────────────────
def realizar_login(body: LoginRequest) -> TokenResponse:
    """Valida credenciais e retorna JWT."""
    if not _verificar_credenciais(body.username, body.password):
        logger.warning("Tentativa de login inválida para usuário '%s'", body.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = _criar_token({"sub": body.username})
    expire_seconds = EXPIRE_HOURS * 3600
    logger.info("Login bem-sucedido: '%s'", body.username)
    return TokenResponse(access_token=token, expires_in=expire_seconds)


def realizar_google_login(body: GoogleLoginRequest) -> TokenResponse:
    """Verifica token do Google, cria usuário se não existir e retorna JWT do sistema."""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=500, detail="Google Client ID não configurado no backend.")

    try:
        # Validate Google token
        idinfo = id_token.verify_oauth2_token(body.credential, google_requests.Request(), client_id)
        email = idinfo['email']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT username, role, status FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            # Register new user from Google
            # We use email as username
            cursor.execute(
                "INSERT INTO users (username, hashed_password, email, role, status) VALUES (?, ?, ?, 'user', 'pending')",
                (email, "[OAUTH_GOOGLE]", email)
            )
            conn.commit()
            username = email
            status_user = 'pending'
        else:
            username = user['username']
            status_user = user['status']
            
        conn.close()
        
        token = _criar_token({"sub": username})
        expire_seconds = EXPIRE_HOURS * 3600
        logger.info("Google Login bem-sucedido: '%s' (Status: %s)", username, status_user)
        return TokenResponse(access_token=token, expires_in=expire_seconds)

    except ValueError as e:
        logger.warning(f"Google token inválido: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token do Google inválido")
    except Exception as e:
        logger.error(f"Erro no login do Google: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno")


# ──────────────────────────────────────────────
# DEPENDENCY — PROTEGE AS ROTAS
# ──────────────────────────────────────────────
def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """
    Dependency do FastAPI. Injete em qualquer rota que exija autenticação.
    Retorna o username do token ou lança 401.
    """
    credenciais_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido, expirado ou ausente. Faça login em /api/v1/auth/login",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credenciais_exception

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credenciais_exception
    except JWTError:
        raise credenciais_exception

    return username


def get_active_user(current_user: str = Depends(get_current_user)) -> str:
    """Verifica se o usuário está ativo no banco de dados."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM users WHERE username = ?", (current_user,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Usuário não encontrado.")
            
        status_user = row["status"]
        if status_user == "pending":
            raise HTTPException(status_code=403, detail="Sua conta está aguardando aprovação do administrador.")
        elif status_user == "blocked":
            raise HTTPException(status_code=403, detail="Sua conta foi bloqueada.")
    finally:
        conn.close()

    return current_user


def get_current_admin(current_user: str = Depends(get_current_user)) -> str:
    """Dependency para rotas restritas a administradores."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ?", (current_user,))
        row = cursor.fetchone()
        if not row or row["role"] != "admin":
            raise HTTPException(status_code=403, detail="Acesso negado. Requer privilégios de administrador.")
    finally:
        conn.close()
    return current_user


# ──────────────────────────────────────────────
# VALIDAÇÃO NA INICIALIZAÇÃO
# ──────────────────────────────────────────────
def validar_config_auth() -> None:
    """Garante que as variáveis de autenticação estão configuradas."""
    erros = []
    if not SECRET_KEY or len(SECRET_KEY) < 32:
        erros.append("JWT_SECRET_KEY ausente ou muito curta (mínimo 32 caracteres)")
    if erros:
        raise RuntimeError(
            "Configuração de autenticação inválida:\n" + "\n".join(f"  • {e}" for e in erros)
        )
