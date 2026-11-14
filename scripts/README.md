# Scripts Utilitários

Scripts para auxiliar no desenvolvimento e descoberta do servidor MCP.

## descobrir_mundo.py

Descobre ferramentas e bases do servidor MCP usando o pacote `mcp`.

### Uso

```bash
python scripts/descobrir_mundo.py
```

### O que faz

1. Conecta ao servidor MCP em `http://localhost:8765/mcp`
2. Lista as ferramentas disponíveis e salva em `docs/ferramentas.json`
3. Chama `listar_bases` com `agente="setup"` e salva em `docs/bases.json`
4. Para cada base, chama `consultar` com `limite=3` e salva exemplos em `docs/exemplos/<base>.json`

### Saída

```
======================================================================
RESUMO DA DESCOBERTA DO MUNDO MCP
======================================================================

📡 Servidor: http://localhost:8765/mcp

🔧 Ferramentas (X):
   • ferramenta1: Descrição...
   • ferramenta2: Descrição...

📊 Bases (X):
   • base1: N campos
     Campos: campo1, campo2, campo3...
   • base2: N campos

📋 Exemplos (X):
   • base1: N registros
   • base2: N registros

📁 Arquivos salvos:
   • docs/ferramentas.json
   • docs/bases.json
   • docs/exemplos/<base>.json

⚠️  IMPORTANTE:
   A primeira chamada ligou o relógio simulado.
   Reinicie o servidor antes de usar os agentes.

======================================================================
```

## descobrir_mundo_http.py

Versão alternativa que usa `httpx` para fazer chamadas HTTP diretas ao servidor MCP.

### Uso

```bash
python scripts/descobrir_mundo_http.py
```

### Diferenças

- Usa `httpx` em vez do pacote `mcp`
- Faz chamadas HTTP diretas ao servidor
- Mais simples e direto

## ⚠️ IMPORTANTE

**A primeira chamada liga o relógio simulado do servidor.**

Siga este procedimento:

1. Inicie o servidor MCP recém-iniciado (relógio parado)
2. Execute o script de descoberta
3. **Reinicie o servidor** antes de usar os agentes

Isso garante que o relógio simulado comece do zero quando os agentes iniciarem.

## Arquivos Gerados

### docs/ferramentas.json

Lista de ferramentas disponíveis no servidor com nome, descrição e parâmetros.

```json
{
  "ferramenta1": {
    "description": "Descrição da ferramenta",
    "parameters": {
      "param1": {"type": "string", "description": "Descrição do parâmetro"}
    }
  }
}
```

### docs/bases.json

Metadados de todas as bases disponíveis.

```json
{
  "base1": {
    "campos": ["campo1", "campo2", "campo3"],
    "campos_para_registrar": ["campo1", "campo2"],
    "campos_alteraveis": ["campo2"]
  }
}
```

### docs/exemplos/<base>.json

Exemplos de registros de cada base (até 3 registros).

```json
[
  {
    "id": "...",
    "campo1": "valor1",
    "campo2": "valor2"
  }
]
```

## Dependências

- `httpx` (para descobrir_mundo_http.py)
- `mcp` (para descobrir_mundo.py)

Instale com:

```bash
pip install httpx mcp
```

## Troubleshooting

### Erro: "Conexão recusada"

O servidor MCP não está rodando. Inicie-o em outro terminal:

```bash
# Assumindo que o servidor está em um repositório local
cd ../servidor-mcp
npm start
```

### Erro: "Pacote 'httpx' não instalado"

Instale as dependências:

```bash
pip install -r requirements.txt
```

### Erro: "Timeout"

O servidor está demorando para responder. Aumente o timeout no script ou verifique se o servidor está saudável.
