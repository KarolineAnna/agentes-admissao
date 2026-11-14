# Índice de Scripts de Descoberta

Índice completo de todos os scripts e documentação criados para descobrir o servidor MCP.

## 📁 Estrutura de Arquivos

```
agentes-admissao/
├── scripts/
│   ├── __init__.py                    # Módulo Python
│   ├── testar_conexao.py              # Teste rápido de conexão
│   ├── descobrir_mundo.py             # Descoberta (versão MCP)
│   ├── descobrir_mundo_http.py        # Descoberta (versão HTTP - RECOMENDADO)
│   ├── exemplo_uso.sh                 # Exemplo de uso
│   ├── README.md                      # Documentação dos scripts
│   └── TECNICO.md                     # Documentação técnica
│
├── docs/
│   ├── exemplos/                      # Diretório para exemplos (criado em runtime)
│   ├── ferramentas.json               # Ferramentas (gerado em runtime)
│   ├── bases.json                     # Bases (gerado em runtime)
│   └── exemplos/<base>.json           # Exemplos por base (gerado em runtime)
│
├── DESCOBERTA_MUNDO.md                # Guia completo de uso
├── CHECKLIST_DESCOBERTA.md            # Checklist de execução
└── INDICE_SCRIPTS.md                  # Este arquivo
```

## 🚀 Guia Rápido

### 1. Testar Conexão

```bash
python scripts/testar_conexao.py
```

**O que faz**: Testa se o servidor MCP está respondendo

**Quando usar**: Antes de descobrir_mundo_http.py

**Saída esperada**: "✓ Conexão bem-sucedida!"

### 2. Descobrir Mundo (RECOMENDADO)

```bash
python scripts/descobrir_mundo_http.py
```

**O que faz**: Descobre ferramentas e bases do servidor

**Quando usar**: Descoberta inicial

**Gera**: 
- docs/ferramentas.json
- docs/bases.json
- docs/exemplos/<base>.json

### 3. Alternativa: Descobrir Mundo (MCP)

```bash
python scripts/descobrir_mundo.py
```

**O que faz**: Mesmo que descobrir_mundo_http.py, mas usando pacote mcp

**Quando usar**: Se preferir usar pacote mcp oficial

## 📖 Documentação

### DESCOBERTA_MUNDO.md

Guia completo de uso dos scripts.

**Contém**:
- Visão geral
- Procedimento passo a passo
- Descrição dos arquivos gerados
- Troubleshooting
- Próximos passos

**Quando ler**: Antes de usar os scripts

### CHECKLIST_DESCOBERTA.md

Checklist detalhado para executar a descoberta com segurança.

**Contém**:
- Preparação
- Execução (4 fases)
- Validação
- Próximos passos
- Troubleshooting

**Quando usar**: Durante a execução dos scripts

### scripts/README.md

Documentação dos scripts.

**Contém**:
- Descrição de cada script
- Como usar
- O que faz
- Saída esperada
- Dependências
- Troubleshooting

**Quando ler**: Para entender cada script

### scripts/TECNICO.md

Documentação técnica detalhada.

**Contém**:
- Arquitetura
- Fluxo de execução
- Detalhes de implementação
- Estrutura de dados
- Tratamento de erros
- Logging
- Performance
- Segurança

**Quando ler**: Para entender a implementação técnica

## 📊 Arquivos Gerados

### docs/ferramentas.json

Lista de ferramentas disponíveis no servidor.

```json
{
  "ferramenta1": {
    "description": "Descrição",
    "parameters": {...}
  },
  ...
}
```

### docs/bases.json

Metadados de todas as bases.

```json
{
  "base1": {
    "campos": [...],
    "campos_para_registrar": [...],
    "campos_alteraveis": [...]
  },
  ...
}
```

### docs/exemplos/<base>.json

Exemplos de registros de cada base.

```json
[
  {"id": "...", "campo1": "...", ...},
  ...
]
```

## 🔧 Scripts Detalhados

### testar_conexao.py

**Tamanho**: 3.6 KB

**Responsabilidades**:
- Testar conexão com servidor MCP
- Tentar GET /ping
- Tentar POST com ação="ping"
- Tentar POST com ação="listar_bases"

**Uso**:
```bash
python scripts/testar_conexao.py
```

**Saída**:
```
✓ Conexão bem-sucedida!
ou
✗ Falha na conexão!
```

