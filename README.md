# Agentes de Admissão CLT

Sistema de três agentes de IA que conduzem a admissão CLT de contratados até o primeiro dia.

## Arquitetura

### Agentes
- **Coordenador**: Orquestra eventos, classifica, roteia e revisa ações críticas
- **Conferente**: Confere documentos, monta pacote da contabilidade, dispara envio
- **Comunicador**: Redige mensagens para contratados, áreas e gestores

### Stack
- **LangGraph**: Orquestração de atendimento com StateGraph e checkpointer SQLite
- **OpenAI**: gpt-4o-mini com Structured Outputs (temperatura 0.1)
- **MCP**: Cliente oficial com timeout de 15s e retry com backoff
- **Playwright**: Envio pelo portal
- **Streamlit**: Painel para aprovações e escalações
- **SQLite**: Memória local (casos, cobranças, propostas, escalações, ações, lições)

## Estrutura do Projeto

```
agentes/
  coordenador.py      # Orquestração de eventos
  conferente.py       # Conferência de documentos
  comunicador.py      # Redação de mensagens

core/
  mcp_cliente.py      # Cliente MCP com retry
  llm.py              # Chamada ao gpt-4o-mini
  memoria.py          # SQLite: casos, cobranças, propostas
  prazos.py           # Dias úteis e varredura
  regras.py           # Regras fixas (roteamento, privacidade)
  schemas.py          # Pydantic para Structured Outputs

grafo/
  estado.py           # TypedDict do estado
  nos.py              # Nós do grafo (CLASSIFICAR, ROTEAR, etc.)
  grafo.py            # StateGraph com checkpointer

portal/
  contabilidade.py    # Envio pelo portal (Playwright)

painel/
  app.py              # Streamlit: aprovações e escalações

prompts/              # Modelos de mensagem e prompts

main.py               # Ponto de entrada
```

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/KarolineAnna/agentes-admissao.git
cd agentes-admissao
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

5. Instale o Playwright:
```bash
playwright install
```

## Uso

Inicie os agentes:
```bash
python main.py
```

O sistema irá:
1. Conectar ao servidor MCP em http://localhost:8765/mcp
2. Iniciar o laço de eventos no coordenador
3. Abrir o painel Streamlit em http://localhost:8501

## Regras de Negócio

Veja [docs/regras_negocio.md](docs/regras_negocio.md) para a lista completa de regras (RN-01 a RN-66).

### Principais
- Prazos em dias úteis (seg-sex, 08:00-18:00)
- Mudança de data/dado sensível/desistência sempre escalam
- CNH nunca vale como RG
- Contabilidade só recebe dados pelo portal
- Documentos: recebido, aceito, aceito com ressalva, recusado
- Duas mensagens ao mesmo contratado contam como dois pedidos com >= 1 hora entre elas

## Limites de Custo

- Máximo US$ 0,50 por rodada do LLM
- Máximo 5 chamadas ao LLM por evento
- Contador de tokens e custo em cada resposta

## Logging

Logs são salvos em `logs/agentes.log` com nível configurável em `.env`.

## Desenvolvimento

### Testes
```bash
pytest
```

### Linting
```bash
pylint agentes/ core/ grafo/ portal/ painel/
```

## Referências

- [Servidor MCP](http://localhost:8765/mcp)
- [Documentação de Regras de Negócio](docs/regras_negocio.md)
- [Prompts dos Agentes](docs/prompts_agentes.md)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
