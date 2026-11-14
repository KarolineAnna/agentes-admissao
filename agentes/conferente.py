"""
Agente Conferente.

Responsabilidades:
- Conferir documentos contra regras (RN-06, RN-11, RN-12)
- Validar estados de documentos: recebido, aceito, aceito com ressalva, recusado
- Montar pacote da contabilidade a partir da ficha do contratado
- Disparar envio pelo portal (Playwright)
- Chamar LLM para decisões de aceitação/recusa com schema fixo

Regras fixas em código:
- CNH nunca vale como RG (RN-04)
- Recusado exige motivo
- Aceito com ressalva exige aprovado_por
"""

# TODO: implementar conferência de documentos
# TODO: implementar validação de estados
# TODO: implementar montagem do pacote da contabilidade
# TODO: implementar envio pelo portal (Playwright)
# TODO: implementar chamada ao LLM para decisões
