# Prompts para o GitHub Copilot — Agentes de Admissão

## Antes de começar

1. Crie o repositório e copie para ele o arquivo `prompts_admissao_3_agentes_gpt4omini.md`, salvo como `docs/prompts_agentes.md`.
2. Crie o arquivo `.github/copilot-instructions.md` com o conteúdo da seção 0 abaixo. O Copilot lê esse arquivo sozinho em todo pedido, então não precisa repetir o contexto.
3. Use o **Copilot Chat em modo Agent** e envie os prompts **um por vez, na ordem**. Teste cada etapa antes de seguir.
4. Modelo no Copilot: **Haiku 4.5** por padrão; troque para **Sonnet 5** nas etapas marcadas com ⚙️.
5. Deixe abertos só os arquivos da etapa (contexto menor, custo menor).
6. **Dois ambientes virtuais separados:** um para o servidor (usa `mcp` 2.x) e outro para os agentes. Se alguma biblioteca de agente pedir `mcp` 1.x, ela fica só no ambiente dos agentes.
7. Durante o desenvolvimento, suba o servidor com o relógio mais lento: `SEGUNDOS_POR_DIA=600` (no padrão, um dia do Tema 2 passa em 2 minutos e uma hora simulada em 12 segundos).

---

## 0. `.github/copilot-instructions.md`

```markdown
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
- Os nós chamam o gpt-4o-mini direto pelo SDK da OpenAI com schema fixo. NÃO usar LangChain agents, create_react_agent, tool calling automático nem adaptadores MCP do LangChain: o código decide qual ferramenta MCP chamar.
- Estado do grafo salvo com checkpointer SQLite (data/grafo.db); thread_id = id do evento ou da tarefa.
- Cada nó informa qual agente agiu (coordenador, conferente ou comunicador) e esse nome vai no campo `agente` das chamadas MCP.

## Stack
- langgraph e langgraph-checkpoint-sqlite (versões estáveis mais recentes; usar StateGraph, add_conditional_edges, interrupt, Command(resume=...) e AsyncSqliteSaver).
- Python 3.11+, OpenAI Python SDK, modelo gpt-4o-mini, temperatura 0.1, Structured Outputs (response_format com schema estrito).
- Cliente MCP: pacote oficial `mcp` (streamable HTTP), timeout de 15 s ou mais.
- pydantic para os schemas, sqlite3 para memória, playwright para o portal, streamlit para o canal humano, python-dotenv para a chave.

## Regras obrigatórias do código
- Toda chamada MCP envia `agente` (nome do agente) e `motivo`; registrar, atualizar e enviar_mensagem enviam `evento_id` quando atendem um evento.
- Nunca inventar nome de base ou campo: usar o que listar_bases retorna (salvo em docs/bases.json).
- Falhas: 503 → retry com backoff (2, 4, 8 s, máx. 4); 504 em consulta → repetir; 504 em ação → consultar antes de repetir; 409 → consultar de novo e reavaliar; 400/404/405/422 → não repetir igual, logar e devolver erro; 410 → parar ações.
- Regras fixas ficam em código, não no LLM: prazos em dias úteis, mudança de data/dado sensível/desistência sempre escalam, CNH nunca vale como RG, checagem de destinatário antes de todo envio.
- Sem evento novo, não chamar o LLM.
- Controle de custo: somar `usage` de cada resposta; parar se uma rodada passar de US$ 0,50 ou se um evento passar de 5 chamadas ao LLM.
- A chave fica em .env (OPENAI_API_KEY), nunca no código. .env no .gitignore.
- Não escrever no código a resposta de eventos específicos do cenário de treino.
- Código simples, funções pequenas, comentários em português.

## Detalhes do servidor (README oficial)
- Toda resposta é JSON com `status` ("ok" ou "erro") e `agora`; erros de regra trazem `codigo` e `mensagem`.
- proximo_evento sem evento novo devolve `evento: null` e a hora do próximo evento; com `esperar_segundos` (máx. 30) o servidor segura a resposta. Fim do cenário: `encerrado: true`.
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
- Bases: contratados, admissoes (uma por contratado, ids ADM-xx, com o status de cada frente: ti, equipamento, exame etc.), checklist, documentos exigidos, áreas, FAQ. Nomes exatos e campos em docs/bases.json.
- A base admissoes é a fonte da verdade do andamento: ler antes de agir e atualizar com `atualizar` a cada etapa concluída. A memória local guarda só o que o servidor não guarda (cobranças feitas, propostas, escalações, lições).
- Muitos eventos de cobrança só chegam se a etapa ainda estiver pendente: agir cedo (acionar TI, equipamentos e clínica no 1º dia) evita cobranças.
- O cenário começa no dia 1 já perto dos prazos (há contratado com D-7 no 1º dia): no 1º dia, iniciar todas as frentes de todos os contratados.
- Documentos chegam estruturados no evento, numa lista `documentos` com `tipo`, `arquivo` e `descricao`. O `tipo` informado pode estar errado (ex.: tipo "rg" com descrição de CNH): conferir sempre pela `descricao` contra a regra. Não usar campos como `valido` ou `problema` mesmo que apareçam: a decisão é do conferente.
- Áreas (docs/areas.json): Contabilidade só recebe dados pelo portal, NUNCA por e-mail (nem respondendo a um e-mail dela). Clínica agenda o exame às 09:00, 2 dias úteis depois do pedido. TI e Equipamentos respondem em até 2 dias úteis. O e-mail do gestor está em gestor_email na base contratados. Cobrar uma área só depois do prazo de resposta dela.
- Equipamentos e TI recebem nome, cargo e data de início. Monitor é para desenvolvimento e design.
- Pedido de mudança da data de início escala SEMPRE, venha do contratado ou do gestor (ex.: gestor pedindo para adiantar).
- FAQ (docs/faq.json): campos id, pergunta, resposta, palavras_chave (com acento). Responder contratado só com o texto de `resposta`.
```

