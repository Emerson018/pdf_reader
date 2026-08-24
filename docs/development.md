# Guia de Desenvolvimento Local

## 1. Requisitos

- Python 3.11+
- Node.js 18+ / 20+
- Docker & Docker Compose

## 2. Configuração de Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Ajuste a chave da OpenAI em `OPENAI_API_KEY` (se desejar testar chamadas reais à OpenAI, caso contrário o sistema atua em modo mock gracioso).

## 3. Execução via Docker Compose

Para subir toda a infraestrutura e microsserviços:

```bash
docker compose up --build
```

Serviços disponibilizados:
- **Frontend (Next.js)**: http://localhost:3000
- **API (FastAPI)**: http://localhost:8000 (Swagger docs em http://localhost:8000/docs)
- **PostgreSQL (pgvector)**: localhost:5432
- **Redis**: localhost:6379
- **MinIO Console**: http://localhost:9001 (minioadmin / minioadmin)
- **n8n (Existente)**: http://localhost:5678

## 4. Execução de Testes Automatizados

```bash
python -m pytest apps/api/tests
```
