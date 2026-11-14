# Estrutura do Projeto - Agentes de Admissão

## Resumo

Estrutura inicial criada com docstrings e TODOs, pronta para implementação.

- **Total de arquivos Python**: 20
- **Total de linhas de código**: 376 (com docstrings e TODOs)
- **Arquivos de configuração**: 4 (.env.example, .gitignore, requirements.txt, README.md)

## Árvore de Diretórios

```
agentes-admissao/
├── agentes/                    # Três agentes de IA
│   ├── __init__.py
│   ├── coordenador.py         # Orquestra eventos, classifica, roteia, revisa
│   ├── conferente.py          # Confere documentos, monta pacote, envia
│   └── comunicador.py         # Redige mensagens
│
├── core/                       # Núcleo do sistema
│   ├── __init__.py
│   ├── mcp_cliente.py         # Cliente MCP com retry e tratamento de falhas
│   ├── llm.py                 # gpt-4o-mini com Structured Outputs
│   ├── memoria.py             # SQLite: casos, cobranças, propostas, escalações
│   ├── prazos.py              # Dias úteis e varredura de prazos
│   ├── regras.py              # Regras fixas (roteamento, privacidade, palavras-gatilho)
│   └── schemas.py             # Pydantic para Structured Outputs
│
├── grafo/                      # Orquestração LangGraph
│   ├── __init__.py
│   ├── estado.py              # TypedDict do estado do atendimento
│   ├── nos.py                 # Nós do grafo (CLASSIFICAR, ROTEAR, CONFERIR, etc.)
│   └── grafo.py               # StateGraph com checkpointer SQLite
│
├── portal/                     # Integração com portal
│   ├── __init__.py
│   └── contabilidade.py       # Envio do pacote (Playwright)
│
├── painel/                     # Interface Streamlit
│   ├── __init__.py
│   └── app.py                 # Aprovações, escalações, histórico
│
├── prompts/                    # Modelos de mensagem e prompts
│   └── (a preencher)
│
├── docs/                       # Documentação (já existente)
│   ├── regras_negocio.md      # RN-01 a RN-66
│   ├── prompts_agentes.md     # Schemas e prompts dos agentes
│   ├── areas.json             # Dados de referência
│   ├── checklist.json
│   ├── contratados.json
│   ├── documentos_exigidos.json
│   └── faq.json
│
├── data/                       # Banco de dados (criado em runtime)
│   ├── grafo.db               # Checkpointer LangGraph
│   └── memoria.db             # Memória local
│
├── logs/                       # Logs (criado em runtime)
│   └── agentes.log
│
├── main.py                     # Ponto de entrada
├── requirements.txt            # Dependências
├── .env.example                # Variáveis de ambiente
├── .gitignore                  # Git ignore
├── README.md                   # Documentação
└── ESTRUTURA.md                # Este arquivo
```

## Arquivos Criados

### Agentes (agentes/)
- **coordenador.py**: Laço de eventos, classificação, roteamento, revisão, escalação, varredura de prazos
- **conferente.py**: Conferência de documentos, validação de estados, montagem de pacote, envio
- **comunicador.py**: Redação de mensagens, checagem de privacidade, validação de destinatário

### Core (core/)
- **mcp_cliente.py**: Cliente MCP com retry (503, 504, 409), timeout 15s, logging
- **llm.py**: OpenAI SDK, gpt-4o-mini, temperatura 0.1, Structured Outputs, contador de custo
- **memoria.py**: SQLite com tabelas para casos, cobranças, propostas, escalações, ações, lições
- **prazos.py**: Cálculo de dias úteis, varredura de prazos, disparo de cobranças
- **regras.py**: Validações fixas (mudança de data, desistência, CNH, privacidade, palavras-gatilho)
- **schemas.py**: Pydantic para ClassificacaoEvento, RoteamentoEvento, DecisaoDocumento, etc.

### Grafo (grafo/)
- **estado.py**: TypedDict com evento, admissao, contratado, acao, revisao, custo, historico
- **nos.py**: Nós CLASSIFICAR, ROTEAR, CONFERIR, REDIGIR, REVISAR, EXECUTAR, CORRIGIR, ESCALAR
- **grafo.py**: StateGraph com checkpointer SQLite, add_conditional_edges, interrupt()

### Portal (portal/)
- **contabilidade.py**: Playwright para envio do pacote (nome, CPF, nascimento, cargo, PIS)

### Painel (painel/)
- **app.py**: Streamlit para aprovações, escalações, histórico

### Configuração
- **main.py**: Ponto de entrada, carrega .env, inicializa MCP, memória, grafo, painel
- **requirements.txt**: langgraph, openai, mcp, pydantic, playwright, streamlit, python-dotenv
- **.env.example**: Variáveis de ambiente (OPENAI_API_KEY, MCP_SERVER_URL, etc.)
- **.gitignore**: Python, venv, .env, data/, logs/, .vscode/, .idea/
- **README.md**: Documentação completa com instalação, uso, regras, limites

## Próximos Passos

1. **Implementar core/mcp_cliente.py**: Cliente MCP com retry e tratamento de falhas
2. **Implementar core/llm.py**: Chamada ao gpt-4o-mini com Structured Outputs
3. **Implementar core/memoria.py**: SQLite com CRUD para casos, cobranças, propostas
4. **Implementar core/prazos.py**: Cálculo de dias úteis e varredura
5. **Implementar core/regras.py**: Validações fixas
6. **Implementar core/schemas.py**: Pydantic para Structured Outputs
7. **Implementar grafo/estado.py**: TypedDict do estado
8. **Implementar grafo/nos.py**: Nós do grafo
9. **Implementar grafo/grafo.py**: StateGraph com checkpointer
10. **Implementar agentes/coordenador.py**: Laço de eventos e orquestração
11. **Implementar agentes/conferente.py**: Conferência de documentos
12. **Implementar agentes/comunicador.py**: Redação de mensagens
13. **Implementar portal/contabilidade.py**: Envio pelo portal
14. **Implementar painel/app.py**: Interface Streamlit
15. **Implementar main.py**: Ponto de entrada
16. **Criar prompts/**: Modelos de mensagem e prompts

## Notas

- Todos os arquivos têm docstrings explicando responsabilidades
- TODOs marcam o que precisa ser implementado
- Estrutura segue as regras obrigatórias do código:
  - Toda chamada MCP envia `agente` e `motivo`
  - Regras fixas em código, não no LLM
  - Sem evento novo, não chamar LLM
  - Controle de custo: US$ 0,50 por rodada, 5 chamadas por evento
  - .env no .gitignore
  - Código simples, funções pequenas, comentários em português