---

## 1. Estrutura do projeto

```text
Crie a estrutura inicial do projeto conforme .github/copilot-instructions.md:

agentes/
  __init__.py
  coordenador.py
  conferente.py
  comunicador.py
core/
  mcp_cliente.py      # conexão MCP + tratamento de falhas
  llm.py              # chamada ao gpt-4o-mini com schema e contador de custo
  memoria.py          # SQLite: estado dos casos e lições
  prazos.py           # dias úteis e varredura
  regras.py           # regras fixas (roteamento forçado, documentos, privacidade)
  schemas.py          # modelos pydantic das saídas
grafo/
  estado.py           # TypedDict do estado do atendimento
  nos.py              # nós do grafo (chamam agentes/*)
  grafo.py            # monta e compila o StateGraph com checkpointer
prompts/              # um .md por tarefa
portal/
  contabilidade.py    # Playwright
painel/
  app.py              # Streamlit: aprovações e escalações
docs/
main.py               # sobe os três agentes com um comando
requirements.txt
.env.example
.gitignore
README.md

Só crie os arquivos com docstrings e TODOs, sem implementar ainda. Preencha requirements.txt, .env.example e .gitignore.
```

## 2. Descobrir o mundo

```text
Crie scripts/descobrir_mundo.py que:
1. Conecta ao servidor MCP em http://localhost:8765/mcp usando o pacote `mcp`.
2. Lista as ferramentas disponíveis e salva nome, descrição e parâmetros em docs/ferramentas.json.
3. Chama listar_bases com agente="setup" e salva o resultado em docs/bases.json.
4. Para cada base, chama consultar com limite=3 e salva exemplos em docs/exemplos/<base>.json.
Imprima um resumo no terminal. Atenção: a primeira chamada liga o relógio simulado, então rode isto com o servidor recém-iniciado e reinicie o servidor depois.
```

> Depois de rodar, abra `docs/bases.json` e `docs/ferramentas.json` no editor: os próximos prompts usam esses arquivos como referência.

## 3. Cliente MCP com tratamento de falhas ⚙️

```text
Implemente core/mcp_cliente.py, usando docs/ferramentas.json como referência dos parâmetros.

Classe ClienteMCP(nome_agente) com:
- chamar(ferramenta, args, motivo, evento_id=None, eh_acao=False): sempre injeta agente e motivo; injeta evento_id quando informado.
- Tratamento de falhas exatamente como em copilot-instructions.md. Para 504 em ação, receba uma função `verificar` opcional que consulta se a ação já foi feita antes de repetir. Para enviar_mensagem, o verificar padrão consulta a base `mensagens` (destinatário + assunto + evento_id).
- registrar_conversa não passa pelo retry (não sofre falha simulada). Erro 500 não tem retry: loga e levanta exceção.
- Ler `status`, `codigo`, `mensagem` e `agora` de toda resposta; devolver um objeto Resposta(ok, dados, codigo, mensagem, agora).
- Timeout de 20 s.
- Atalhos: proximo_evento(esperar=30), ler_evento, consultar, registrar, atualizar, enviar_mensagem, responder_evento, registrar_conversa(de, para, texto).
- Guarda o último `agora` recebido em self.agora.
- Log de cada chamada em logs/agentes.jsonl (agente, ferramenta, status, motivo, tempo).
Inclua um teste rápido em scripts/testar_mcp.py.
```

