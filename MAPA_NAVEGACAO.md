# 🗺️ Mapa de Navegação - Scripts de Descoberta

Guia visual para navegar pela documentação e scripts.

## 📍 Você está aqui

```
agentes-admissao/
├── QUICK_START.md ⭐ COMECE AQUI (2 min)
├── MAPA_NAVEGACAO.md (você está aqui)
├── RESUMO_SCRIPTS.md (5 min)
├── INDICE_SCRIPTS.md (10 min)
├── DESCOBERTA_MUNDO.md (15 min)
├── CHECKLIST_DESCOBERTA.md (checklist)
└── scripts/
    ├── testar_conexao.py
    ├── descobrir_mundo_http.py ⭐ RECOMENDADO
    ├── descobrir_mundo.py
    ├── exemplo_uso.sh
    ├── README.md
    └── TECNICO.md
```

## 🎯 Fluxo de Leitura Recomendado

### Iniciante (15 minutos)
```
1. QUICK_START.md (2 min)
   └─ Entender o que fazer
   
2. RESUMO_SCRIPTS.md (5 min)
   └─ Ver o que foi criado
   
3. Executar scripts (5 min)
   └─ python scripts/testar_conexao.py
   └─ python scripts/descobrir_mundo_http.py
   
4. Reiniciar servidor (1 min)
   └─ ⚠️ IMPORTANTE
```

### Intermediário (30 minutos)
```
1. QUICK_START.md (2 min)
2. RESUMO_SCRIPTS.md (5 min)
3. INDICE_SCRIPTS.md (10 min)
   └─ Entender estrutura completa
4. scripts/README.md (5 min)
   └─ Detalhes dos scripts
5. Executar e verificar (8 min)
```

### Avançado (45 minutos)
```
1. DESCOBERTA_MUNDO.md (15 min)
   └─ Guia detalhado
2. scripts/TECNICO.md (10 min)
   └─ Documentação técnica
3. CHECKLIST_DESCOBERTA.md (5 min)
   └─ Checklist de execução
4. Revisar código dos scripts (15 min)
   └─ Entender implementação
```

## 📚 Documentação por Tópico

### Começar Rápido
- **QUICK_START.md**: Guia de 5 minutos
- **RESUMO_SCRIPTS.md**: Resumo visual

### Entender Tudo
- **INDICE_SCRIPTS.md**: Índice completo
- **DESCOBERTA_MUNDO.md**: Guia detalhado
- **CHECKLIST_DESCOBERTA.md**: Checklist

### Detalhes Técnicos
- **scripts/README.md**: Documentação dos scripts
- **scripts/TECNICO.md**: Documentação técnica

## 🚀 Procedimento Passo a Passo

```
┌─────────────────────────────────────────────────────────┐
│ PASSO 1: Ler QUICK_START.md (2 min)                     │
│ └─ Entender o que fazer                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ PASSO 2: Iniciar servidor MCP (recém-iniciado)          │
│ └─ Relógio parado em 08:00                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ PASSO 3: Executar testar_conexao.py                     │
│ └─ python scripts/testar_conexao.py                     │
│ └─ Esperado: ✓ Conexão bem-sucedida!                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ PASSO 4: Executar descobrir_mundo_http.py               │
│ └─ python scripts/descobrir_mundo_http.py               │
│ └─ Gera: docs/ferramentas.json, docs/bases.json         │
│ └─ Gera: docs/exemplos/<base>.json                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ PASSO 5: Verificar arquivos gerados                     │
│ └─ ls -la docs/ferramentas.json docs/bases.json         │
│ └─ ls -la docs/exemplos/                                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ PASSO 6: Reiniciar servidor MCP                         │
│ └─ ⚠️ IMPORTANTE! Relógio começará do zero              │
│ └─ Aguarde 2-3 segundos                                 │
│ └─ Reinicie o servidor                                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ PASSO 7: Revisar documentação (opcional)                │
│ └─ RESUMO_SCRIPTS.md (5 min)                            │
│ └─ INDICE_SCRIPTS.md (10 min)                           │
│ └─ DESCOBERTA_MUNDO.md (15 min)                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ ✅ PRONTO PARA IMPLEMENTAR AGENTES                      │
└─────────────────────────────────────────────────────────┘
```

## 🔍 Encontrar Informações

### "Como começo?"
→ Leia [QUICK_START.md](QUICK_START.md)

### "O que foi criado?"
→ Leia [RESUMO_SCRIPTS.md](RESUMO_SCRIPTS.md)

### "Quero entender tudo"
→ Leia [INDICE_SCRIPTS.md](INDICE_SCRIPTS.md)

### "Preciso de detalhes técnicos"
→ Leia [scripts/TECNICO.md](scripts/TECNICO.md)

### "Qual script usar?"
→ Leia [scripts/README.md](scripts/README.md)

### "Tenho um problema"
→ Leia [DESCOBERTA_MUNDO.md](DESCOBERTA_MUNDO.md) seção Troubleshooting

### "Preciso de um checklist"
→ Leia [CHECKLIST_DESCOBERTA.md](CHECKLIST_DESCOBERTA.md)

## 📊 Matriz de Documentação

| Documento | Tempo | Nível | Conteúdo |
|-----------|-------|-------|----------|
| QUICK_START.md | 2 min | Iniciante | Guia rápido |
| RESUMO_SCRIPTS.md | 5 min | Iniciante | Resumo visual |
| INDICE_SCRIPTS.md | 10 min | Intermediário | Índice completo |
| DESCOBERTA_MUNDO.md | 15 min | Intermediário | Guia detalhado |
| scripts/README.md | 5 min | Intermediário | Docs dos scripts |
| scripts/TECNICO.md | 10 min | Avançado | Docs técnicas |
| CHECKLIST_DESCOBERTA.md | 5 min | Qualquer | Checklist |

## 🎓 Aprendizado Progressivo

### Nível 1: Iniciante
- Ler QUICK_START.md
- Executar scripts
- Verificar arquivos gerados

### Nível 2: Intermediário
- Ler RESUMO_SCRIPTS.md
- Ler INDICE_SCRIPTS.md
- Ler scripts/README.md
- Entender estrutura

### Nível 3: Avançado
- Ler DESCOBERTA_MUNDO.md
- Ler scripts/TECNICO.md
- Revisar código dos scripts
- Entender implementação

## ✅ Checklist de Leitura

- [ ] QUICK_START.md
- [ ] RESUMO_SCRIPTS.md
- [ ] INDICE_SCRIPTS.md
- [ ] DESCOBERTA_MUNDO.md
- [ ] scripts/README.md
- [ ] scripts/TECNICO.md
- [ ] CHECKLIST_DESCOBERTA.md

## 🚀 Próximos Passos

Após ler a documentação:

1. Executar scripts de descoberta
2. Revisar docs/ferramentas.json
3. Revisar docs/bases.json
4. Revisar docs/exemplos/
5. Implementar core/mcp_cliente.py
6. Implementar agentes

## 📞 Suporte

Se tiver dúvidas:

1. Procure no índice (INDICE_SCRIPTS.md)
2. Leia a seção relevante (DESCOBERTA_MUNDO.md)
3. Consulte o checklist (CHECKLIST_DESCOBERTA.md)
4. Revise o código (scripts/)

---

**Tempo total de leitura**: ~45 minutos  
**Tempo de execução**: ~5 minutos  
**Status**: ✅ Pronto
