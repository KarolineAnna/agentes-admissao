# Checklist de Descoberta do Mundo MCP

Checklist para executar a descoberta do servidor MCP de forma segura e completa.

## Preparação

- [ ] Servidor MCP está instalado e pronto para iniciar
- [ ] Porta 8765 está disponível (não há outro serviço usando)
- [ ] Python 3.11+ está instalado
- [ ] Dependências instaladas: `pip install -r requirements.txt`
- [ ] Variáveis de ambiente configuradas (se necessário)

## Execução

### Fase 1: Teste de Conexão

- [ ] Inicie o servidor MCP (recém-iniciado, relógio parado)
- [ ] Execute: `python scripts/testar_conexao.py`
- [ ] Verifique saída: "✓ Conexão bem-sucedida!"
- [ ] Se falhar, verifique:
  - [ ] Servidor está rodando?
  - [ ] URL correta: http://localhost:8765/mcp
  - [ ] Porta 8765 está aberta?
  - [ ] Firewall não está bloqueando?

### Fase 2: Descoberta

- [ ] Execute: `python scripts/descobrir_mundo_http.py`
- [ ] Aguarde conclusão (pode levar alguns minutos)
- [ ] Verifique saída: "✓ Conexão bem-sucedida!"
- [ ] Verifique saída: "Arquivos salvos:"
  - [ ] docs/ferramentas.json
  - [ ] docs/bases.json
  - [ ] docs/exemplos/<base>.json

### Fase 3: Verificação de Arquivos

- [ ] Verifique docs/ferramentas.json
  - [ ] Contém lista de ferramentas?
  - [ ] Cada ferramenta tem nome, descrição, parâmetros?
  - [ ] Ferramentas esperadas estão presentes?
    - [ ] proximo_evento
    - [ ] listar_bases
    - [ ] consultar
    - [ ] registrar
    - [ ] atualizar
    - [ ] enviar_mensagem
    - [ ] responder_evento
    - [ ] (outras)

- [ ] Verifique docs/bases.json
  - [ ] Contém lista de bases?
  - [ ] Cada base tem campos, campos_para_registrar, campos_alteraveis?
  - [ ] Bases esperadas estão presentes?
    - [ ] contratados
    - [ ] admissoes
    - [ ] checklist
    - [ ] documentos
    - [ ] areas
    - [ ] faq
    - [ ] (outras)

- [ ] Verifique docs/exemplos/
  - [ ] Contém um arquivo JSON por base?
  - [ ] Cada arquivo contém até 3 registros?
  - [ ] Registros têm estrutura esperada?
  - [ ] Dados fazem sentido?

### Fase 4: Reinicialização do Servidor

- [ ] **IMPORTANTE**: Reinicie o servidor MCP
  - [ ] Parar servidor (Ctrl+C)
  - [ ] Aguarde 2-3 segundos
  - [ ] Reinicie o servidor
- [ ] Verifique que servidor iniciou com sucesso
- [ ] Verifique que relógio está em 08:00 (início do dia)

## Validação

- [ ] Todos os arquivos foram gerados?
- [ ] Todos os arquivos têm conteúdo válido (JSON)?
- [ ] Nenhum arquivo está vazio?
- [ ] Nenhum arquivo tem erros de sintaxe?

Teste com:
```bash
python -m json.tool docs/ferramentas.json > /dev/null && echo "✓ ferramentas.json OK"
python -m json.tool docs/bases.json > /dev/null && echo "✓ bases.json OK"
for f in docs/exemplos/*.json; do python -m json.tool "$f" > /dev/null && echo "✓ $f OK"; done
```

## Próximos Passos

- [ ] Revisar docs/ferramentas.json
- [ ] Revisar docs/bases.json
- [ ] Revisar docs/exemplos/
- [ ] Atualizar documentação (regras_negocio.md, prompts_agentes.md)
- [ ] Implementar core/mcp_cliente.py com base nas ferramentas
- [ ] Implementar agentes com base nas bases e exemplos
- [ ] Testar agentes contra o servidor

## Troubleshooting

### Problema: "Conexão recusada"

**Causa**: Servidor MCP não está rodando

**Solução**:
1. Verifique se servidor está iniciado
2. Verifique URL: http://localhost:8765/mcp
3. Verifique porta: 8765
4. Verifique firewall

### Problema: "Timeout"

**Causa**: Servidor está demorando para responder

**Solução**:
1. Verifique saúde do servidor
2. Aumente timeout no script (padrão: 15s)
3. Verifique carga do servidor
4. Tente novamente

### Problema: "Relógio simulado já ligado"

**Causa**: Você executou o script mais de uma vez sem reiniciar

**Solução**:
1. Reinicie o servidor
2. Execute o script novamente

### Problema: "Arquivo vazio ou inválido"

**Causa**: Erro durante descoberta

**Solução**:
1. Verifique logs do script
2. Verifique resposta do servidor
3. Tente novamente
4. Se persistir, verifique servidor

## Notas

- A primeira chamada ao servidor liga o relógio simulado
- Você DEVE reiniciar o servidor depois de executar o script
- Não execute o script mais de uma vez sem reiniciar
- Se algo der errado, reinicie o servidor e tente novamente
- Mantenha os arquivos gerados para referência

## Referências

- [DESCOBERTA_MUNDO.md](DESCOBERTA_MUNDO.md): Guia completo
- [scripts/README.md](scripts/README.md): Documentação dos scripts
- [docs/regras_negocio.md](docs/regras_negocio.md): Regras de negócio
- [docs/prompts_agentes.md](docs/prompts_agentes.md): Prompts dos agentes
