"""
Serviço de extração de texto de PDFs.
"""

import io
import logging
import mimetypes
from fastapi import HTTPException, UploadFile

import pdfplumber

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024   # 10 MB
MAX_TEXT_LENGTH = 15_000                  # chars enviados à IA
MIN_TEXT_LENGTH = 50                      # texto mínimo para ser válido


def _validar_arquivo(filename: str, content_type: str, size: int) -> None:
    """Valida tipo MIME e tamanho antes de processar."""
    if size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande. Máximo permitido: {MAX_FILE_SIZE_BYTES // (1024*1024)} MB",
        )

    # Aceita application/pdf e octet-stream (alguns browsers enviam assim)
    tipos_aceitos = {"application/pdf", "application/octet-stream", "binary/octet-stream"}
    extensao = (filename or "").lower().rsplit(".", 1)[-1]

    if content_type not in tipos_aceitos and extensao != "pdf":
        raise HTTPException(
            status_code=415,
            detail="Apenas arquivos PDF são aceitos.",
        )


async def extrair_texto_pdf(file: UploadFile) -> tuple[str, bool]:
    """
    Extrai texto de um PDF enviado via upload.

    Returns:
        (texto_extraido, is_ats_friendly)
        is_ats_friendly = False se alguma página não teve texto extraível (provável imagem).

    Raises:
        HTTPException 400 se o arquivo for ilegível.
        HTTPException 413 se o arquivo for grande demais.
        HTTPException 415 se não for PDF.
    """
    # Lê os bytes e valida
    file_bytes = await file.read()
    _validar_arquivo(file.filename or "", file.content_type or "", len(file_bytes))

    # Validação de Magic Bytes (assinatura PDF)
    if not file_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=415,
            detail="Arquivo inválido. O arquivo não possui a assinatura de um PDF autêntico.",
        )

    extracted_text = ""
    is_ats_friendly = True

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text(layout=True)
                if text:
                    extracted_text += text + "\n\n"
                else:
                    is_ats_friendly = False
                    logger.debug("Página %d sem texto extraível (possível imagem)", i + 1)
    except Exception as exc:
        logger.error("Falha ao processar PDF: %s", exc)
        raise HTTPException(status_code=400, detail=f"Não foi possível ler o PDF: {exc}")

    if len(extracted_text.strip()) < MIN_TEXT_LENGTH:
        raise HTTPException(
            status_code=422,
            detail="PDF ilegível ou em formato de imagem (texto extraído insuficiente).",
        )

    # Limita o texto para não explodir os tokens da IA
    if len(extracted_text) > MAX_TEXT_LENGTH:
        logger.warning(
            "Texto truncado de %d para %d chars", len(extracted_text), MAX_TEXT_LENGTH
        )
        extracted_text = extracted_text[:MAX_TEXT_LENGTH]

    return extracted_text, is_ats_friendly