### descobrir_mundo_http.py (RECOMENDADO)

**Tamanho**: 13.3 KB

**Responsabilidades**:
- Conectar ao servidor MCP
- Descobrir ferramentas (opcional)
- Listar bases
- Descobrir exemplos para cada base
- Salvar resultados em JSON
- Imprimir resumo

**Uso**:
```bash
python scripts/descobrir_mundo_http.py
```

**Gera**:
- docs/ferramentas.json
- docs/bases.json
- docs/exemplos/<base>.json

**Vantagens**:
- Usa httpx (mais simples)
- Faz chamadas HTTP diretas
- Não requer pacote mcp

### descobrir_mundo.py

**Tamanho**: 10 KB

**Responsabilidades**:
- Mesmo que descobrir_mundo_http.py
- Mas usando pacote mcp

**Uso**:
```bash
python scripts/descobrir_mundo.py
```

**Vantagens**:
- Usa pacote mcp oficial
- Mais robusto para protocolos complexos

### exemplo_uso.sh

**Tamanho**: 2.5 KB

**Responsabilidades**:
- Exemplo de como usar os scripts
- Passo a passo com explicações

**Uso**:
```bash
bash scripts/exemplo_uso.sh
```

## ⚠️ Avisos Importantes

### Relógio Simulado

A primeira chamada ao servidor liga o relógio simulado.

**O que fazer**:
1. Execute o script de descoberta
2. Reinicie o servidor
3. Agora o relógio começará do zero

**Por quê**: Garante que os agentes comecem com o relógio sincronizado

### Ordem de Execução

1. testar_conexao.py (teste)
2. descobrir_mundo_http.py (descoberta)
3. Reiniciar servidor
4. Usar agentes

**Não faça**:
- Executar descobrir_mundo_http.py sem testar conexão primeiro
- Usar agentes sem reiniciar servidor depois
- Executar descobrir_mundo_http.py mais de uma vez sem reiniciar

## 🔍 Troubleshooting

### "Conexão recusada"

**Causa**: Servidor MCP não está rodando

**Solução**:
1. Verifique se servidor está iniciado
2. Verifique URL: http://localhost:8765/mcp
3. Verifique porta: 8765

### "Timeout"

**Causa**: Servidor está demorando para responder

**Solução**:
1. Verifique saúde do servidor
2. Aumente timeout no script
3. Tente novamente

### "Relógio simulado já ligado"

**Causa**: Executou script mais de uma vez sem reiniciar

**Solução**:
1. Reinicie o servidor
2. Execute o script novamente

## 📚 Referências

- [DESCOBERTA_MUNDO.md](DESCOBERTA_MUNDO.md): Guia completo
- [CHECKLIST_DESCOBERTA.md](CHECKLIST_DESCOBERTA.md): Checklist
- [scripts/README.md](scripts/README.md): Documentação dos scripts
- [scripts/TECNICO.md](scripts/TECNICO.md): Documentação técnica
- [docs/regras_negocio.md](docs/regras_negocio.md): Regras de negócio
- [docs/prompts_agentes.md](docs/prompts_agentes.md): Prompts dos agentes

## 📞 Suporte

Se tiver dúvidas:

1. Leia [DESCOBERTA_MUNDO.md](DESCOBERTA_MUNDO.md)
2. Consulte [CHECKLIST_DESCOBERTA.md](CHECKLIST_DESCOBERTA.md)
3. Verifique [scripts/README.md](scripts/README.md)
4. Leia [scripts/TECNICO.md](scripts/TECNICO.md)

## ✅ Checklist de Uso

- [ ] Servidor MCP iniciado (recém-iniciado)
- [ ] Executou testar_conexao.py
- [ ] Conexão bem-sucedida
- [ ] Executou descobrir_mundo_http.py
- [ ] Arquivos gerados em docs/
- [ ] Reiniciou o servidor
- [ ] Pronto para usar agentes

## 🎯 Próximos Passos

Após descobrir o mundo:

1. Revisar docs/ferramentas.json
2. Revisar docs/bases.json
3. Revisar docs/exemplos/
4. Atualizar documentação
5. Implementar core/mcp_cliente.py
6. Implementar agentes
7. Testar agentes

---

**Última atualização**: 2024-01-15  
**Versão**: 1.0  
**Status**: Pronto para uso
