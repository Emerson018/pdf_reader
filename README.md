# AI Agent Platform (ai-platform)

Plataforma modular e extensível para desenvolvimento e orquestração de **Agentes de IA**, com suporte a múltiplos provedores de modelos, banco relacional com vetorização (`pgvector`), armazenamento em cache e objetos (`Redis`/`MinIO`), e camada de automação integrada ao `n8n`.

---

## 🏗 Arquitetura Conceitual

```text
                        ┌────────────────────┐
                        │        APP         │
                        │ Next.js / React    │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │      API           │
                        │      FastAPI       │
                        └─────────┬──────────┘
                                  │
                                  ▼
                     ┌────────────────────────┐
                     │      ORCHESTRATOR      │
                     │       LangGraph        │
                     └───────────┬────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             │                   │                   │
             ▼                   ▼                   ▼
          MODELS               TOOLS               DATA
             │                   │                   │
             │                   │                   │
          LLMs                  MCP              PostgreSQL
          Embeddings            APIs             pgvector
          Ollama                n8n              Redis
             │                                      MinIO
             │
             ▼
       External Models
```

---

## ⚡ Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript, TailwindCSS
- **Backend API**: FastAPI, Python 3.11, Pydantic, SQLAlchemy 2.0 (Async)
- **IA & Orquestração**: LangGraph, ModelProvider Abstraction (`OpenAIProvider`, `OllamaProvider`)
- **Data & Storage**: PostgreSQL (com extensão `pgvector`), Redis 7, MinIO S3 Object Storage
- **Automação**: n8n (Integração assíncrona por Webhooks via `N8NClient`)
- **Infraestrutura & DevOps**: Docker, Docker Compose, GitHub Actions CI/CD

---

## 🚀 Como Executar

### 1. Clonar o repositório e configurar variáveis de ambiente

```bash
cp .env.example .env
```

### 2. Subir os serviços com Docker Compose

```bash
docker compose up --build
```

Acesse os serviços locais:
- 💻 **Chat Web App**: [http://localhost:3000](http://localhost:3000)
- ⚙️ **API REST / Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 🗄️ **MinIO Console**: [http://localhost:9001](http://localhost:9001)
- 🔄 **n8n Automation**: [http://localhost:5678](http://localhost:5678)

---

## 📁 Estrutura do Diretório

```text
ai-platform/
├── apps/
│   ├── frontend/             # Next.js Chat Web UI
│   └── api/                  # FastAPI Web Server & Endpoints
├── services/
│   ├── orchestrator/         # LangGraph Orchestration Engine & Supervisor Router
│   ├── agents/               # Specialized AI Agents (Research, Data, Automation)
│   ├── models/               # Model Provider Abstraction (OpenAI, Ollama)
│   └── tools/                # Extensible Tools (DatabaseTool, N8NTool, MCPTool)
├── infrastructure/
│   ├── postgres/             # Database initialization script (pgvector)
│   ├── redis/
│   └── minio/
├── docs/                     # Comprehensive Architecture & Component Documentation
├── .github/workflows/        # GitHub Actions CI/CD Workflow
├── docker-compose.yml
└── README.md
```

---

## 📚 Documentação Técnica

- 🏛 [Arquitetura Detalhada](docs/architecture.md)
- 🤖 [Guia de Agentes](docs/agents.md)
- 🛠 [Guia de Ferramentas (Tools & MCP)](docs/tools.md)
- 🔄 [Integração n8n](docs/n8n.md)
- 💻 [Desenvolvimento Local & Testes](docs/development.md)

---

## 🧪 Testes

Para rodar os testes automatizados da suíte backend:

```bash
python -m pytest apps/api/tests
```
