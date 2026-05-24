"""
Router: Analyze and Rebuild
POST /api/v1/analyze-and-rebuild

Compara currículo com vaga, gera score ATS e reescreve o currículo.
Retorna JSON totalmente estruturado (sem Markdown cru).
Requer autenticação JWT.
"""

import logging
from fastapi import APIRouter, Depends, Body

from auth import get_active_user
from models import (
    CurriculoEstruturado,
    RespostaAnalise,
    MetaResposta,
)
from services.ai_service import gerar_score_ats, reescrever_curriculo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Análise ATS"])


@router.post(
    "/analyze-and-rebuild",
    response_model=RespostaAnalise,
    summary="Analisa compatibilidade e reescreve currículo",
    description=(
        "Recebe o JSON do currículo (retornado por /parse-resume) e a descrição da vaga. "
        "Retorna: score de compatibilidade, mapa de palavras-chave, e currículo reescrito "
        "em formato JSON estruturado. Requer autenticação."
    ),
)
async def analyze_and_rebuild(
    vaga: str = Body(..., embed=True, description="Texto completo da descrição da vaga"),
    curriculo: CurriculoEstruturado = Body(..., description="JSON retornado pelo /parse-resume"),
    current_user: str = Depends(get_active_user),
):
    logger.info(
        "analyze-and-rebuild | usuário: %s | candidato: %s",
        current_user,
        curriculo.nome_completo,
    )

    # 1. Score ATS (gpt-4o-mini — rápido e barato)
    analise = gerar_score_ats(curriculo, vaga)

    # 2. Reescrita estruturada (gpt-4o — qualidade máxima, sem Markdown)
    curriculo_otimizado = reescrever_curriculo(curriculo, analise, vaga)

    # 3. Score ATS do Currículo Otimizado (Prova de Valor)
    analise_otimizada = gerar_score_ats(curriculo_otimizado, vaga)

    return RespostaAnalise(
        analise_ats=analise,
        curriculo_otimizado=curriculo_otimizado,
        analise_ats_otimizada=analise_otimizada,
        meta=MetaResposta(),
    )