## 4. Memória

```text
Implemente core/memoria.py com sqlite3 (arquivo data/memoria.db):

Tabela casos: contratado_id, nome, data_inicio, fase, etapas (JSON com status de cada etapa do checklist: pendente/feito/risco e data), documentos (JSON: tipo, status, motivo), ultimo_contato_contratado, ultima_cobranca, propostas_abertas (JSON), escalacoes_abertas (JSON), atualizado_em.
Tabela licoes: id, texto, criada_em. Nunca guardar dado pessoal aqui.
Tabela aprovacoes: id, contratado_id, tipo, descricao, status (pendente/aprovado/recusado), decidido_por, decidido_em.
Tabela escalacoes: id, contratado_id, regra, conteudo (JSON), status, resolvido_em.

Funções: carregar_caso, salvar_caso, resumo_caso(contratado_id, campos) que devolve só os campos pedidos (para mandar ao LLM com pouco contexto), adicionar_licao, listar_licoes(limite=5), criar_aprovacao, aprovacoes_decididas, criar_escalacao.
Inicialize os casos a partir das bases de contratados e checklist (ver docs/bases.json).
```

## 5. Prazos em dias úteis

> Salve o checklist recebido do servidor em `docs/checklist.json` antes de enviar este prompt.

```text
Implemente core/prazos.py. As etapas e prazos NÃO ficam fixos no código: vêm da base de checklist do servidor (consultar no início da rodada; formato em docs/checklist.json).

Formato de cada item: id, fase, etapa, prazo_dias_uteis_antes (int ou null), quando (texto opcional), quem.

Funções:
- carregar_checklist(cliente_mcp) → consulta a base de checklist e devolve a lista de itens. Se a consulta falhar, usa docs/checklist.json como reserva.
- dias_uteis_entre(agora, data) contando só segunda a sexta.
- d_menos(contratado, agora) → quantos dias úteis faltam para a data de início.
- prazo_da_etapa(item, data_inicio) → data limite = data_inicio menos prazo_dias_uteis_antes dias úteis; prazo 0 = o próprio primeiro dia.

Tratamento dos itens com prazo null (lidos pelo id e pelo campo "quando"):
- E1 (proposta aceita): ponto de partida do caso; marca a admissão como iniciada.
- E2 (acionar TI e equipamentos): ação imediata assim que a admissão começa.
- E10 (pós-admissão): só gera a mensagem de próximos passos, enviada antes ou no primeiro dia.
- R1 (contratado sem responder): ler "cobrar depois de N dias úteis; escalar depois de M" do campo "quando" (extrair os números com regex; se falhar, usar 2 e 4).

varredura(casos, checklist, agora) → lista de ações pendentes, cada uma com contratado_id, etapa_id, tipo (acionar_area, cobrar_contratado, cobrar_area, escalar, checar_primeiro_dia, proximos_passos), agente_responsavel e motivo (citando o id da etapa e o prazo):
  - etapa com prazo vencendo em ≤1 dia útil e não feita → ação para o agente responsável (mapear pelo campo "quem": contratado → comunicador cobra o contratado; clínica/gestor/TI → comunicador aciona a área; "time, pelo portal" → conferente)
  - etapa com prazo vencido e não feita → escalar
  - regra R1 aplicada ao último contato do contratado
  - E7 ou E8 não feitos em D-2 → escalar primeiro_dia_em_risco
  - D-1 → checar_primeiro_dia: exame apto (E7), contrato assinado (E8), acessos criados e equipamento acionado (E2), gestor avisado (E6)
- Não repetir a mesma ação no mesmo dia útil (consultar ultima_cobranca na memória).

Sem LLM neste arquivo. Inclua testes em tests/test_prazos.py usando docs/checklist.json e datas de exemplo (incluindo uma semana com fim de semana no meio).
```

## 6. Chamada ao LLM com custo controlado

