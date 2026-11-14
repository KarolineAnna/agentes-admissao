#!/bin/bash
# Script de exemplo: como usar os scripts de descoberta

echo "========================================================================"
echo "EXEMPLO DE USO: DESCOBERTA DO MUNDO MCP"
echo "========================================================================"
echo ""

# Passo 1: Testar conexão
echo "Passo 1: Testando conexão com o servidor MCP..."
echo "Comando: python scripts/testar_conexao.py"
echo ""
echo "Saída esperada:"
echo "  ✓ Conexão bem-sucedida!"
echo ""
echo "Se falhar, verifique:"
echo "  • Servidor MCP está rodando?"
echo "  • URL correta: http://localhost:8765/mcp"
echo "  • Porta 8765 está aberta?"
echo ""

# Passo 2: Descobrir mundo
echo "Passo 2: Descobrindo ferramentas e bases..."
echo "Comando: python scripts/descobrir_mundo_http.py"
echo ""
echo "Saída esperada:"
echo "  ========================================================================"
echo "  RESUMO DA DESCOBERTA DO MUNDO MCP"
echo "  ========================================================================"
echo "  📡 Servidor: http://localhost:8765/mcp"
echo "  🔧 Ferramentas (X):"
echo "  📊 Bases (X):"
echo "  📋 Exemplos (X):"
echo "  📁 Arquivos salvos:"
echo "  ⚠️  IMPORTANTE: Reinicie o servidor antes de usar os agentes"
echo ""

# Passo 3: Verificar arquivos
echo "Passo 3: Verificando arquivos gerados..."
echo "Comando: ls -la docs/ferramentas.json docs/bases.json docs/exemplos/"
echo ""
echo "Saída esperada:"
echo "  docs/ferramentas.json (lista de ferramentas)"
echo "  docs/bases.json (metadados das bases)"
echo "  docs/exemplos/contratados.json (exemplos)"
echo "  docs/exemplos/admissoes.json (exemplos)"
echo "  ... (mais bases)"
echo ""

# Passo 4: Reiniciar servidor
echo "Passo 4: Reiniciando o servidor..."
echo "Comando: (parar servidor com Ctrl+C e reiniciar)"
echo ""
echo "Por quê? A primeira chamada ligou o relógio simulado."
echo "Você precisa reiniciar para que o relógio comece do zero."
echo ""

# Passo 5: Usar os dados
echo "Passo 5: Usando os dados nos agentes..."
echo "Agora você pode:"
echo "  • Revisar docs/ferramentas.json para entender as ações disponíveis"
echo "  • Revisar docs/bases.json para entender a estrutura dos dados"
echo "  • Revisar docs/exemplos/ para ver exemplos de dados"
echo "  • Implementar os agentes usando esses dados"
echo ""

echo "========================================================================"
echo "FIM DO EXEMPLO"
echo "========================================================================"
