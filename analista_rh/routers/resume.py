"""
Router: Parse Resume
POST /api/v1/parse-resume

Extrai dados estruturados de um currículo em PDF.
Requer autenticação JWT (Bearer token).
"""

import logging
from fastapi import APIRouter, Depends, UploadFile, File

from auth import get_active_user
from models import RespostaParseResume, ErroResposta, MetaResposta
from services.pdf_service import extrair_texto_pdf
from services.ai_service import extrair_curriculo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Currículos"])


@router.post(
    "/parse-resume",
    response_model=RespostaParseResume,
    responses={400: {"model": ErroResposta}, 500: {"model": ErroResposta}},
    summary="Extrai dados estruturados de um PDF de currículo",
    description="Faz o upload de um arquivo PDF, extrai o texto e utiliza IA para devolver um JSON estruturado.",
)
async def parse_resume(
    file: UploadFile = File(..., description="Arquivo PDF do currículo"),
    current_user: str = Depends(get_active_user),
):
    logger.info("parse-resume | usuário: %s | arquivo: %s", current_user, file.filename)

    # 1. Extrai e valida o PDF
    texto_bruto, is_ats_friendly = await extrair_texto_pdf(file)

    # 2. IA estrutura os dados
    dados = extrair_curriculo(texto_bruto)

    return RespostaParseResume(
        is_ats_friendly=is_ats_friendly,
        dados_extraidos=dados,
        meta=MetaResposta(),
    )