```text
Implemente core/llm.py e core/schemas.py.

schemas.py: modelos pydantic para cada saída de docs/prompts_agentes.md: ClassificacaoEvento, RevisaoAcao, Escalacao, ConferenciaDocumento, PacoteContabilidade, Mensagem. Use Literal para os enums.

llm.py:
- executar(tarefa, contexto: dict, schema) → carrega prompts/base.md + prompts/<tarefa>.md, substitui as variáveis {…}, chama gpt-4o-mini com temperature=0.1 e response_format estruturado com o schema.
- Parte fixa do prompt sempre no início e variáveis no fim (aproveita o cache automático da OpenAI).
- max_tokens por tarefa (ex.: 300 para classificar, 600 para redigir mensagem).
- Se a saída não validar no schema, tenta mais 1 vez; se falhar, devolve None (quem chamou escala).
- Contador global de custo (US$ 0,15 por 1M de entrada, US$ 0,075 em cache, US$ 0,60 por 1M de saída) com limite por rodada e por evento, como em copilot-instructions.md. Ao estourar, lança LimiteCustoExcedido.
- Loga tarefa, tokens e custo em logs/custo.jsonl.
Crie os arquivos prompts/*.md copiando os textos de docs/prompts_agentes.md, um por tarefa.
```

## 7. Regras fixas

```text
Implemente core/regras.py, sem LLM:
- forcar_roteamento(evento, classificacao): se o texto do evento indicar mudança de data de início, desistência ou dado sensível (lista de palavras-chave), força encaminhar_para="escalar_rh", mesmo que o LLM diga outra coisa.
- Documentos: NÃO fixar a lista no código. Carregar da base de documentos exigidos do servidor (formato em docs/documentos.json: tipo, nome, regra, exigido, palavras), com docs/documentos.json como reserva.
- documentos_exigidos(contratado, docs_base) → filtra pelo campo "exigido":
  - "sempre" → sempre
  - "se casado ou casada" → se o estado civil do contratado for casado(a)
  - "se tiver filhos" → se tiver filhos; certidao_nascimento_filhos é exigida UMA POR FILHO (guardar quantidade esperada e recebida)
  - "para homens" → se o contratado for homem
  - valor desconhecido → marcar como "verificar com RH" (não ignorar)
  Usar os campos do contratado descritos em docs/bases.json.
- Documentos estruturados (lista `documentos` no evento): usar o `tipo` só como indicação do que a pessoa diz que mandou; o conferente confere a `descricao`. Se a descrição citar outro documento (ex.: CNH com tipo "rg"), tratar como inválido para aquele tipo.
- identificar_tipo(texto, docs_base) → só para documento citado em texto livre, sem a lista estruturada. Normaliza o texto (minúsculo, sem acento) e procura as "palavras" de cada tipo. Regras:
  - testar primeiro as expressões mais longas ("comprovante de residencia", "carteira de trabalho", "cartao nacional de saude") antes das curtas ("rg", "pis", "sus", "foto");
  - palavras curtas só valem como palavra inteira (regex \b), para "rg" não casar dentro de outra palavra;
  - se o evento for ficha cadastral, não identificar documentos por palavras soltas como "endereco" ou "nascimento";
  - zero ou mais de um tipo encontrado → devolve None e o conferente pede ao LLM para identificar.
- pre_checar_documento(texto, tipo_esperado) → sem LLM: se o texto citar "cnh" ou "habilitacao" e o esperado for rg (ou não houver RG), recusa com o motivo "CNH não serve no lugar do RG" (regra da base).
- documentos_cobertos_por_outro(): CPF fica atendido se o número do CPF estiver no RG recebido; PIS fica atendido se o número aparecer na carteira de trabalho. Registrar no caso de onde veio.
- comprovante_residencia: conferir se a data está dentro de 90 dias antes de `agora` (dias corridos) e se está no nome do contratado. Em nome de outra pessoa → resultado "divergencia" (proposta ao RH), nunca recusa nem aceite direto.
- destinatarios_permitidos(tipo_dado, contratado): contabilidade só via portal; gestor, TI e equipamentos recebem nome, cargo e data de início; clínica só o necessário para agendar.
- checar_privacidade(mensagem, destinatario): detecta CPF, RG e endereço por regex e bloqueia se o destinatário não puder receber.
- nivel_acao(tipo_acao) → "faz_sozinho" | "propoe" | "escala", conforme a tabela de níveis do Tema 2.
Inclua testes em tests/test_regras.py.
```

