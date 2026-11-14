# Quick Start: Scripts de Descoberta

Guia rápido para começar a usar os scripts de descoberta.

## ⚡ 5 Minutos para Começar

### 1. Testar Conexão (1 minuto)

```bash
python scripts/testar_conexao.py
```

**Esperado**: `✓ Conexão bem-sucedida!`

**Se falhar**: Verifique se o servidor MCP está rodando em `http://localhost:8765/mcp`

### 2. Descobrir Mundo (2-3 minutos)

```bash
python scripts/descobrir_mundo_http.py
```

**Esperado**: Resumo com ferramentas, bases e exemplos

**Gera**:
- `docs/ferramentas.json`
- `docs/bases.json`
- `docs/exemplos/<base>.json`

### 3. Verificar Arquivos (1 minuto)

```bash
# Linux/Mac
ls -la docs/ferramentas.json docs/bases.json docs/exemplos/

# Windows
dir docs\ferramentas.json docs\bases.json docs\exemplos\
```

### 4. Reiniciar Servidor (1 minuto)

⚠️ **IMPORTANTE**: Reinicie o servidor MCP agora!

```bash
# Parar servidor (Ctrl+C)
# Aguarde 2-3 segundos
# Reinicie o servidor
```

## 📖 Próximas Leituras

1. **RESUMO_SCRIPTS.md** (2 min): Visão geral
2. **INDICE_SCRIPTS.md** (5 min): Índice completo
3. **DESCOBERTA_MUNDO.md** (10 min): Guia detalhado

## 🔧 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| "Conexão recusada" | Inicie o servidor MCP |
| "Timeout" | Aguarde o servidor responder |
| "Relógio já ligado" | Reinicie o servidor |

## ✅ Checklist

- [ ] Servidor MCP iniciado
- [ ] Executou testar_conexao.py
- [ ] Conexão bem-sucedida
- [ ] Executou descobrir_mundo_http.py
- [ ] Arquivos gerados em docs/
- [ ] Reiniciou o servidor
- [ ] Pronto para implementar agentes

## 📚 Documentação Completa

- [RESUMO_SCRIPTS.md](RESUMO_SCRIPTS.md): Resumo visual
- [INDICE_SCRIPTS.md](INDICE_SCRIPTS.md): Índice completo
- [DESCOBERTA_MUNDO.md](DESCOBERTA_MUNDO.md): Guia detalhado
- [CHECKLIST_DESCOBERTA.md](CHECKLIST_DESCOBERTA.md): Checklist
- [scripts/README.md](scripts/README.md): Docs dos scripts
- [scripts/TECNICO.md](scripts/TECNICO.md): Docs técnicas

## 🚀 Próximos Passos

Após descobrir o mundo:

1. Revisar `docs/ferramentas.json`
2. Revisar `docs/bases.json`
3. Revisar `docs/exemplos/`
4. Implementar `core/mcp_cliente.py`
5. Implementar agentes

---

**Tempo total**: ~5 minutos  
**Dificuldade**: Fácil  
**Status**: ✅ Pronto
