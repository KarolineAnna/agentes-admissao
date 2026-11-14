"""
Monta e compila o StateGraph com checkpointer SQLite.

Responsabilidades:
- Criar StateGraph com estado do atendimento
- Adicionar nós (CLASSIFICAR, ROTEAR, CONFERIR, REDIGIR, REVISAR, EXECUTAR, CORRIGIR, ESCALAR)
- Adicionar arestas condicionais (add_conditional_edges)
- Configurar checkpointer SQLite (data/grafo.db)
- Compilar grafo com interrupt() para escalações
- Fornecer método para executar grafo com thread_id = id do evento

LangGraph:
- StateGraph: orquestra atendimento de CADA evento ou tarefa de prazo
- add_conditional_edges: roteamento dinâmico
- interrupt(): pausa para escalação ao RH
- Command(resume=...): retoma após decisão
- AsyncSqliteSaver: checkpointer
"""

import logging
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import AsyncSqliteSaver

# TODO: implementar criação do StateGraph
# TODO: implementar adição de nós
# TODO: implementar adição de arestas condicionais
# TODO: implementar configuração do checkpointer
# TODO: implementar compilação do grafo
# TODO: implementar método para executar grafo