## 8. Os três agentes ⚙️

```text
Implemente agentes/coordenador.py, agentes/conferente.py e agentes/comunicador.py, usando core/*.
Estes arquivos têm só as capacidades de cada agente (funções que recebem dados e devolvem resultado). A orquestração (quem chama quem, revisão, correção, aprovação) fica no grafo da etapa 9, não aqui.

coordenador:
- classificar(evento) → llm.executar("classificar_evento") + regras.forcar_roteamento.
- revisar(tipo_acao, acao, contratado_id) → llm.executar("revisar_acao"); sempre registra o resultado com registrar_conversa(de=autor, para="coordenador", texto=decisão + erro + correção).
- escalar(contratado_id, regra, evento) → llm.executar("redigir_escalacao") e salva em memoria.criar_escalacao.
- propor(contratado_id, tipo, descricao) → memoria.criar_aprovacao; nunca executa sem aprovação.

conferente:
- conferir(evento, contratado_id) → regras.pre_checar_documento e depois llm.executar("conferir_documento"); atualiza o caso; devolve o resultado.
- montar_pacote(contratado_id) → llm.executar("montar_pacote_contabilidade").

comunicador:
- buscar_faq(pergunta, faq_base) → sem LLM: normaliza pergunta e palavras_chave (minúsculo, sem acento), pontua cada FAQ pelo número de palavras-chave encontradas (expressão de duas palavras vale 2) e devolve as 2 melhores com pontuação > 0. Passa as duas ao LLM, que usa só a que responde à pergunta (ex.: "primeiro dia" aparece em FAQ-06 e FAQ-08). Nenhuma → fora_do_faq.
- destinatario_area(nome_area) e email_gestor(contratado) → leem as bases de áreas e contratados; nunca e-mail fixo no código.
- redigir(objetivo, destinatario, contratado_id, evento=None) → usa buscar_faq quando o objetivo for responder dúvida, chama llm.executar("redigir_mensagem"), roda regras.checar_privacidade.
- Pergunta de gestor ou área sobre o andamento (ex.: data de início, se os acessos foram pedidos): responder com os dados das bases contratados e admissoes, sem dado pessoal sensível; se pedir algo novo (acesso específico, monitor, licença), repassar para a área certa com evento_id.
- enviar(mensagem, evento_id) → enviar_mensagem ou responder_evento.

Ações que precisam de revisão (o grafo da etapa 9 garante): recusa de documento, mensagem com dado pessoal, mensagem fora do FAQ, proposta ao RH e envio ao portal.
```

## 9. Grafo de atendimento (LangGraph) ⚙️

