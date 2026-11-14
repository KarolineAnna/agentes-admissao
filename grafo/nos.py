"""
Nós do grafo LangGraph.

Nós:
- CLASSIFICAR: chamar LLM para classificar evento
- ROTEAR: chamar LLM para rotear para conferente ou comunicador
- CONFERIR: chamar conferente para conferir documentos
- REDIGIR: chamar comunicador para redigir mensagem
- REVISAR: chamar coordenador para revisar ação crítica
- EXECUTAR: executar ação (enviar mensagem, registrar, atualizar)
- CORRIGIR: corrigir erro (1 vez)
- ESCALAR: escalar ao RH com interrupt()

Cada nó informa qual agente agiu (coordenador, conferente ou comunicador)
no campo `agente` das chamadas MCP.
"""

import logging
from typing import Any, Dict

# TODO: implementar nó CLASSIFICAR
# TODO: implementar nó ROTEAR
# TODO: implementar nó CONFERIR
# TODO: implementar nó REDIGIR
# TODO: implementar nó REVISAR
# TODO: implementar nó EXECUTAR
# TODO: implementar nó CORRIGIR
# TODO: implementar nó ESCALAR
