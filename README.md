# Time de agentes de Admissão (Hackathon UNIFEI, Tema 2)

**Problema:** a admissão CLT passa por muitas mãos (contratado, TI, equipamentos, clínica, contabilidade, gestor) com prazos curtos em dias úteis. Um documento aceito errado, um contrato não assinado ou um exame não confirmado fazem a pessoa **não começar** no primeiro dia.

## Como rodar

1. Servidor do kit com o tema de admissão:
   - Docker: `$env:TEMA="admissao"; docker compose up --build mundo`
   - ou Python: `python mundo.py --tema admissao`
2. `.env` na raiz com `MCP_URL`, `MODELO`, `LITELLM_URL`, `LITELLM_API_KEY` (igual ao `agente.py`). Sem as chaves do LiteLLM, o time roda só com as regras.
3. Terminal 1: `python admissao.py` (agentes).
4. Terminal 2: `python rh.py` (pessoa do RH decide aprovações e escalações). Também dá para usar `python rh.py --listar` ou `python rh.py --decidir RH-001 --decisao aprovado --nome "Seu Nome"`.

Arquivos gerados: `data/estado.json` (memória do caso), `data/rh.json` (aprovações e escalações), `data/licoes.json` (memória longa, sem dado pessoal), `logs/agentes.log` (uma linha por ação), `docs/ferramentas.json` e `docs/bases.json` (lidos do servidor).

## Os agentes

| Agente | Papel |
| --- | --- |
| **coordenador** | Puxa eventos (`proximo_evento`), classifica (regras por palavras-chave, e o modelo só no que sobra), decide quem cuida, varre prazos, prepara escalações e aprovações para o RH, **revisa** as ações críticas dos outros e devolve para correção. |
| **conferente** | Confere cada documento pela **descrição** contra `documentos_exigidos` (RN-09). Aceita, recusa com motivo ou marca divergência. Grava o estado de cada documento no servidor. |
| **comunicador** | Envia as mensagens de modelo fixo (TI, equipamentos, clínica, contrato, gestor, pedido de documentos) e responde a quem pediu: o que foi feito e o que falta. |

Toda passagem de caso entre agentes vira `registrar_conversa`. Toda chamada leva `agente`, um `motivo` com a regra RN-xx e o `evento_id` quando atende um evento.

## Quem revisa quem

O **coordenador** revisa antes de sair:
- recusas de documento do **conferente** (a recusa precisa citar uma regra real);
- respostas livres e mensagens fora de modelo fixo do **comunicador** (sem CPF, RG, PIS, nascimento ou endereço de outra pessoa; sem palavras-gatilho como contrato, assinar, exame ou pedido de documento, RN-57 a RN-59).

Se a revisão falha, ele registra "Corrigir: erro | correção" e o autor refaz uma vez. Se falhar de novo, o caso vai para o RH.

## Faz sozinho, propõe ou escala

| Nível | Situações | Por quê |
| --- | --- | --- |
| **Faz sozinho** | Acionar TI, equipamentos e clínica; avisar gestor; mandar contrato; pedir e cobrar documentos; aceitar documento claramente válido; recusar CNH no lugar do RG ou comprovante com mais de 90 dias; responder dúvidas do FAQ | Baixo risco, regra clara, e atraso custa o primeiro dia |
| **Propõe ao RH** | Mudança de data de início; comprovante em nome de outra pessoa; remarcar exame de quem faltou | Precisa do OK de uma pessoa (`aprovado_por`). O servidor recusa o nome de um agente |
| **Só escala** | Dado sensível (saúde, laudo, processo); desistência; dúvida fora do FAQ; remetente não identificado; contratado sem resposta há 4 dias úteis; primeiro dia em risco (D-2 sem exame apto ou contrato) | Risco jurídico ou de privacidade, ou decisão que não é do agente |

As propostas trazem situação, o que já foi feito, risco, opções e recomendação (RN-37, RN-51). Os agentes nunca ficam esperando: o laço segue e retoma o caso quando a decisão aparece em `data/rh.json`.

## Métricas de sucesso

- Pessoas prontas no primeiro dia (exame apto e contrato assinado): todas.
- Documentos inválidos aceitos: **0**.
- Dados pessoais vazados: **0**.
- Eventos sem ação: 0 (todo evento recebe resposta ou mensagem com `evento_id`).

## Com mais tempo

- Fase 2: envio à contabilidade pelo portal `/legado` com Playwright (RN-15, RN-32, RN-33).
- Retomar eventos lidos e sem ação depois de uma queda (`listar_eventos`).
- Priorizar a fila (cobranças do mundo e primeiro dia em risco primeiro).
- Usar o modelo para julgar descrições ambíguas de documentos, sempre com revisão.
- Painel web simples para o RH no lugar do terminal.
