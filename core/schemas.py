"""
Modelos pydantic das saídas do LLM.

Schemas para Structured Outputs:
- ClassificacaoEvento: tipo, prioridade, motivo
- RoteamentoEvento: agente (conferente ou comunicador), tarefa
- DecisaoDocumento: aceito (bool), motivo, aprovado_por?
- RedacaoMensagem: destinatario, assunto, corpo
- RevisaoAcaoCritica: aprovado (bool), motivo, escalacao?
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal

# TODO: implementar ClassificacaoEvento
# TODO: implementar RoteamentoEvento
# TODO: implementar DecisaoDocumento
# TODO: implementar RedacaoMensagem
# TODO: implementar RevisaoAcaoCritica
# TODO: implementar validação de schemas
