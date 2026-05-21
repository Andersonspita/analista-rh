"""
Router: Parse Resume
POST /api/v1/parse-resume

Extrai dados estruturados de um currículo em PDF.
Requer autenticação JWT (Bearer token).
"""

import logging
from fastapi import APIRouter, Depends, UploadFile, File

from auth import get_current_user
from models import RespostaParseResume, MetaResposta
from services.pdf_service import extrair_texto_pdf
from services.ai_service import extrair_curriculo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Currículo"])


@router.post(
    "/parse-resume",
    response_model=RespostaParseResume,
    summary="Extrai dados de um currículo PDF",
    description=(
        "Recebe um arquivo PDF, extrai o texto e usa IA para estruturar "
        "os dados do candidato em JSON. Requer autenticação."
    ),
)
async def parse_resume(
    file: UploadFile = File(..., description="Arquivo PDF do currículo"),
    current_user: str = Depends(get_current_user),
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
