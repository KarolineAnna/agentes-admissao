"""
TypedDict do estado do atendimento.

Estado compartilhado entre nós do grafo:
- evento: evento atual (id, tipo, origem, dados)
- admissao: dados da admissão (id, contratado_id, status das frentes)
- contratado: dados do contratado (nome, CPF, cargo, etc.)
- acao: ação a executar (tipo, dados, resultado)
- revisao: resultado da revisão (aprovado, motivo, escalacao)
- custo: contador de custo (tokens, rodadas, US$)
- historico: lista de ações executadas

Thread_id = id do evento ou da tarefa.
Checkpointer SQLite salva estado em data/grafo.db.
"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime

# TODO: implementar TypedDict do estado
# TODO: implementar inicialização do estado
# TODO: implementar atualização do estado
