import os
import logging

logger = logging.getLogger(__name__)

DEFAULT_RULES = """=== REGRAS ESTREITAS E OBRIGATÓRIAS DE RESPOSTA DA IA ===
1. BASE EXCLUSIVA DE CONHECIMENTO: Responder APENAS com base nos documentos e informações do banco de dados local (tabela 'document_chunks').
2. PROIBIÇÃO DE CONHECIMENTO EXTERNO: Não responder com conhecimento genérico externo da API ou da web.
3. OBJETIVIDADE E SÍNTESE: Evitar gerar muito texto para a resposta. Seja objetivo, direto e sintético.
4. SEM TEXTOS GENÉRICOS OU PROLIXOS: Evite colocar textos genéricos, introduções desnecessárias ou enrolações.
5. AUSÊNCIA DE DADOS NO BANCO: Quando não encontrar o conteúdo no banco de dados referente à pergunta, retornar explicitamente que não há nenhum dado no banco de dados referente à pergunta.
"""


def load_system_rules() -> str:
    """Reads system_rules.txt dynamically from disk on each request."""
    possible_paths = [
        os.path.join(os.getcwd(), "apps", "api", "app", "core", "system_rules.txt"),
        os.path.join(os.getcwd(), "services", "core", "system_rules.txt"),
        os.path.join(os.path.dirname(__file__), "system_rules.txt"),
    ]

    for p in possible_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        return content
            except Exception as e:
                logger.error(f"Error reading system_rules.txt from {p}: {e}")

    return DEFAULT_RULES
