from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class GoogleLoginRequest(BaseModel):
    credential: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


# ──────────────────────────────────────────────
# PERFIL DE USUÁRIO
# ──────────────────────────────────────────────
class UserProfile(BaseModel):
    username: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    role: str = "user"
    status: str = "pending"

class UserUpdate(BaseModel):
    email: Optional[str] = None
    telefone: Optional[str] = None
    nova_senha: Optional[str] = None

# ──────────────────────────────────────────────
# CURRÍCULO — ENTRADA
# ──────────────────────────────────────────────
class FormacaoAcademica(BaseModel):
    curso: str
    instituicao: str
    periodo: str

class CursoCertificacao(BaseModel):
    nome: str
    instituicao: str
    periodo: Optional[str] = None

class ExperienciaProfissional(BaseModel):
    cargo: str
    empresa: str
    periodo: str
    descricao: str

class CurriculoEstruturado(BaseModel):
    nome_completo: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    links: List[str] = Field(default_factory=list)
    habilidades_tecnicas: List[str] = Field(default_factory=list)
    experiencias: List[ExperienciaProfissional] = Field(default_factory=list)
    formacao_academica: List[FormacaoAcademica] = Field(default_factory=list)
    cursos_certificacoes: List[CursoCertificacao] = Field(default_factory=list)
    resumo_profissional: str


# ──────────────────────────────────────────────
# ANÁLISE ATS
# ──────────────────────────────────────────────
class AnaliseATS(BaseModel):
    score_compatibilidade: int = Field(
        description="Nota de 0 a 100 baseada na compatibilidade com a vaga"
    )
    palavras_chave_encontradas: List[str]
    palavras_chave_faltando: List[str]
    dicas_melhoria: List[str] = Field(
        description="Ações concretas que o candidato deve tomar"
    )


# ──────────────────────────────────────────────
# CURRÍCULO OTIMIZADO — SAÍDA ESTRUTURADA
# ──────────────────────────────────────────────
class ExperienciaOtimizada(BaseModel):
    cargo: str
    empresa: str
    periodo: str
    descricao: str = Field(
        description="Descrição reescrita com palavras-chave da vaga, SEM inventar fatos"
    )


class CurriculoOtimizado(BaseModel):
    nome_completo: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    links: List[str] = Field(default_factory=list)
    habilidades_tecnicas: List[str] = Field(default_factory=list)
    formacao_academica: List[FormacaoAcademica] = Field(default_factory=list)
    cursos_certificacoes: List[CursoCertificacao] = Field(default_factory=list)
    resumo_profissional: str = Field(
        description="Resumo profissional reescrito e otimizado para a vaga"
    )
    experiencias: List[ExperienciaOtimizada] = Field(
        description="Lista de experiências com descrições otimizadas"
    )


# ──────────────────────────────────────────────
# RESPOSTAS DA API
# ──────────────────────────────────────────────
class MetaResposta(BaseModel):
    modelo_extracao: str = "gpt-4o-mini"
    modelo_score: str = "gpt-4o-mini"
    modelo_reescrita: str = "gpt-4o"
    processado_em: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class RespostaParseResume(BaseModel):
    is_ats_friendly: bool
    dados_extraidos: CurriculoEstruturado
    meta: MetaResposta


class RespostaAnalise(BaseModel):
    analise_ats: AnaliseATS
    curriculo_otimizado: CurriculoOtimizado
    analise_ats_otimizada: AnaliseATS
    meta: MetaResposta


class ErroResposta(BaseModel):
    erro: str
    detalhe: Optional[str] = None
    codigo: int
