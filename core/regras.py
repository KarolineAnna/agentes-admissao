"""
Regras fixas em código (não no LLM).

Responsabilidades:
- Roteamento forçado (mudança de data/dado sensível/desistência sempre escalam)
- Validação de documentos (CNH nunca vale como RG)
- Checagem de privacidade (não expor dados sensíveis)
- Checagem de palavras-gatilho (contrato, assinatura, exame em mensagens de ação)
- Validação de destinatário antes de envio
- Regras de negócio (RN-01 a RN-66)

Implementar como funções que retornam bool ou levantam exceção.
"""

import logging
from typing import Dict, List, Optional

# TODO: implementar validação de mudança de data (sempre escala)
# TODO: implementar validação de desistência (sempre escala)
# TODO: implementar validação de dado sensível (sempre escala)
# TODO: implementar validação de CNH como RG (rejeitar)
# TODO: implementar checagem de privacidade
# TODO: implementar checagem de palavras-gatilho em mensagens de ação
# TODO: implementar validação de destinatário
# TODO: implementar mapeamento de regras de negócio (RN-xx)
