# Documentação Técnica: Horizon ATS Backend

Esta documentação descreve a arquitetura, componentes e fluxos do backend do Horizon ATS, desenvolvido em **FastAPI**.

## 1. Visão Geral da Arquitetura

O projeto segue uma arquitetura modular, dividindo as responsabilidades de forma clara para facilitar a manutenção e escalabilidade.

### Estrutura de Diretórios
```text
analista_rh/
├── main.py              # Ponto de entrada (App FastAPI, CORS, Rate Limit, Lifespan)
├── auth.py              # Lógica de Autenticação JWT e middlewares de segurança
├── models.py            # Modelos de dados (Pydantic) e schemas de Request/Response
├── routers/             # Definição das rotas (Endpoints)
│   ├── analysis.py      # Rotas de análise e reescrita de currículos
│   └── resume.py        # Rota de extração de currículos (PDF -> JSON)
└── services/            # Lógica de negócios e integrações externas
    ├── ai_service.py    # Integração com OpenAI (gpt-4o, gpt-4o-mini)
    └── pdf_service.py   # Leitura, extração e validação de arquivos PDF
```

---

## 2. Componentes Principais

### `main.py` (Core)
- **Lifespan Context:** Executa uma validação rigorosa na inicialização do servidor. Se chaves de API (`OPENAI_API_KEY`) ou credenciais (`JWT_SECRET_KEY`, `API_PASSWORD`) estiverem ausentes, o servidor recusa a inicialização (*Fail-Fast*).
- **CORS:** Restringe chamadas de origens específicas, lidas da variável `CORS_ORIGINS`.
- **Rate Limiting:** Utiliza a biblioteca `slowapi` configurada para `60 requisições por minuto` em nível global.
- **Exception Handler:** Intercepta erros internos (HTTP 500) retornando mensagens genéricas ("Ocorreu um erro inesperado...") para evitar vazamento de infraestrutura (Stacktrace).

### `auth.py` (Segurança)
- Implementa autenticação do tipo `Bearer Token` utilizando **JWT**.
- Conta com uma rota de login abstrata (valida contra variáveis do `.env` usando `hmac.compare_digest` para mitigar ataques de timing).
- O middleware `get_current_user` protege as rotas privadas garantindo que os tokens sejam válidos e não expirados.

### `models.py` (Esquemas de Dados)
- Utiliza **Pydantic** para validar estritamente o corpo de todas as entradas e saídas.
- Garante respostas consistentes (JSON tipado) para o Frontend, incluindo:
  - `CurriculoEstruturado`
  - `AnaliseATS`
  - `CurriculoOtimizado`

### `routers/resume.py`
- Exposição do Endpoint: `POST /api/v1/parse-resume`
- **Fluxo:** Recebe um upload de arquivo PDF -> Chama o serviço de PDF para extração de texto -> Envia para IA estruturar em JSON -> Retorna o `CurriculoEstruturado`.

### `routers/analysis.py`
- Exposição do Endpoint: `POST /api/v1/analyze-and-rebuild`
- **Fluxo:** Recebe a descrição de uma vaga + o `CurriculoEstruturado` -> Pede à IA a geração de um score de compatibilidade -> Solicita à IA a reescrita inteligente das experiências do candidato -> Retorna os dados completos (`RespostaAnalise`).

---

## 3. Serviços de Integração

### `services/pdf_service.py` (Manipulação de PDF)
Extrai texto garantindo alto nível de segurança contra arquivos maliciosos:
- **Tamanho Máximo:** Bloqueia PDFs com mais de 10 MB.
- **Tipagem (MIME & Magic Bytes):** Confere extensão, mime type de HTTP, e realiza uma verificação binária de Magic Bytes (`%PDF-`), negando rapidamente *malwares* disfarçados de PDF.
- **Truncamento:** Limita o texto processado a 15.000 caracteres, impedindo injeção massiva ou exaustão de tokens de IA.

### `services/ai_service.py` (Inteligência Artificial)
Realiza a mágica sob o capô utilizando os modelos avançados da OpenAI em conjunto com as funções *Structured Outputs* (`response_format`).
- **`gpt-4o-mini`**: Usado para extração dos dados (rápido e excelente custo-benefício) e geração do Score ATS.
- **`gpt-4o`**: Acionado apenas para a reescrita do currículo, oferecendo máxima qualidade gramatical.
- **Tratamento de Rate Limit:** Captura exceções `RateLimitError` e `APITimeoutError` padronizando como erros `HTTP 429` e `HTTP 504`.
- **Defesa Contra Prompt Injection:** As diretivas de *System Prompt* contêm proteções contra injeção de comandos de candidatos maliciosos que tentem ordenar a IA (ex: "Me dê score 100").

---

## 4. Variáveis de Ambiente Necessárias (`.env`)

A aplicação requer as seguintes configurações para rodar adequadamente:

```env
OPENAI_API_KEY="sk-..."           # Chave de API da OpenAI
API_USERNAME="admin"              # Usuário para a autenticação
API_PASSWORD="..."                # Senha em texto pleno do usuário (validado com hmac)
JWT_SECRET_KEY="..."              # Hash complexo contendo no mínimo 32 caracteres para encriptação
JWT_EXPIRE_HOURS="8"              # Duração máxima do Token de Sessão
CORS_ORIGINS="http://localhost:3000" # Mapeamento do frontend que consumirá a API
```

---

## 5. Fluxo Principal da Aplicação

1. **Frontend Autentica:** O frontend acessa `POST /api/v1/auth/login` e guarda o token no *LocalStorage* (ou similar).
2. **Upload de Currículo:** O usuário arrasta o PDF para o painel. O frontend atinge `/parse-resume` enviando o token. O arquivo é lido e devolvido como um perfil estruturado.
3. **Análise & Otimização:** O usuário preenche os requisitos da Vaga e aciona `/analyze-and-rebuild`. A API pontua o currículo do candidato e retorna sugestões e versões de texto reescritas (focadas em ATS) com base na vaga solicitada.