```text
Implemente grafo/estado.py, grafo/nos.py e grafo/grafo.py com LangGraph, conforme a seção "Arquitetura: LangGraph híbrido" de copilot-instructions.md.

estado.py — TypedDict EstadoAtendimento:
  origem ("evento" | "prazo"), evento (dict ou None), tarefa_prazo (dict ou None), contratado_id, classificacao, acao_proposta (dict: tipo_acao, autor, conteudo), revisao, tentativas_correcao (int), decisao_rh, resultado, log (lista de strings, com reducer de concatenação).

nos.py — cada nó é uma função pequena que chama agentes/* e devolve só os campos que mudou:
  - carregar_contexto: lê contratado e admissão nas bases; se o evento tiver responde_a, liga ao caso do evento original.
  - classificar (coordenador): coordenador.classificar + regras.forcar_roteamento. Para origem "prazo", a classificação vem da própria tarefa da varredura (sem LLM).
  - conferir (conferente): confere cada documento da lista `documentos`; gera acao_proposta de recusa, de proposta ao RH (divergência) ou de registro como conferido; se todos os exigidos estiverem conferidos, marca pronto_para_pacote.
  - montar_pacote (conferente): gera acao_proposta tipo "envio_portal".
  - redigir (comunicador): gera acao_proposta tipo "mensagem".
  - revisar (coordenador): coordenador.revisar; registra com registrar_conversa(de=autor, para="coordenador").
  - corrigir: devolve ao autor com a correcao_sugerida e incrementa tentativas_correcao.
  - aguardar_rh: cria a aprovação em memoria e chama interrupt({...}) com o resumo da proposta; ao retomar, grava decisao_rh.
  - escalar (coordenador): coordenador.escalar e registra no painel.
  - executar: faz a chamada MCP real (enviar_mensagem, responder_evento, registrar, atualizar ou portal.enviar_dados) com evento_id e o nome do agente autor.
  - fechar_atendimento: garante pelo menos uma ação com evento_id; se não houve ação, grava `observacao` com o motivo.

grafo.py — arestas:
  START → carregar_contexto → classificar
  classificar → (condicional) conferir | redigir | escalar
  conferir → (condicional) revisar (recusa ou divergência) | montar_pacote (pronto_para_pacote) | executar (registro simples)
  montar_pacote → revisar
  redigir → (condicional) revisar (dado pessoal, fora do FAQ ou recusa) | executar
  revisar → (condicional) executar (aprovado e nível "faz_sozinho") | aguardar_rh (aprovado e nível "propoe") | corrigir (corrigir e tentativas_correcao < 1) | escalar (corrigir de novo)
  corrigir → volta ao nó do autor (conferir, montar_pacote ou redigir)
  aguardar_rh → (condicional) executar (aprovado) | fechar_atendimento (recusado, registrando a decisão)
  executar → fechar_atendimento; escalar → fechar_atendimento; fechar_atendimento → END
  Mudança de data, dado sensível e desistência sempre vão para escalar (a regra vem de regras.forcar_roteamento).

  - Compilar com AsyncSqliteSaver em data/grafo.db.
  - Função exportar_diagrama() que salva grafo.get_graph().draw_mermaid() em docs/grafo.md (para o README e a apresentação).
  - Limite de passos do grafo (recursion_limit) baixo, por exemplo 25, para evitar laço infinito.
Inclua tests/test_grafo.py simulando um documento inválido (CNH como RG), uma divergência (comprovante em nome de outra pessoa) e uma mensagem com CPF para o gestor (deve ir para corrigir).
```

## 10. Laço principal ⚙️

```text
Implemente main.py (asyncio):
1. Carrega .env, cria um ClienteMCP para cada agente, inicializa a memória e compila o grafo.
   - Recuperação: listar_eventos com status "lido" e rodar o grafo para os que ainda não têm ação (o agente pode ter caído no meio).
2. Laço: proximo_evento(esperar=30) até encerrado=true.
   - Com evento: roda o grafo com thread_id = id do evento (origem "evento").
   - Eventos de contratados diferentes rodam em paralelo (asyncio.create_task); eventos do MESMO contratado rodam em fila (um asyncio.Lock por contratado) para não haver conflito de estado.
   - Processar cada evento em poucos segundos: cobranças do mundo chegam ~40 s reais depois.
   - Sem evento: prazos.varredura → para cada ação pendente, roda o grafo com origem "prazo" e thread_id = "<contratado>-<etapa>-<data>".
   - A cada volta: lê em memoria as aprovações decididas no painel e retoma o thread pausado com Command(resume={"aprovado": bool, "por": nome, "comentario": texto}).
3. Erro 410 → para as ações e imprime um resumo final (casos, escalações, custo total).
4. Ctrl+C encerra com segurança (o checkpointer já guardou o estado).
Execução: `python main.py`. Logs legíveis no terminal: [hora simulada] agente → nó → ação (motivo).
```

## 11. Canal humano

```text
Implemente painel/app.py com Streamlit, lendo e gravando data/memoria.db:
- Aba "Aprovações": lista as pendentes com contexto e botões Aprovar e Recusar, com campo de nome de quem decidiu e comentário. O painel só grava a decisão na tabela aprovacoes; quem retoma o grafo pausado é o main.py.
- Aba "Escalações": lista as abertas no formato de escalação (situação, já feito, risco, decisão necessária, opções), com campo de resposta e botão Resolver.
- Aba "Risco do primeiro dia": tabela com os 5 contratados, D-n e o status dos 5 itens de checagem, colorindo verde, amarelo e vermelho.
- Atualiza sozinho a cada 5 s.
Execução: `streamlit run painel/app.py`.
```

## 12. Portal da contabilidade ⚙️

> Antes deste prompt, abra http://localhost:8765/legado no navegador, veja a tela do portal e anote os campos e botões (ou salve o HTML da página em `docs/portal.html`).

