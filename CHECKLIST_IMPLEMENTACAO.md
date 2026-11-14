# Checklist de Implementação

## Fase 1: Core (Fundação)

### core/mcp_cliente.py
- [ ] Classe MCPClient com httpx ou requests
- [ ] Método para proximo_evento(esperar_segundos)
- [ ] Método para listar_eventos(status)
- [ ] Método para responder_evento(evento_id, resposta, agente, motivo)
- [ ] Método para enviar_mensagem(destinatario, assunto, corpo, agente, motivo, evento_id?, vai_responder?)
- [ ] Método para registrar(base, dados, agente, motivo, evento_id?)
- [ ] Método para atualizar(base, id, dados, agente, motivo, evento_id?)
- [ ] Método para consultar(base, filtro?, busca?, limite?, offset?)
- [ ] Método para listar_bases()
- [ ] Método para tela(tipo, dados, agente, motivo, evento_id?)
- [ ] Retry com backoff exponencial (2, 4, 8 s, máx. 4)
- [ ] Tratamento de 503, 504, 409, 400, 404, 405, 422, 410
- [ ] Timeout de 15s
- [ ] Logging de todas as chamadas
- [ ] Validação de respostas JSON

### core/llm.py
- [ ] Classe LLMClient com OpenAI SDK
- [ ] Método chamar_llm(prompt, schema, temperatura=0.1)
- [ ] Structured Outputs com response_format
- [ ] Contador de tokens (input_tokens, output_tokens)
- [ ] Cálculo de custo (input: $0.15/1M, output: $0.60/1M)
- [ ] Limite de US$ 0,50 por rodada
- [ ] Limite de 5 chamadas por evento
- [ ] Logging de tokens e custo
- [ ] Tratamento de erros da OpenAI

### core/memoria.py
- [ ] Inicialização do banco SQLite (data/memoria.db)
- [ ] Tabela casos (id_admissao, contratado_id, status, data_criacao)
- [ ] Tabela cobranças (id_admissao, area, data_cobranca, tentativas)
- [ ] Tabela propostas (id_admissao, tipo, dados, status)
- [ ] Tabela escalações (id_admissao, motivo, data_escalacao, resposta_rh)
- [ ] Tabela ações (evento_id, agente, tarefa, resultado, data)
- [ ] Tabela lições (tema, aprendizado, data)
- [ ] Tabela mensagens_enviadas (evento_id, destinatario, assunto, data)
- [ ] CRUD para cada tabela
- [ ] Consultas por id_admissao
- [ ] Transações e rollback

### core/prazos.py
- [ ] Função is_dia_util(data)
- [ ] Função proximo_dia_util(data)
- [ ] Função dias_uteis_entre(data1, data2)
- [ ] Função varrer_prazos(agora)
- [ ] Função disparar_cobranca(id_admissao, area, agora)
- [ ] Sincronização com relógio do servidor (campo `agora`)
- [ ] Prazos: TI 2 dias, Equipamentos 2 dias, Clínica 2 dias, Contrato 1 dia, Exame 1 dia, Documento 3 dias

### core/regras.py
- [ ] Função validar_mudanca_data(dados) → escala sempre
- [ ] Função validar_desistencia(dados) → escala sempre
- [ ] Função validar_dado_sensivel(dados) → escala sempre
- [ ] Função validar_cnh_como_rg(documento) → rejeita
- [ ] Função validar_privacidade(mensagem) → bloqueia dados sensíveis
- [ ] Função validar_palavras_gatilho(mensagem) → bloqueia contrato, assinatura, exame
- [ ] Função validar_destinatario(destinatario) → verifica existência
- [ ] Mapeamento de regras de negócio (RN-xx)

### core/schemas.py
- [ ] ClassificacaoEvento (tipo, prioridade, motivo)
- [ ] RoteamentoEvento (agente, tarefa)
- [ ] DecisaoDocumento (aceito, motivo, aprovado_por?)
- [ ] RedacaoMensagem (destinatario, assunto, corpo)
- [ ] RevisaoAcaoCritica (aprovado, motivo, escalacao?)
- [ ] Validação de schemas com Pydantic

## Fase 2: Grafo (Orquestração)

### grafo/estado.py
- [ ] TypedDict AtendimentoEstado
- [ ] Campos: evento, admissao, contratado, acao, revisao, custo, historico
- [ ] Inicialização do estado
- [ ] Atualização do estado

### grafo/nos.py
- [ ] Nó CLASSIFICAR (chamar LLM para classificar evento)
- [ ] Nó ROTEAR (chamar LLM para rotear para conferente ou comunicador)
- [ ] Nó CONFERIR (chamar conferente para conferir documentos)
- [ ] Nó REDIGIR (chamar comunicador para redigir mensagem)
- [ ] Nó REVISAR (chamar coordenador para revisar ação crítica)
- [ ] Nó EXECUTAR (executar ação: enviar mensagem, registrar, atualizar)
- [ ] Nó CORRIGIR (corrigir erro, 1 vez)
- [ ] Nó ESCALAR (escalar ao RH com interrupt())
- [ ] Cada nó informa qual agente agiu (coordenador, conferente, comunicador)

