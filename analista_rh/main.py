"""
Horizon ATS — Backend API
=========================
Ponto de entrada da aplicação FastAPI.

Para rodar em desenvolvimento:
    uvicorn main:app --reload

Variáveis de ambiente necessárias (.env):
    OPENAI_API_KEY     — Chave da OpenAI
    API_USERNAME       — Usuário para login (padrão: admin)
    API_PASSWORD       — Senha para login
    JWT_SECRET_KEY     — Chave secreta JWT (mínimo 32 chars)
    JWT_EXPIRE_HOURS   — Validade do token em horas (padrão: 8)
    CORS_ORIGINS       — Origins permitidas, separadas por vírgula
                         (padrão: http://localhost:3000)
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# ──────────────────────────────────────────────
# CONFIGURAÇÃO INICIAL
# ──────────────────────────────────────────────
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# LIFESPAN — VALIDAÇÕES NA INICIALIZAÇÃO
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executado na inicialização e no shutdown do servidor."""
    logger.info("═══════════════════════════════════════")
    logger.info("  Horizon ATS API — Iniciando...")
    logger.info("═══════════════════════════════════════")

    # Importações aqui para evitar import circular na validação
    from auth import validar_config_auth
    from services.ai_service import validar_chaves_ia
    from database import init_db

    try:
        init_db()
        validar_config_auth()
        validar_chaves_ia()
        logger.info("✓ Banco de Dados inicializado")
        logger.info("✓ Configuração de autenticação OK")
        logger.info("✓ Chaves de API OK")
    except RuntimeError as exc:
        logger.critical("✗ ERRO DE CONFIGURAÇÃO:\n%s", exc)
        raise  # Impede o servidor de subir com configuração inválida

    logger.info("✓ Servidor pronto para receber requisições")
    logger.info("═══════════════════════════════════════")
    yield
    logger.info("Horizon ATS API — Encerrando.")


# ──────────────────────────────────────────────
# APLICAÇÃO
# ──────────────────────────────────────────────
app = FastAPI(
    title="Horizon ATS API",
    description=(
        "API de análise de currículos com IA. "
        "Autentique-se via POST /api/v1/auth/login para obter um token JWT."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ──────────────────────────────────────────────
# CORS
# ──────────────────────────────────────────────
_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# RATE LIMITING (slowapi)
# ──────────────────────────────────────────────
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware

    limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    logger.info("✓ Rate limiting ativo (60 req/min global)")
except ImportError:
    logger.warning("slowapi não instalado — rate limiting desativado")


# ──────────────────────────────────────────────
# TRATAMENTO DE ERROS GLOBAL
# ──────────────────────────────────────────────
@app.exception_handler(Exception)
async def handler_erro_generico(request: Request, exc: Exception):
    logger.exception("Erro não tratado em %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"erro": "Erro interno do servidor", "detalhe": "Ocorreu um erro inesperado no processamento da requisição.", "codigo": 500},
    )


# ──────────────────────────────────────────────
# ROUTERS
# ──────────────────────────────────────────────
from auth import realizar_login, realizar_google_login
from models import LoginRequest, GoogleLoginRequest, TokenResponse
from routers.resume import router as resume_router
from routers.analysis import router as analysis_router
from routers.users import router as users_router

# Endpoint de login (sem autenticação prévia, obviamente)
@app.post(
    "/api/v1/auth/login",
    response_model=TokenResponse,
    tags=["Autenticação"],
    summary="Obtém token JWT de acesso",
    description="Informe usuário e senha para receber um Bearer token. Use-o no header `Authorization: Bearer <token>`.",
)
async def login(body: LoginRequest):
    return realizar_login(body)

@app.post(
    "/api/v1/auth/google-login",
    response_model=TokenResponse,
    tags=["Autenticação"],
    summary="Login via Google",
)
async def google_login(body: GoogleLoginRequest):
    return realizar_google_login(body)


# Rotas protegidas
app.include_router(resume_router)
app.include_router(analysis_router)
app.include_router(users_router)


# ──────────────────────────────────────────────
# HEALTH CHECK
# ──────────────────────────────────────────────
@app.get("/health", tags=["Sistema"], summary="Verifica se a API está online")
async def health_check():
    return {"status": "ok", "versao": "2.0.0"}