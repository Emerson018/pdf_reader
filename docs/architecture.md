# Arquitetura da Plataforma de Agentes de IA (`ai-platform`)

## 1. Visão Geral

A **AI Agent Platform** é uma plataforma de inteligência artificial modular, extensível e orientada a serviços projetada com baixo acoplamento e separação estrita de responsabilidades.

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

## 2. Princípios de Design

1. **Simple First → Modular → Production Ready**: O sistema evolui de uma versão funcional mínima até um orquestrador multi-agente distribuído.
2. **Provider Agnostic**: Camada de abstração `ModelProvider` permite trocar entre OpenAI, Ollama ou provedores locais/em nuvem sem alterar os agentes.
3. **Orquestração Desacoplada**: A lógica dos agentes (`services/orchestrator` / `services/agents`) é 100% independente da camada web HTTP (`FastAPI`).
4. **Automation Layer (n8n)**: O n8n é tratado como camada de integração externa para workflows, acessado via webhooks resilientes pelo `N8NClient`.

## 3. Fluxo de Execução de Mensagem

```text
Next.js Frontend (Chat UI)
       │ (POST /api/v1/chat)
       ▼
FastAPI API (Router & Controllers)
       │
       ▼
ChatService & OrchestratorService
       │
       ▼
LangGraph Orchestration Engine
       ├─► Supervisor Router (Intent Classification)
       ├─► ResearchAgent / DataAgent / AutomationAgent
       └─► BaseTool Execution (PostgreSQL / n8n / MCP)
       │
       ▼
Database Persistence (PostgreSQL: conversations, messages, agent_runs)
       │
       ▼
JSON Response -> Frontend UI
```