### grafo/grafo.py
- [ ] Criar StateGraph com AtendimentoEstado
- [ ] Adicionar nós ao grafo
- [ ] Adicionar arestas condicionais (add_conditional_edges)
- [ ] Configurar checkpointer SQLite (data/grafo.db)
- [ ] Compilar grafo com interrupt()
- [ ] Método para executar grafo com thread_id = id do evento
- [ ] Método para retomar grafo após decisão (resume)

## Fase 3: Agentes

### agentes/coordenador.py
- [ ] Laço de proximo_evento(esperar_segundos=8)
- [ ] Classificação de eventos
- [ ] Roteamento para conferente ou comunicador
- [ ] Revisão de ações críticas
- [ ] Escalação ao RH com interrupt()
- [ ] Varredura de prazos
- [ ] Disparo de cobranças
- [ ] Retomada de eventos não atendidos (listar_eventos status=lido)
- [ ] Tratamento de respostas do mundo (responde_a)

### agentes/conferente.py
- [ ] Conferência de documentos contra regras
- [ ] Validação de estados: recebido, aceito, aceito com ressalva, recusado
- [ ] Montagem do pacote da contabilidade (nome, CPF, nascimento, cargo, PIS)
- [ ] Envio pelo portal (Playwright)
- [ ] Chamada ao LLM para decisões com schema fixo
- [ ] Validação de CNH como RG (rejeitar)
- [ ] Validação de motivo para recusado
- [ ] Validação de aprovado_por para aceito com ressalva

### agentes/comunicador.py
- [ ] Redação de mensagens para contratados
- [ ] Redação de mensagens para áreas
- [ ] Redação de mensagens para gestores
- [ ] Uso de modelos fixos para ações (prompts/modelos_mensagem.md)
- [ ] Redação de respostas livres (FAQ, gestor)
- [ ] Checagem de privacidade em código
- [ ] Checagem de palavras-gatilho em código
- [ ] Verificação de destinatário antes de envio
- [ ] Validação de duas mensagens ao mesmo contratado (>= 1 hora)

## Fase 4: Portal e Painel

### portal/contabilidade.py
- [ ] Montagem do pacote a partir da ficha do contratado
- [ ] Campos: quem envia, admissão, nome, CPF, nascimento (DD/MM/AAAA), cargo, início (DD/MM/AAAA), PIS
- [ ] Cópia de máscara de CPF, RG, PIS (com X)
- [ ] Autenticação no portal
- [ ] Preenchimento de formulário com Playwright
- [ ] Envio do pacote
- [ ] Confirmação de envio

### painel/app.py
- [ ] Interface Streamlit
- [ ] Exibição de propostas pendentes
- [ ] Exibição de escalações pendentes
- [ ] Aprovação ou recusa com motivo
- [ ] Retorno de decisão ao grafo (resume)
- [ ] Exibição de histórico de ações
- [ ] Autenticação básica

## Fase 5: Integração

### main.py
- [ ] Carregamento de .env
- [ ] Inicialização de MCPClient
- [ ] Inicialização de Memoria
- [ ] Inicialização de Grafo
- [ ] Inicialização de LLMClient
- [ ] Inicialização de Prazos
- [ ] Inicialização de Regras
- [ ] Laço de proximo_evento no coordenador
- [ ] Inicialização de painel Streamlit em thread separada
- [ ] Tratamento de sinais (Ctrl+C)

### prompts/
- [ ] Copiar prompts de docs/prompts_agentes.md
- [ ] Criar modelos_mensagem.md com templates fixos
- [ ] Criar prompts para cada tarefa (CLASSIFICAR, ROTEAR, CONFERIR, REDIGIR, REVISAR)

## Fase 6: Testes e Validação

- [ ] Testes unitários para core/
- [ ] Testes de integração para grafo/
- [ ] Testes de ponta a ponta para agentes/
- [ ] Validação de limites de custo
- [ ] Validação de retry com backoff
- [ ] Validação de checkpointer SQLite
- [ ] Validação de interrupt() e resume()
- [ ] Validação de Playwright
- [ ] Validação de Streamlit

## Notas

- Implementar em ordem: core → grafo → agentes → portal/painel → main → testes
- Cada arquivo tem TODOs marcando o que precisa ser feito
- Seguir regras obrigatórias do código (ver .github/copilot-instructions.md)
- Testar com servidor MCP em http://localhost:8765/mcp
- Usar dados de referência em docs/ (bases.json, contratados.json, etc.)
