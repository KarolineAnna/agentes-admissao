"""
Memória local em SQLite.

Responsabilidades:
- Guardar estado dos casos (cobranças feitas, propostas, escalações)
- Guardar lições aprendidas
- Guardar histórico de ações por evento
- Guardar respostas do mundo para conferir 504

Tabelas:
- casos: id_admissao, contratado_id, status, data_criacao
- cobranças: id_admissao, area, data_cobranca, tentativas
- propostas: id_admissao, tipo, dados, status (pendente, aprovado, recusado)
- escalações: id_admissao, motivo, data_escalacao, resposta_rh
- ações: evento_id, agente, tarefa, resultado, data
- lições: tema, aprendizado, data
- mensagens_enviadas: evento_id, destinatario, assunto, data (para conferir 504)
"""

import sqlite3
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

# TODO: implementar inicialização do banco (criar tabelas)
# TODO: implementar CRUD para casos
# TODO: implementar CRUD para cobranças
# TODO: implementar CRUD para propostas
# TODO: implementar CRUD para escalações
# TODO: implementar CRUD para ações
# TODO: implementar CRUD para lições
# TODO: implementar CRUD para mensagens_enviadas
# TODO: implementar consultas por id_admissao