```text
Implemente portal/contabilidade.py com Playwright (sync API), usando docs/portal.html como referência:
- enviar_dados(pacote: PacoteContabilidade, agente="conferente", evento_id=None) → abre http://localhost:8765/legado, navega até o Portal da Contabilidade, preenche o campo do nome do agente (o formulário exige), preenche cada campo com os valores do pacote, relê os campos preenchidos e compara com o pacote antes de enviar.
- Tela não sofre falha simulada; erro 410 significa cenário encerrado (parar).
- Depois de enviar, confirma na tela que o registro aparece; devolve sucesso/falha e o que leu na tela.
- Antes de enviar, verifica se o contratado já consta como enviado (evita duplicar em caso de erro ou timeout).
- headless configurável por variável de ambiente (HEADLESS=0 para mostrar na demo).
Só é chamado depois de coordenador.revisar aprovar o pacote.
```

## 13. README e entrega

```text
Escreva o README.md:
- O que o projeto faz, em 3 linhas.
- Como rodar com um comando (servidor MCP com TEMA=admissao, depois `python main.py` e `streamlit run painel/app.py`).
- Papel de cada agente e quem revisa quem.
- Diagrama do grafo LangGraph (colar o mermaid de docs/grafo.md) explicando revisão, correção e pausa para aprovação.
- O que é decidido em código e o que é decidido pelo LLM.
- Como funcionam memória, escalação, aprovação e tratamento de falhas.
- Custo médio por rodada (ler de logs/custo.jsonl).
- O que faríamos com mais tempo.
```

---

## Ordem de testes

1. Etapas 1–3 → `scripts/testar_mcp.py` com `ERROS=0`.
2. Etapas 4–7 → `pytest`.
3. Etapas 8–9 → `pytest tests/test_grafo.py` e conferir `docs/grafo.md`.
4. Etapa 10 → servidor com `SEM_CENARIO=1 SEGUNDOS_POR_DIA=600`, criando eventos pelo botão **+ Novo evento**.
5. Etapas 11–12 → testar a pausa para aprovação (aprovar no painel e ver o grafo retomar) e o envio ao portal.
6. Cenário completo com `SEED=42` e falhas ligadas: o mesmo sorteio a cada rodada facilita comparar antes e depois de uma correção.
7. Cenário completo no relógio padrão (20 min), como na apresentação. Conferir o painel, `python ver_log.py --erros` e `logs/custo.jsonl`.

### Matriz de testes com o cenário de treino

Use estes casos para conferir o comportamento no painel. **Não** escreva no código nenhuma resposta específica para eles: o comportamento tem que sair das regras gerais.

| Evento | Comportamento esperado |
|---|---|
| PED-001 a 005 (aceites) | Admissão iniciada; TI, equipamentos e clínica acionados já no 1º dia; pedido de documentos a quem ainda não mandou |
| PED-006 (Beatriz, tudo certo) | Todos conferidos → pacote → revisão → portal |
| PED-008 / PED-023 (Thiago) | Detecta falta de foto 3x4 e certificado militar; cobra; certidão do filho aceita |
| PED-009 (CTPS digital) | Responde com FAQ-02 antes da cobrança chegar |
| PED-010 (Larissa, CNH como RG) | Recusa com o motivo (FAQ-01) e pede o RG frente e verso |
| PED-011 / ADM-05 (comprovante no nome do marido) | Divergência → proposta ao RH, sem aceitar nem recusar sozinho |
| PED-012, 014, 015, 018, 019, 021, 025, 026, 030 | Resposta só com o FAQ certo |
| PED-007, PED-013 (gestores perguntando) | Resposta com dados das bases; acessos específicos repassados à TI |
| PED-016 (Beatriz pede outra data) | Escala ao RH; nada é alterado sem OK |
| PED-020 (gestora quer adiantar a Camila) | Também é mudança de data → escala |
| PED-017, PED-024 (equipamentos, kit com monitor) | Envia nome, cargo e data de início; repassa monitor e licença |
| PED-022, PED-029 (Diego sumiu) | Cobra em 2 dias úteis, escala em 4; responde ao gestor sem prometer |
| PED-027 (lembrete da contabilidade) | Responde confirmando, sem mandar dado por e-mail |
| PED-028 (exame da Larissa) | Não deveria acontecer se a clínica foi acionada cedo |
| ADM-05 (contrato) | Cobra a assinatura de novo até assinar |

Para testar casos difíceis (documento inválido, mudança de data, contratado que some), copie `dados/admissao/treino.json`, crie pedidos extras e suba com `--cenario meu_cenario.json`. Isso é permitido pelas regras, desde que sem dados reais.
