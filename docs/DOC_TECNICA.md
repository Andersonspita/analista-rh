# 💻 Documentação Técnica: Horizon ATS

Bem-vindo à documentação técnica do **Horizon ATS**. Este documento explica a arquitetura, estrutura do projeto, tecnologias utilizadas e as instruções para rodar o projeto localmente ou em produção.

---

## 1. Arquitetura e Tecnologias

O Horizon ATS é estruturado como uma aplicação Full-Stack contendo serviços apartados:

**Frontend (analista_rh_front)**
- **Tecnologias:** React 18, TypeScript, Vite, CSS Vanilla.
- **Componentes-Chave:** 
  - `@react-oauth/google` para Autenticação via Google e OAuth.
  - `@react-pdf/renderer` para geração dinâmica e em tempo real do novo currículo em PDF na aba do cliente.
  - `lucide-react` para iconografia vetorial.
- **Integração Backend:** Utiliza a biblioteca genérica `api.ts` (baseada em Axios/Fetch) utilizando interceptores para injetar o Bearer Token do JWT no header das chamadas.

**Backend (analista_rh)**
- **Tecnologias:** Python 3, FastAPI, SQLite, Pydantic, Uvicorn.
- **Integrações (LLM):** OpenAI API (`gpt-4o-mini` para análise/parsing estruturado e `gpt-4o` para reconstrução textual/otimizada do currículo).
- **Leitura de Documentos:** `pdfplumber` e `PyPDF2` para extração raw de texto.
- **Autenticação:** JWT (JSON Web Tokens) baseados na spec RFC 7519, `passlib` (para hashes seguros locais, caso necessário no futuro) e validação OAuth2 nativa da biblioteca `google-auth`.

---

## 2. Estrutura de Diretórios

```
analista-rh/
├── analista_rh/                  # Diretório do Backend (FastAPI)
│   ├── env/                      # Ambiente Virtual Python (não versionado)
│   ├── .env                      # Variáveis de ambiente secretas
│   ├── database.sqlite           # Banco de Dados SQLite local
│   ├── main.py                   # Ponto de Entrada / Servidor
│   ├── auth.py                   # Validação Google OAuth, Geração JWT e Middlewares
│   ├── database.py               # Instanciação/Migrações do DB
│   ├── models.py                 # Schemas (Pydantic models) para Validação e IO
│   ├── routers/                  # Controladores de Rotas REST
│   │   ├── users.py              # Operações de CRUD do Perfil e Admin B2B
│   │   ├── resume.py             # Endpoint para conversão de PDF para JSON
│   │   └── analysis.py           # Endpoint para comunicação via IA LLM OpenAI
│   └── services/                 # Regras de Negócio e Helpers
│       ├── ai_service.py         # Abstrações LangChain/OpenAI
│       └── pdf_service.py        # Helpers de extração Textual de PDFs
│
├── analista_rh_front/            # Diretório do Frontend (React)
│   ├── .env                      # Keys públicas da API Vite
│   ├── src/
│   │   ├── components/           # Componentes Modulares (Cards, Buttons, PDF Template)
│   │   ├── contexts/             # Gerenciadores Globais (ThemeContext)
│   │   ├── pages/                # Views de Navegação (Dashboard, Login)
│   │   ├── services/             # Instâncias e Wrappers de API Network
│   │   ├── App.tsx               # Roteador (react-router-dom) e Autenticador
│   │   └── main.tsx              # Provider Global de OAuth e injeção do App React
│   └── public/                   # Assets estáticos (Vetor de Logo Futurista)
```

---

## 3. Fluxo de Autenticação

1. O Cliente clica no componente de `<GoogleLogin>` nativo (fornecido pelo `@react-oauth/google`).
2. Após o fluxo Pop-Up, o navegador recebe a `credential` Token.
3. O frontend envia a `credential` para `/api/v1/auth/google-login` no FastAPI.
4. O Backend usa o `id_token.verify_oauth2_token()` do pacote Oficial da Google para descriptografar e validar as keys públicas do Google em relação ao ClientID do Backend.
5. Se for bem-sucedido, ele extrai o email, verifica o banco de dados. 
   - Se é novo: Cria status `pending`.
6. O Backend gera um `JWT` (JSON Web Token) criptografado por `JWT_SECRET_KEY` contendo as claims e devolve pro frontend.
7. O Frontend utiliza esse token no localStorage para chamadas futuras.

---

## 4. Configuração e Variáveis de Ambiente

Para rodar este projeto em outro ambiente, os arquivos `.env` precisam ser gerados.

**Backend (.env na pasta `/analista_rh`):**
```ini
OPENAI_API_KEY="sk-proj-xxxxx..."
JWT_SECRET_KEY="SUA_CHAVE_SUPER_SECRETA_ALEATORIA"
JWT_EXPIRE_HOURS="8"
CORS_ORIGINS="http://localhost:5173"
GOOGLE_CLIENT_ID="SUA_CHAVE_GOOGLE.apps.googleusercontent.com"
```

**Frontend (.env na pasta `/analista_rh_front`):**
```ini
VITE_GOOGLE_CLIENT_ID="SUA_CHAVE_GOOGLE.apps.googleusercontent.com"
```

---

## 5. Como Iniciar o Projeto Localmente

**Pré-requisitos:**
- Python 3.10 ou superior
- Node.js LTS 18+

### Rodando o Backend
Abra um terminal e execute:
```bash
cd analista_rh
python -m venv env
# No Windows
env\Scripts\activate
# No Linux/Mac
source env/bin/activate

pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.1 --port 8000
```

### Rodando o Frontend
Abra um segundo terminal e execute:
```bash
cd analista_rh_front
npm install
npm run dev
```

O Frontend rodará em `http://localhost:5173` e acessará o backend em `http://localhost:8000`.

---

## 6. Endpoints REST da API (Resumo)

| Método | Endpoint                     | Permissão      | Objetivo |
|--------|------------------------------|----------------|----------|
| POST   | `/api/v1/auth/google-login`  | Público        | Efetuar/Cadastrar e retornar JWT via Auth Token do Google. |
| GET    | `/api/v1/users/me`           | Qualquer Logado| Resgata os dados de perfil, níveis (Admin/User) e status. |
| GET    | `/api/v1/users/admin/list`   | Apenas Admin   | Lista todo o banco de usuários registrados. |
| PUT    | `/api/v1/users/admin/status` | Apenas Admin   | Libera (active) ou bloqueia usuários (blocked/pending). |
| POST   | `/api/v1/parse-resume`       | Apenas 'active'| Recebe um FileUpload PDF e extrai JSON via GPT-4o-Mini. |
| POST   | `/api/v1/analyze-and-rebuild`| Apenas 'active'| Recebe JSON do currículo e texto da vaga. Aplica avaliação dupla ATS e otimização GPT-4o. |
