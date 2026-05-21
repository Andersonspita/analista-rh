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
