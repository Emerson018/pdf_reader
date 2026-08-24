# Arquitetura de Ferramentas (Tools)

## 1. Visão Geral

Todas as ferramentas seguem a especificação de interface `BaseTool` em `services/tools/base/base_tool.py`:

- **Nome** (`name`): Identificador único da ferramenta.
- **Descrição** (`description`): Explicação do objetivo da ferramenta.
- **Schema de Entrada** (`args_schema`): Classe Pydantic para validação.
- **Execução** (`_run`): Método assíncrono.
- **Retorno Estruturado** (`ToolResult`): Objeto contendo `success`, `data`, `error` e `metadata`.

## 2. Ferramentas Implementadas

1. **`DatabaseTool`** (`services/tools/database/database_tool.py`): Executa consultas estruturadas e busca no banco PostgreSQL.
2. **`N8NTool`** (`services/tools/n8n/n8n_tool.py`): Aciona webhooks e fluxos de trabalho no container n8n.
3. **`MCPTool`** (`services/tools/mcp/mcp_tool.py`): Base para comunicação com servidores Model Context Protocol.

## 3. Como Adicionar uma Nova Tool

1. Crie um novo módulo em `services/tools/<modulo>/`.
2. Defina o schema de entrada usando `Pydantic`.
3. Herde de `BaseTool` e implemente o método assíncrono `_run`.
4. Exporte a nova tool em `services/tools/__init__.py`.
