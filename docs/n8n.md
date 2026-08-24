# Integração com n8n (Automation Layer)

## 1. Diretriz de Integração

O container n8n é tratado estritamente como **Camada de Integração / Automação Externa** (`Automation / Integration Layer`), e não como o núcleo de raciocínio LLM dos agentes.

## 2. Arquitetura da Chamada

```text
Agent (AutomationAgent)
  ↓
N8NTool
  ↓
N8NClient (httpx assíncrono)
  ↓
n8n Webhook (http://localhost:5678/webhook/...)
  ↓
n8n Workflow
  ↓
Resposta Estruturada
```

## 3. Resiliência e Tratamento de Erros

O `N8NClient` implementa:
- Timeout configurável (default 30.0s).
- Tratamento de status de erro HTTP (ex: 4xx, 5xx).
- Fallback em caso de indisponibilidade momentânea do webhook para garantir estabilidade da execução dos agentes.
