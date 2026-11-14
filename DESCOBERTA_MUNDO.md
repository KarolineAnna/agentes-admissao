# Descoberta do Mundo MCP

Guia para descobrir ferramentas e bases do servidor MCP.

## Visão Geral

O servidor MCP é o "mundo" onde os agentes operam. Antes de implementar os agentes, precisamos descobrir:

1. **Ferramentas disponíveis**: Quais ações podemos executar
2. **Bases de dados**: Quais dados estão disponíveis
3. **Exemplos de dados**: Como os dados são estruturados

## Procedimento

### 1. Testar Conexão

Primeiro, verifique se o servidor está rodando:

```bash
python scripts/testar_conexao.py
```

Saída esperada:

```
======================================================================
TESTE DE CONEXÃO COM SERVIDOR MCP
======================================================================

✓ Conexão bem-sucedida!

Você pode agora executar:
  python scripts/descobrir_mundo_http.py

======================================================================
```

### 2. Descobrir Mundo

Execute o script de descoberta:

```bash
python scripts/descobrir_mundo_http.py
```

Saída esperada:

```
======================================================================
RESUMO DA DESCOBERTA DO MUNDO MCP
======================================================================

📡 Servidor: http://localhost:8765/mcp

🔧 Ferramentas (X):
   • proximo_evento: Obtém o próximo evento da fila...
   • listar_bases: Lista as bases disponíveis...
   • consultar: Consulta registros de uma base...
   • ... (mais ferramentas)

📊 Bases (X):
   • contratados: N campos
     Campos: id, nome, cpf, ...
   • admissoes: N campos
     Campos: id, contratado_id, status, ...
   • ... (mais bases)

📋 Exemplos (X):
   • contratados: N registros
   • admissoes: N registros
   • ... (mais bases)

📁 Arquivos salvos:
   • docs/ferramentas.json
   • docs/bases.json
   • docs/exemplos/<base>.json

⚠️  IMPORTANTE:
   A primeira chamada ligou o relógio simulado.
   Reinicie o servidor antes de usar os agentes.

======================================================================
```

### 3. Reiniciar Servidor

**IMPORTANTE**: A primeira chamada ao servidor liga o relógio simulado. Você deve reiniciar o servidor antes de usar os agentes.

```bash
# Parar o servidor (Ctrl+C)
# Reiniciar o servidor
```

## Arquivos Gerados

### docs/ferramentas.json

Lista de ferramentas disponíveis no servidor.

```json
{
  "proximo_evento": {
    "description": "Obtém o próximo evento da fila",
    "parameters": {
      "esperar_segundos": {
        "type": "integer",
        "description": "Segundos para esperar"
      }
    }
  },
  "listar_bases": {
    "description": "Lista as bases disponíveis",
    "parameters": {
      "agente": {
        "type": "string",
        "description": "Nome do agente"
      }
    }
  },
  ...
}
```

### docs/bases.json

Metadados de todas as bases disponíveis.

```json
{
  "contratados": {
    "campos": ["id", "nome", "cpf", "cargo", ...],
    "campos_para_registrar": ["nome", "cpf", "cargo", ...],
    "campos_alteraveis": ["cargo", "data_inicio", ...]
  },
  "admissoes": {
    "campos": ["id", "contratado_id", "status", ...],
    "campos_para_registrar": ["contratado_id", "status", ...],
    "campos_alteraveis": ["status", ...]
  },
  ...
}
```

### docs/exemplos/<base>.json

Exemplos de registros de cada base (até 3 registros).

```json
[
  {
    "id": "CONT-001",
    "nome": "João Silva",
    "cpf": "123.456.789-00",
    "cargo": "Desenvolvedor",
    "data_inicio": "2024-01-15",
    ...
  },
  {
    "id": "CONT-002",
    "nome": "Maria Santos",
    "cpf": "987.654.321-00",
    "cargo": "Designer",
    "data_inicio": "2024-01-20",
    ...
  },
  ...
]
```

## Scripts Disponíveis

### testar_conexao.py

Testa a conexão com o servidor MCP.

```bash
python scripts/testar_conexao.py
```

**Quando usar**: Antes de executar descobrir_mundo_http.py

### descobrir_mundo_http.py

Descobre ferramentas e bases usando HTTP direto.

```bash
python scripts/descobrir_mundo_http.py
```

**Quando usar**: Descoberta inicial do servidor

**Vantagens**:
- Usa httpx (mais simples)
- Faz chamadas HTTP diretas
- Não requer pacote mcp

### descobrir_mundo.py

Descobre ferramentas e bases usando o pacote mcp.

```bash
python scripts/descobrir_mundo.py
```

**Quando usar**: Se preferir usar o pacote mcp oficial

**Vantagens**:
- Usa pacote mcp oficial
- Mais robusto para protocolos complexos

## Troubleshooting

### Erro: "Conexão recusada"

O servidor MCP não está rodando.

**Solução**:
1. Verifique se o servidor está iniciado
2. Verifique a URL: http://localhost:8765/mcp
3. Verifique a porta: 8765

### Erro: "Timeout"

O servidor está demorando para responder.

**Solução**:
1. Verifique se o servidor está saudável
2. Aumente o timeout no script (padrão: 15s)
3. Verifique a carga do servidor

### Erro: "Pacote 'httpx' não instalado"

Dependências não instaladas.

**Solução**:
```bash
pip install -r requirements.txt
```

### Erro: "Relógio simulado já ligado"

Você executou o script mais de uma vez sem reiniciar o servidor.

**Solução**:
1. Reinicie o servidor
2. Execute o script novamente

## Próximos Passos

Após descobrir o mundo:

1. **Revisar dados**: Examine os arquivos gerados em docs/
2. **Atualizar documentação**: Atualize docs/regras_negocio.md com base nos dados
3. **Implementar agentes**: Use os dados para implementar os agentes
4. **Testar agentes**: Execute os agentes contra o servidor

## Referências

- [Servidor MCP](http://localhost:8765/mcp)
- [Documentação de Regras de Negócio](docs/regras_negocio.md)
- [Prompts dos Agentes](docs/prompts_agentes.md)
- [Scripts](scripts/README.md)
