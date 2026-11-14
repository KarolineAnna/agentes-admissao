"""
Script para testar conexão com o servidor MCP.

Uso:
    python scripts/testar_conexao.py
"""

import asyncio
import json
import logging
import sys
from typing import Optional

try:
    import httpx
except ImportError:
    print("Erro: httpx não instalado. Execute: pip install httpx")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def testar_conexao(url: str = "http://localhost:8765/mcp") -> bool:
    """
    Testa conexão com o servidor MCP.

    Args:
        url: URL do servidor MCP

    Returns:
        True se conectado com sucesso, False caso contrário
    """
    try:
        logger.info(f"Testando conexão com {url}...")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Tentar GET /ping
            try:
                response = await client.get(f"{url}/ping")
                logger.info(f"✓ GET /ping: {response.status_code}")
            except Exception as e:
                logger.warning(f"✗ GET /ping falhou: {e}")
            
            # Tentar POST com ação vazia
            try:
                payload = {
                    "acao": "ping",
                    "agente": "teste",
                    "motivo": "Teste de conexão"
                }
                response = await client.post(url, json=payload)
                logger.info(f"✓ POST (ping): {response.status_code}")
                
                if response.status_code == 200:
                    dados = response.json()
                    logger.info(f"  Resposta: {json.dumps(dados, indent=2)}")
                    return True
            except Exception as e:
                logger.warning(f"✗ POST (ping) falhou: {e}")
            
            # Tentar listar_bases
            try:
                payload = {
                    "acao": "listar_bases",
                    "agente": "teste",
                    "motivo": "Teste de conexão"
                }
                response = await client.post(url, json=payload)
                logger.info(f"✓ POST (listar_bases): {response.status_code}")
                
                if response.status_code == 200:
                    dados = response.json()
                    if dados.get("status") == "ok":
                        bases = dados.get("bases", {})
                        logger.info(f"  Bases encontradas: {len(bases)}")
                        for nome in list(bases.keys())[:3]:
                            logger.info(f"    • {nome}")
                        return True
            except Exception as e:
                logger.warning(f"✗ POST (listar_bases) falhou: {e}")
        
        return False
    except Exception as e:
        logger.error(f"✗ Erro ao testar conexão: {e}")
        return False


async def main():
    """Função principal."""
    print("\n" + "=" * 70)
    print("TESTE DE CONEXÃO COM SERVIDOR MCP")
    print("=" * 70 + "\n")
    
    sucesso = await testar_conexao()
    
    if sucesso:
        print("\n✓ Conexão bem-sucedida!")
        print("\nVocê pode agora executar:")
        print("  python scripts/descobrir_mundo_http.py")
    else:
        print("\n✗ Falha na conexão!")
        print("\nVerifique se o servidor está rodando:")
        print("  • URL: http://localhost:8765/mcp")
        print("  • Porta: 8765")
        print("  • Protocolo: HTTP")
    
    print("\n" + "=" * 70 + "\n")
    sys.exit(0 if sucesso else 1)


if __name__ == "__main__":
    asyncio.run(main())
