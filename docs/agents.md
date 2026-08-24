# Guia de Agentes de IA

## 1. Conceito e Estrutura

Todos os agentes herdam da classe abstrata `BaseAgent` localizada em `services/agents/base/base_agent.py`.

```python
class BaseAgent(ABC):
    name: str
    description: str
    provider: ModelProvider
    tools: Dict[str, BaseTool]

    async def run(self, user_message: str, history: Optional[List[LLMMessage]]) -> AgentResponse:
        ...
```

## 2. Agentes Disponíveis

- **ResearchAgent**: Agente especialista em síntese, pesquisa e geração de respostas explicativas.
- **DataAgent**: Agente integrado à `DatabaseTool`, responsável por consultas relacionais e análise de dados.
- **AutomationAgent**: Agente integrado à `N8NTool`, responsável por acionar workflows de automação no n8n.

## 3. Como Adicionar um Novo Agente

Para adicionar um novo agente à plataforma:

1. Crie o diretório do novo agente em `services/agents/<nome_do_agente>/`.
2. Herde de `BaseAgent` e defina `system_prompt` e ferramentas associadas.
3. Registre o novo agente no `SupervisorRouter` em `services/orchestrator/routing/supervisor.py` e no grafo LangGraph em `services/orchestrator/graphs/agent_graph.py`.
