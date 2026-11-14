"""
Agente Comunicador.

Responsabilidades:
- Redige mensagens para contratados, áreas e gestores
- Usa modelos fixos para ações (acionar TI, equipamentos, clínica, contrato, exame, documento)
- Redige respostas livres (FAQ, gestor)
- Checagem de privacidade e palavras-gatilho em código antes da revisão
- Verifica destinatário antes de todo envio

Regras fixas em código:
- Mensagens de ação usam modelos fixos em prompts/modelos_mensagem.md
- Um id de admissão (ADM-xx) por mensagem
- Sem negativas nem menções de passagem a contrato, assinatura ou exame
- Duas mensagens ao mesmo contratado contam como dois pedidos com >= 1 hora entre elas (RN-46)
- Checagem de privacidade e palavras-gatilho antes da revisão do coordenador
"""

# TODO: implementar redação de mensagens para contratados
# TODO: implementar redação de mensagens para áreas
# TODO: implementar redação de mensagens para gestores
# TODO: implementar checagem de privacidade
# TODO: implementar checagem de palavras-gatilho
# TODO: implementar verificação de destinatário
