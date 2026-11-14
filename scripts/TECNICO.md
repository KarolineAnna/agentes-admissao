# Documentação Técnica dos Scripts

Documentação técnica detalhada dos scripts de descoberta.

## Arquitetura

### Fluxo de Execução

```
testar_conexao.py
    ↓
    Testa GET /ping e POST com ação="ping"
    ↓
    Se OK → descobrir_mundo_http.py
    ↓
    Conecta ao servidor
    ↓
    Descobre ferramentas (opcional)
    ↓
    Chama listar_bases com agente="setup"
    ↓
    Para cada base, chama consultar com limite=3
    ↓
    Salva resultados em docs/
    ↓
    Imprime resumo
    ↓
    Reiniciar servidor (IMPORTANTE!)
```

## Detalhes de Implementação

### testar_conexao.py

**Responsabilidades**:
- Testar conexão com servidor MCP
- Tentar GET /ping
- Tentar POST com ação="ping"
- Tentar POST com ação="listar_bases"
- Imprimir resultado

**Fluxo**:
1. Criar cliente httpx com timeout=5s
2. Tentar GET /ping
3. Tentar POST com payload vazio
4. Tentar POST com listar_bases
5. Se alguma chamada suceder, retornar True
6. Caso contrário, retornar False

**Saída**:
```
✓ Conexão bem-sucedida!
ou
✗ Falha na conexão!
```

### descobrir_mundo_http.py

**Responsabilidades**:
- Conectar ao servidor MCP
- Descobrir ferramentas (opcional)
- Listar bases
- Descobrir exemplos para cada base
- Salvar resultados em JSON
- Imprimir resumo

**Fluxo**:
1. Criar cliente httpx com timeout=15s
2. Testar conexão com GET /ping
3. Chamar listar_bases com agente="setup"
4. Para cada base:
   - Chamar consultar com limite=3
   - Salvar resultados
5. Salvar tudo em JSON
6. Imprimir resumo

**Payloads**:

```json
{
  "acao": "listar_bases",
  "agente": "setup",
  "motivo": "Descoberta inicial do mundo"
}
```

```json
{
  "acao": "consultar",
  "base": "contratados",
  "limite": 3,
  "agente": "setup",
  "motivo": "Descoberta de exemplos"
}
```

**Respostas Esperadas**:

listar_bases:
```json
{
  "status": "ok",
  "bases": {
    "contratados": {
      "campos": ["id", "nome", "cpf", ...],
      "campos_para_registrar": ["nome", "cpf", ...],
      "campos_alteraveis": ["cargo", ...]
    },
    ...
  },
  "agora": "2024-01-15T08:00:00"
}
```

consultar:
```json
{
  "status": "ok",
  "registros": [
    {"id": "...", "nome": "...", ...},
    ...
  ],
  "total": 100,
  "tem_mais": true,
  "agora": "2024-01-15T08:00:00"
}
```

### descobrir_mundo.py

**Responsabilidades**:
- Mesmo que descobrir_mundo_http.py
- Mas usando pacote mcp em vez de httpx

**Diferenças**:
- Usa ClientSession do pacote mcp
- Pode usar StdioClientTransport ou HTTPClientTransport
- Mais robusto para protocolos complexos

## Estrutura de Dados

### docs/ferramentas.json

```json
{
  "ferramenta1": {
    "description": "Descrição da ferramenta",
    "parameters": {
      "param1": {
        "type": "string",
        "description": "Descrição do parâmetro"
      },
      "param2": {
        "type": "integer",
        "description": "Descrição do parâmetro"
      }
    }
  },
  ...
}
```

### docs/bases.json

```json
{
  "base1": {
    "campos": ["campo1", "campo2", "campo3"],
    "campos_para_registrar": ["campo1", "campo2"],
    "campos_alteraveis": ["campo2", "campo3"],
    "exemplo": {
      "campo1": "valor1",
      "campo2": "valor2"
    }
  },
  ...
}
```

### docs/exemplos/<base>.json

```json
[
  {
    "id": "ID-001",
    "campo1": "valor1",
    "campo2": "valor2",
    ...
  },
  {
    "id": "ID-002",
    "campo1": "valor3",
    "campo2": "valor4",
    ...
  },
  ...
]
```

## Tratamento de Erros

### Erros HTTP

| Código | Significado | Ação |
|--------|-------------|------|
| 200 | OK | Processar resposta |
| 400 | Bad Request | Logar erro, não repetir |
| 404 | Not Found | Logar erro, não repetir |
| 500 | Server Error | Logar erro, não repetir |
| 503 | Service Unavailable | Retry com backoff |
| 504 | Gateway Timeout | Retry com backoff |

### Erros de Resposta

| Status | Significado | Ação |
|--------|-------------|------|
| "ok" | Sucesso | Processar dados |
| "erro" | Erro | Logar mensagem, não repetir |

## Logging

Todos os scripts usam logging padrão do Python:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

Níveis:
- INFO: Informações gerais (conexão, descoberta)
- WARNING: Avisos (falhas não críticas)
- ERROR: Erros (falhas críticas)

## Timeouts

- testar_conexao.py: 5 segundos
- descobrir_mundo_http.py: 15 segundos
- descobrir_mundo.py: Padrão do mcp

## Limites

- Limite de registros por consulta: 3
- Máximo de bases: Sem limite (mas pode ser lento)
- Máximo de ferramentas: Sem limite

## Dependências

### testar_conexao.py
- httpx

### descobrir_mundo_http.py
- httpx
- json (stdlib)
- logging (stdlib)
- asyncio (stdlib)

### descobrir_mundo.py
- mcp
- json (stdlib)
- logging (stdlib)
- asyncio (stdlib)

## Performance

### Tempo Estimado

- testar_conexao.py: < 5 segundos
- descobrir_mundo_http.py: 10-30 segundos (depende do número de bases)
- descobrir_mundo.py: 10-30 segundos (depende do número de bases)

### Otimizações

- Usar httpx em vez de requests (mais rápido)
- Usar async/await para paralelizar chamadas
- Limitar número de registros por consulta (3)
- Usar timeout apropriado (15s)

## Segurança

- Sem credenciais hardcoded
- Sem dados sensíveis em logs
- Sem exposição de erros internos
- Validação de respostas JSON

## Extensibilidade

Os scripts podem ser estendidos para:
- Descobrir mais dados (campos, índices, etc.)
- Validar dados (tipos, formatos, etc.)
- Gerar documentação (Markdown, HTML, etc.)
- Gerar código (schemas, modelos, etc.)

## Referências

- [DESCOBERTA_MUNDO.md](../DESCOBERTA_MUNDO.md): Guia de uso
- [scripts/README.md](README.md): Documentação dos scripts
- [httpx](https://www.python-httpx.org/): Cliente HTTP
- [mcp](https://github.com/modelcontextprotocol/python-sdk): SDK MCP
