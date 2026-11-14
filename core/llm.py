"""
Chamada ao gpt-4o-mini com schema fixo e contador de custo.

Responsabilidades:
- Chamar OpenAI SDK com modelo gpt-4o-mini
- Temperatura 0.1
- Structured Outputs (response_format com schema estrito)
- Somar `usage` de cada resposta
- Parar se uma rodada passar de US$ 0,50
- Parar se um evento passar de 5 chamadas ao LLM
- Chave em .env (OPENAI_API_KEY), nunca no código

Schemas (pydantic):
- Classificação de evento
- Roteamento (conferente ou comunicador)
- Decisão de aceitação/recusa de documento
- Redação de mensagem
- Revisão de ação crítica
"""

import logging
from typing import Any, Dict, Type, TypeVar
from pydantic import BaseModel

# TODO: implementar cliente OpenAI com SDK oficial
# TODO: implementar Structured Outputs com schema
# TODO: implementar contador de custo (input_tokens, output_tokens)
# TODO: implementar limite de US$ 0,50 por rodada
# TODO: implementar limite de 5 chamadas por evento
# TODO: implementar logging de tokens e custo

T = TypeVar('T', bound=BaseModel)

async def chamar_llm(
    prompt: str,
    schema: Type[T],
    temperatura: float = 0.1,
) -> T:
    """
    Chama gpt-4o-mini com schema fixo.
    
    Args:
        prompt: instrução para o LLM
        schema: classe pydantic para validar resposta
        temperatura: 0.1 por padrão
    
    Returns:
        Instância do schema com resposta validada
    """
    # TODO: implementar
    pass
