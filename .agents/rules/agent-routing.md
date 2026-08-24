# Agent Routing Rules

## Available Agents & When to Use Each

Este projeto possui **11 agentes especializados**. O orquestrador deve selecionar o agente
com base no domínio da tarefa conforme a tabela abaixo.

## Tabela de Roteamento

| Intenção / Domínio | Agente | Skill Path |
|---|---|---|
| Frontend, React, Next.js, CSS, UI, UX, componentes, interface | `frontend_developer_agent` | `.agents/skills/frontend-developer/` |
| Backend, API, REST, GraphQL, microsserviços, servidor, arquitetura de sistema | `backend_architect_agent` | `.agents/skills/backend-architect/` |
| Índices, EXPLAIN ANALYZE, tuning SQL, schema de banco, pgbouncer | `database_optimizer_agent` | `.agents/skills/database-optimizer/` |
| Prompt, system prompt, few-shot, chain-of-thought, prompt engineering | `prompt_engineer_agent` | `.agents/skills/prompt-engineer/` |
| RAG, embedding, chunking, HNSW, busca híbrida, rerank, RAGAS, vetor | `rag_engineer_agent` | `.agents/skills/rag-pipeline-engineer/` |
| Revisão de código, code review, refatorar, bug, vulnerabilidade, PR | `code_reviewer_agent` | `.agents/skills/code-reviewer/` |
| Manual do colaborador, política, diretriz, férias, benefícios, regulamento | `document_agent` | `.agents/skills/document-agent/` |
| Dados, SQL, tabela, relatório, métrica, análise de dados | `data_agent` | `.agents/skills/data-agent/` |
| Automação, n8n, workflow, webhook, disparar processo | `automation_agent` | `.agents/skills/automation-agent/` |
| Pesquisa, buscar, artigo, resumo, explicar, comparar tecnologias | `research_agent` | `.agents/skills/research-agent/` |
| Git, branch, commit, PR, merge, rebase, conflito, versionamento | `git_workflow_master` | `.agents/skills/git-workflow-master/` |

## Regras de Roteamento

1. **Especialista primeiro** — Sempre prefira o agente especialista ao `llm_direct`
2. **Contexto prevalece** — Se a pergunta mistura domínios, escolha o agente do domínio primário
3. **Fallback** — Se nenhum agente especialista se aplica, use resposta direta do LLM (`llm_direct`)
4. **Skill antes de responder** — Antes de responder em sua role, leia seu `SKILL.md` correspondente para carregar contexto completo

## Como o Orquestrador Deve Carregar Cada Agente

Ao rotear para um agente, o orquestrador deve:

1. Identificar o agente pelo domínio da mensagem (tabela acima)
2. O agente Python correspondente em `services/agents/` é instanciado
3. O `system_prompt` do agente Python deve refletir a missão definida no `SKILL.md`
4. O agente executa com suas ferramentas específicas (ex: `DocumentSearchTool`, `N8NTool`, `DatabaseTool`)

## Estrutura de Arquivos de Referência

```
.agents/
├── rules/
│   ├── agent-routing.md          ← Este arquivo
│   └── git-workflow.md           ← Regras de Git para o time
└── skills/
    ├── automation-agent/SKILL.md
    ├── backend-architect/SKILL.md
    ├── code-reviewer/SKILL.md
    ├── data-agent/SKILL.md
    ├── database-optimizer/SKILL.md
    ├── document-agent/SKILL.md
    ├── frontend-developer/SKILL.md
    ├── git-workflow-master/SKILL.md
    ├── prompt-engineer/SKILL.md
    ├── rag-pipeline-engineer/SKILL.md
    └── research-agent/SKILL.md

services/agents/              ← Código Python de produção (não mover)
├── automation/automation_agent.py
├── backend/backend_architect_agent.py
├── coding/code_reviewer_agent.py
├── data/data_agent.py
├── database/database_optimizer_agent.py
├── document/document_agent.py
├── frontend/frontend_developer_agent.py
├── prompt/prompt_engineer_agent.py
├── rag/rag_engineer_agent.py
└── research/research_agent.py
```
