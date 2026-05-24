# Horizon ATS: Assistente Inteligente de Currículos

Bem-vindo ao repositório principal do **Horizon ATS**, uma plataforma desenvolvida para analisar, reescrever e otimizar currículos de forma inteligente utilizando as mais recentes ferramentas de Inteligência Artificial (LLMs via OpenAI), garantindo máxima aderência a vagas específicas e superando os sistemas robóticos de rastreamento de candidatos (Applicant Tracking Systems).

## 📄 Documentação Oficial

Para facilitar o entendimento, dividimos nossa documentação em duas frentes:

1. 📘 **[Manual do Usuário](docs/DOC_USUARIO.md)**: Se você quer entender como fazer login no sistema, subir seu currículo em PDF e utilizar o painel de aprovações (Administração B2B).
2. 💻 **[Documentação Técnica](docs/DOC_TECNICA.md)**: Se você é desenvolvedor e deseja entender a arquitetura do projeto (FastAPI, React, SQLite, GPT-4o), configurar as variáveis de ambiente e rodar a aplicação localmente.

---

### Principais Recursos
- **Leitura Automática de PDF:** O sistema extrai e estrutura todos os dados do candidato de forma independente.
- **Avaliação de Duplo Score (Antes/Depois):** Mostra a nota percentual do currículo recebido frente aos requisitos da vaga e a nova nota da versão reescrita.
- **Identificação de Palavras-chave:** Detecção inteligente de Gaps (habilidades ausentes).
- **Geração de PDF Otimizado Nativo:** Baixe um novo arquivo pronto em PDF estruturado com `@react-pdf/renderer`.
- **Modo Escuro (Dark Mode):** Alternância instantânea de tema no painel com salvamento de preferências no cache.
- **Sistema de Login Google OAuth:** Entradas 1-click via Google com controle total do nível de permissões de quem pode ou não executar as IAs.

Desenvolvido para revolucionar a conversão em candidaturas 🚀.
