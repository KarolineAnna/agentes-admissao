# 🌍 Scripts de Descoberta do Mundo MCP

Ferramentas para descobrir e documentar as capacidades do servidor MCP.

## ⚡ Quick Start (5 minutos)

```bash
# 1. Teste de conexão
python scripts/testar_conexao.py

# 2. Descobrir mundo
python scripts/descobrir_mundo_http.py

# 3. Reinicie o servidor MCP
# ⚠️ IMPORTANTE!
```

## 📚 Documentação

| Documento | Tempo | Conteúdo |
|-----------|-------|----------|
| [QUICK_START.md](QUICK_START.md) | 2 min | Guia rápido |
| [SUMARIO_FINAL.md](SUMARIO_FINAL.md) | 5 min | Sumário completo |
| [INDICE_ARQUIVOS.md](INDICE_ARQUIVOS.md) | 5 min | Índice de arquivos |
| [MAPA_NAVEGACAO.md](MAPA_NAVEGACAO.md) | 5 min | Mapa de navegação |
| [DESCOBERTA_MUNDO.md](DESCOBERTA_MUNDO.md) | 15 min | Guia detalhado |
| [CHECKLIST_DESCOBERTA.md](CHECKLIST_DESCOBERTA.md) | 5 min | Checklist |
| [scripts/README.md](scripts/README.md) | 5 min | Docs dos scripts |
| [scripts/TECNICO.md](scripts/TECNICO.md) | 10 min | Docs técnicas |

## 🔧 Scripts Disponíveis

### 1. testar_conexao.py
Teste rápido de conexão com o servidor.

```bash
python scripts/testar_conexao.py
```

**Esperado**: `✓ Conexão bem-sucedida!`

### 2. descobrir_mundo_http.py ⭐ RECOMENDADO
Descobre ferramentas e bases usando HTTP.

```bash
python scripts/descobrir_mundo_http.py
```

**Gera**:
- `docs/ferramentas.json`
- `docs/bases.json`
- `docs/exemplos/<base>.json`

### 3. descobrir_mundo.py
Descobre ferramentas e bases usando MCP package.

```bash
python scripts/descobrir_mundo.py
```

**Nota**: Mais robusto, mas mais complexo.

## 📊 O Que Será Gerado

```
docs/
├── ferramentas.json          # Ferramentas disponíveis
├── bases.json                # Bases de dados
└── exemplos/
    ├── contratados.json
    ├── admissoes.json
    ├── checklist.json
    ├── documentos_exigidos.json
    ├── areas.json
    └── faq.json
```

## ⚠️ Avisos Importantes

### 🔴 CRÍTICO
- **A primeira chamada ao servidor liga o relógio simulado**
- **Você DEVE reiniciar o servidor depois de executar o script**
- **Não execute o script mais de uma vez sem reiniciar**

### 🟡 IMPORTANTE
- Se algo der errado, reinicie o servidor e tente novamente
- O relógio simulado é acelerado (1 hora = 12 segundos reais)
- Cada execução do script avança o relógio

## 🎯 Procedimento Completo

```
1. Inicie o servidor MCP (recém-iniciado)
   └─ Relógio parado em 08:00

2. Execute: python scripts/testar_conexao.py
   └─ Testa conexão com servidor

3. Execute: python scripts/descobrir_mundo_http.py
   └─ Descobre ferramentas e bases
   └─ Gera: docs/ferramentas.json, docs/bases.json, docs/exemplos/

4. Verifique arquivos gerados
   └─ ls -la docs/ferramentas.json docs/bases.json docs/exemplos/

5. Reinicie o servidor MCP
   └─ ⚠️ IMPORTANTE! Relógio começará do zero
```

## 🔍 Troubleshooting

| Problema | Solução |
|----------|---------|
| "Conexão recusada" | Inicie o servidor MCP |
| "Timeout" | Aguarde o servidor responder |
| "Relógio já ligado" | Reinicie o servidor |
| "Arquivo não encontrado" | Verifique o caminho |

## 📈 Estatísticas

- **7 scripts** Python/Shell
- **9 arquivos** de documentação
- **~90 KB** de código e documentação
- **~50 minutos** de leitura
- **~5 minutos** de execução

## ✨ Próximos Passos

Após descobrir o mundo:

1. Revisar `docs/ferramentas.json`
2. Revisar `docs/bases.json`
3. Revisar `docs/exemplos/`
4. Implementar `core/mcp_cliente.py`
5. Implementar agentes

## 📞 Suporte

Se tiver dúvidas:

1. Leia [QUICK_START.md](QUICK_START.md)
2. Leia [DESCOBERTA_MUNDO.md](DESCOBERTA_MUNDO.md)
3. Consulte [CHECKLIST_DESCOBERTA.md](CHECKLIST_DESCOBERTA.md)
4. Revise [scripts/README.md](scripts/README.md)

---

**Status**: ✅ Pronto para uso  
**Versão**: 1.0  
**Data**: 2024-01-15
