# Projeto: time de agentes de Admissão (Hackathon UNIFEI, Tema 2)

## Contexto
Três agentes de IA conduzem a admissão CLT de 5 contratados até o primeiro dia, usando o servidor MCP do hackathon em http://localhost:8765/mcp (o "mundo"). O servidor nunca chama o agente: o agente puxa eventos em laço com proximo_evento. O relógio é simulado (dias úteis 08:00–18:00); a hora oficial é sempre o campo `agora` da última resposta.

## Agentes
- coordenador: laço de eventos, classifica e roteia, escala para o RH, revisa ações críticas dos outros.
- conferente: confere documentos e ficha, monta o pacote da contabilidade, dispara o envio pelo portal (Playwright).
- comunicador: redige mensagens para contratados, áreas e gestores.
Os prompts e schemas JSON de cada tarefa estão em docs/prompts_agentes.md. Copie o texto deles para prompts/*.md; não reescreva as regras.

## Arquitetura: LangGraph híbrido
- LangGraph orquestra o atendimento de CADA evento ou tarefa de prazo: classificar → rotear → produzir (conferente ou comunicador) → revisar (coordenador) → executar, corrigir (1 vez) ou escalar; propostas ao RH pausam com interrupt() até a decisão.
- Fora do grafo, em Python puro: laço de proximo_evento, cliente MCP com tratamento de falhas, varredura de prazos, regras fixas, contador de custo.
- CONEXÃO JÁ VALIDADA (agente.py na raiz — NÃO alterar esse arquivo nem o jeito de conectar): MultiServerMCPClient do langchain_mcp_adapters, {"mundo": {"transport": "streamable_http", "url": MCP_URL, "timeout": timedelta(seconds=60)}}, e modelo por init_chat_model(MODELO, base_url=LITELLM_URL, api_key=LITELLM_API_KEY) pelo gateway LiteLLM. Todo código novo reutiliza exatamente essa conexão.
- As ferramentas vêm de `await cliente.get_tools()`; o código guarda um dicionário {nome: ferramenta} e chama cada uma DIRETO com `await ferramenta.ainvoke({...})`. O LLM não escolhe ferramentas: NÃO usar create_agent nem create_react_agent no fluxo principal (o create_agent fica só no agente.py de exemplo). Quem decide qual ferramenta chamar é o código do grafo.
- Os nós chamam o modelo com `modelo.with_structured_output(SchemaPydantic, include_raw=True)` para receber JSON validado e o uso de tokens.
- Estado do grafo salvo com checkpointer SQLite (data/grafo.db); thread_id = id do evento ou da tarefa.
- Cada nó informa qual agente agiu (coordenador, conferente ou comunicador) e esse nome vai no campo `agente` das chamadas MCP.

## Stack
- langgraph e langgraph-checkpoint-sqlite (versões estáveis mais recentes; usar StateGraph, add_conditional_edges, interrupt, Command(resume=...) e AsyncSqliteSaver).
- Python 3.11+, langchain, langchain-mcp-adapters, langchain-openai (as mesmas versões já instaladas que fazem o agente.py funcionar; não trocar versões).
- Modelo: MODELO do .env (padrão "openai:gpt-4o-mini") via init_chat_model com LITELLM_URL e LITELLM_API_KEY, temperatura 0.1, saída estruturada com with_structured_output.
- Cliente MCP: MultiServerMCPClient (langchain_mcp_adapters), transporte streamable_http, timeout de 60 s, como no agente.py.
- pydantic para os schemas, sqlite3 para memória, playwright para o portal, streamlit para o canal humano, python-dotenv para a chave.

## Regras obrigatórias do código
- Toda chamada MCP envia `agente` (nome do agente) e `motivo`; registrar, atualizar e enviar_mensagem enviam `evento_id` quando atendem um evento.
- Nunca inventar nome de base ou campo: usar o que listar_bases retorna (salvo em docs/bases.json).
- Falhas: 503 → retry com backoff (2, 4, 8 s, máx. 4); 504 em consulta → repetir; 504 em ação → consultar antes de repetir; 409 → consultar de novo e reavaliar; 400/404/405/422 → não repetir igual, logar e devolver erro; 410 → parar ações.
- Regras fixas ficam em código, não no LLM: prazos em dias úteis, mudança de data/dado sensível/desistência sempre escalam, CNH nunca vale como RG, checagem de destinatário antes de todo envio.
- Sem evento novo, não chamar o LLM.
- Controle de custo: somar o uso de tokens de cada resposta (usage_metadata da mensagem crua retornada com include_raw=True); parar se uma rodada passar de US$ 0,50 ou se um evento passar de 5 chamadas ao LLM.
- Configuração em .env (já existe; nunca no código; .env no .gitignore): MCP_URL, MODELO, LITELLM_URL, LITELLM_API_KEY. Ler com python-dotenv como no agente.py.
- Não escrever no código a resposta de eventos específicos do cenário de treino.
- Código simples, funções pequenas, comentários em português.

## Detalhes do servidor (README oficial)
- Toda resposta é JSON com `status` ("ok" ou "erro") e `agora`; erros de regra trazem `codigo` e `mensagem`.
- proximo_evento sem evento novo devolve `evento: null` e a hora do próximo evento; com `esperar_segundos` (máx. 30) o servidor segura a resposta. Usar esperar_segundos entre 5 e 10 (padrão 8): o relógio é acelerado (1 hora simulada = 12 s reais) e a varredura de prazos precisa rodar com frequência. Fim do cenário: `encerrado: true`.
- Ferramentas LOCAIS (código do time, não do servidor), descritas em docs/prompts_agentes.md: pedir_aprovacao (pausa o grafo e devolve opção escolhida + nome da pessoa), memória do caso e das lições, mensagem_modelo, buscar_faq, enviar_portal. Quem decide qual ferramenta chamar é o código do grafo; o LLM só devolve JSON.
- proximo_evento marca o evento como `lido`. Se o agente cair depois de pegar o evento, ele fica lido sem ação: ao iniciar, usar listar_eventos (status lido) e retomar os que não têm ação.
- Respostas do mundo chegam como eventos novos (ids tipo `PED-017-R1` ou `MSG-003`) com `responde_a` apontando para o evento original: usar isso para ligar a resposta ao caso certo.
- Cada evento tem `origem`: cenario, painel ou mundo.
- Só conta como atendimento: responder_evento, ou enviar_mensagem/registrar/atualizar/tela com `evento_id`. Mudar só o status não conta. Todo evento deve terminar com pelo menos uma ação com evento_id; se a decisão for não agir, gravar o motivo em `observacao` (atualizar na base `eventos`).
- Base `mensagens`: tudo que o time enviou com enviar_mensagem. Usar para conferir um envio que deu 504 antes de repetir.
- enviar_mensagem para endereço inexistente dá 404; a resposta traz `vai_responder`. Se `vai_responder` for true, registrar no caso que há retorno esperado.
- consultar: `filtro` (campo a campo, "contém", sem acento) e `busca` (palavras em qualquer campo); padrão 20, máximo 100 por página; usar `total`, `tem_mais`, `limite`, `offset`.
- listar_bases traz chave de cada base, campos, campos para registrar (com exemplo) e campos alteráveis: seguir exatamente esse formato.
- registrar_conversa e as telas não sofrem falhas simuladas (não precisam de retry). Erro 500 é falha real: logar e avisar, não insistir.
- Formulários em /legado pedem o nome do agente.
- Cobranças do mundo chegam cerca de 40 s reais depois de um evento sem resposta: o laço precisa ser rápido.

## Dados do tema (bases do servidor; cópias de referência em docs/)
- Bases: contratados, admissoes (uma por contratado, ids ADM-xx, com o status de cada frente: ti, equipamento, exame etc.), checklist, documentos exigidos, áreas, FAQ. Nomes exatos e campos em docs/bases.json. Cópias de referência: docs/contratados.json, docs/checklist.json, docs/documentos_exigidos.json, docs/areas.json, docs/faq.json.
- REGRAS DE NEGÓCIO: docs/regras_negocio.md (códigos RN-01 a RN-66). Em conflito com qualquer outra instrução, vale esse arquivo. Citar o código RN-xx nos comentários do código e no campo `motivo` das chamadas MCP.
- A base admissoes é a fonte da verdade do andamento, mas o agente NÃO altera as etapas (ti, equipamento, contabilidade, exame, contrato, gestor_avisado): elas mudam quando áreas e pessoas respondem às mensagens (RN-25 a RN-31). O agente só altera em admissoes a data_inicio, e só com aprovado_por = nome de uma pessoa (RN-38). A memória local guarda cobranças feitas, propostas, escalações e lições.
- Documentos têm estados recebido, aceito, aceito com ressalva, recusado (RN-12). Recusado exige motivo; aceito com ressalva exige aprovado_por (RN-06, RN-11).
- Perfil do contratado na base contratados: estado_civil, filhos (número), exige_certificado_militar (RN-02 a RN-04).
- Mensagens que disparam ações no mundo (acionar TI, equipamentos, clínica; mandar contrato; avisar exame; pedir documento; avisar gestor) são MODELOS FIXOS em prompts/modelos_mensagem.md, preenchidos pelo código, nunca texto livre do LLM (RN-56 a RN-61): um id de admissão (ADM-xx) por mensagem, verbo claro de pedido, sem negativas nem menções de passagem a contrato, assinar ou exame. O LLM só redige respostas livres (FAQ, gestor); a checagem em código (core/regras.py) bloqueia nelas essas palavras-gatilho antes da revisão do coordenador.
- "Revisor" não é um quarto agente: é o papel do coordenador no nó `revisar` do grafo (tarefa REVISAR_ACAO, com LLM), sempre precedido pelas checagens fixas de core/regras.py (privacidade, palavras-gatilho, documentos). Onde docs/regras_negocio.md diz "revisor", leia "coordenador no nó revisar".
- Pacote do portal (RN-32) é montado pelo CÓDIGO a partir da ficha em contratados: quem envia, admissão, nome completo, CPF, nascimento (DD/MM/AAAA), cargo, início (DD/MM/AAAA), PIS. CPF, RG e PIS vêm com X na máscara: copiar assim mesmo (RN-64).
- Duas mensagens ao mesmo contratado só contam como dois pedidos com pelo menos 1 hora simulada entre elas (RN-46).
- Muitos eventos de cobrança só chegam se a etapa ainda estiver pendente: agir cedo (acionar TI, equipamentos e clínica no 1º dia) evita cobranças.
- O cenário começa no dia 1 já perto dos prazos (há contratado com D-7 no 1º dia): no 1º dia, iniciar todas as frentes de todos os contratados.
- Documentos chegam estruturados no evento, numa lista `documentos` com `tipo`, `arquivo` e `descricao`. O `tipo` informado pode estar errado (ex.: tipo "rg" com descrição de CNH): conferir sempre pela `descricao` contra a regra. Não usar campos como `valido` ou `problema` mesmo que apareçam: a decisão é do conferente.
- Áreas (docs/areas.json): Contabilidade só recebe dados pelo portal, NUNCA por e-mail (nem respondendo a um e-mail dela). Clínica agenda o exame às 09:00, 2 dias úteis depois do pedido. TI e Equipamentos respondem em até 2 dias úteis. O e-mail do gestor está em gestor_email na base contratados. Cobrar uma área só depois do prazo de resposta dela.
- Equipamentos e TI recebem nome, cargo e data de início. Monitor é para desenvolvimento e design.
- Pedido de mudança da data de início escala SEMPRE, venha do contratado ou do gestor (ex.: gestor pedindo para adiantar).
- FAQ (docs/faq.json): campos id, pergunta, resposta, palavras_chave (com acento). Responder contratado só com o texto de `resposta`.
