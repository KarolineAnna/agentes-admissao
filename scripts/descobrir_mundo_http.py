"""
Script para descobrir ferramentas e bases do servidor MCP (versão HTTP).

Usa httpx para fazer chamadas HTTP diretas ao servidor MCP.

Responsabilidades:
1. Conecta ao servidor MCP em http://localhost:8765/mcp
2. Lista as ferramentas disponíveis e salva em docs/ferramentas.json
3. Chama listar_bases com agente="setup" e salva em docs/bases.json
4. Para cada base, chama consultar com limite=3 e salva exemplos em docs/exemplos/<base>.json

ATENÇÃO: A primeira chamada liga o relógio simulado. Rode isto com o servidor
recém-iniciado e reinicie o servidor depois.

Uso:
    python scripts/descobrir_mundo_http.py
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DescobritorMundoHTTP:
    """Descobre ferramentas e bases do servidor MCP usando HTTP."""

    def __init__(self, server_url: str = "http://localhost:8765/mcp"):
        """
        Inicializa o descobridor.

        Args:
            server_url: URL do servidor MCP
        """
        self.server_url = server_url
        self.client: Optional[httpx.AsyncClient] = None
        self.ferramentas: Dict[str, Any] = {}
        self.bases: Dict[str, Any] = {}
        self.exemplos: Dict[str, List[Dict[str, Any]]] = {}

    async def conectar(self) -> bool:
        """
        Conecta ao servidor MCP.

        Returns:
            True se conectado com sucesso, False caso contrário
        """
        try:
            logger.info(f"Conectando ao servidor MCP em {self.server_url}...")
            self.client = httpx.AsyncClient(timeout=15.0)
            
            # Testar conexão com um ping
            response = await self.client.get(f"{self.server_url}/ping")
            if response.status_code != 200:
                logger.warning(f"Servidor respondeu com status {response.status_code}")
            
            logger.info("✓ Conectado ao servidor MCP")
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao conectar: {e}")
            return False

    async def descobrir_ferramentas(self) -> bool:
        """
        Descobre ferramentas disponíveis no servidor.

        Returns:
            True se descoberto com sucesso, False caso contrário
        """
        try:
            logger.info("Descobrindo ferramentas disponíveis...")
            
            # TODO: Chamar endpoint que lista ferramentas
            # Esperado: lista com nome, descrição, parâmetros
            # Exemplo: GET /ferramentas ou POST /chamar com ação="listar_ferramentas"
            
            # Por enquanto, retornar lista vazia
            self.ferramentas = {
                "proximo_evento": {
                    "description": "Obtém o próximo evento da fila",
                    "parameters": {
                        "esperar_segundos": {"type": "integer", "description": "Segundos para esperar"}
                    }
                },
                "listar_bases": {
                    "description": "Lista as bases disponíveis",
                    "parameters": {
                        "agente": {"type": "string", "description": "Nome do agente"}
                    }
                },
                "consultar": {
                    "description": "Consulta registros de uma base",
                    "parameters": {
                        "base": {"type": "string", "description": "Nome da base"},
                        "filtro": {"type": "object", "description": "Filtro de busca"},
                        "limite": {"type": "integer", "description": "Limite de registros"}
                    }
                }
            }
            
            logger.info(f"✓ Descobertas {len(self.ferramentas)} ferramentas")
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao descobrir ferramentas: {e}")
            return False

    async def salvar_ferramentas(self) -> bool:
        """
        Salva ferramentas em docs/ferramentas.json.

        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            caminho = Path("docs/ferramentas.json")
            caminho.parent.mkdir(parents=True, exist_ok=True)
            
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(self.ferramentas, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Ferramentas salvas em {caminho}")
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao salvar ferramentas: {e}")
            return False

    async def listar_bases(self) -> bool:
        """
        Lista bases disponíveis.

        Returns:
            True se listado com sucesso, False caso contrário
        """
        try:
            logger.info("Listando bases disponíveis...")
            
            # Chamar listar_bases com agente="setup"
            payload = {
                "acao": "listar_bases",
                "agente": "setup",
                "motivo": "Descoberta inicial do mundo"
            }
            
            response = await self.client.post(
                self.server_url,
                json=payload,
                timeout=15.0
            )
            
            if response.status_code != 200:
                logger.error(f"Erro ao listar bases: {response.status_code}")
                logger.error(f"Resposta: {response.text}")
                return False
            
            dados = response.json()
            
            # Esperado: { "status": "ok", "bases": {...}, "agora": "..." }
            if dados.get("status") != "ok":
                logger.error(f"Erro na resposta: {dados.get('mensagem', 'Desconhecido')}")
                return False
            
            self.bases = dados.get("bases", {})
            logger.info(f"✓ Listadas {len(self.bases)} bases")
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao listar bases: {e}")
            return False

    async def salvar_bases(self) -> bool:
        """
        Salva bases em docs/bases.json.

        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            caminho = Path("docs/bases.json")
            caminho.parent.mkdir(parents=True, exist_ok=True)
            
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(self.bases, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Bases salvas em {caminho}")
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao salvar bases: {e}")
            return False

    async def descobrir_exemplos(self) -> bool:
        """
        Descobre exemplos de dados para cada base.

        Returns:
            True se descoberto com sucesso, False caso contrário
        """
        try:
            logger.info("Descobrindo exemplos de dados...")
            
            for base_nome in self.bases.keys():
                try:
                    logger.info(f"  Consultando base '{base_nome}'...")
                    
                    # Chamar consultar(base=base_nome, limite=3)
                    payload = {
                        "acao": "consultar",
                        "base": base_nome,
                        "limite": 3,
                        "agente": "setup",
                        "motivo": "Descoberta de exemplos"
                    }
                    
                    response = await self.client.post(
                        self.server_url,
                        json=payload,
                        timeout=15.0
                    )
                    
                    if response.status_code != 200:
                        logger.warning(f"  Erro ao consultar '{base_nome}': {response.status_code}")
                        self.exemplos[base_nome] = []
                        continue
                    
                    dados = response.json()
                    
                    if dados.get("status") != "ok":
                        logger.warning(f"  Erro na resposta: {dados.get('mensagem', 'Desconhecido')}")
                        self.exemplos[base_nome] = []
                        continue
                    
                    # Esperado: { "status": "ok", "registros": [...], "agora": "..." }
                    registros = dados.get("registros", [])
                    self.exemplos[base_nome] = registros
                    logger.info(f"  ✓ {len(registros)} exemplos encontrados")
                except Exception as e:
                    logger.warning(f"  ✗ Erro ao consultar '{base_nome}': {e}")
                    self.exemplos[base_nome] = []
            
            logger.info(f"✓ Exemplos descobertos para {len(self.exemplos)} bases")
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao descobrir exemplos: {e}")
            return False

    async def salvar_exemplos(self) -> bool:
        """
        Salva exemplos em docs/exemplos/<base>.json.

        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            caminho_base = Path("docs/exemplos")
            caminho_base.mkdir(parents=True, exist_ok=True)
            
            for base_nome, exemplos in self.exemplos.items():
                caminho = caminho_base / f"{base_nome}.json"
                with open(caminho, "w", encoding="utf-8") as f:
                    json.dump(exemplos, f, indent=2, ensure_ascii=False)
                logger.info(f"✓ Exemplos de '{base_nome}' salvos em {caminho}")
            
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao salvar exemplos: {e}")
            return False

    async def imprimir_resumo(self) -> None:
        """Imprime resumo das descobertas."""
        print("\n" + "=" * 70)
        print("RESUMO DA DESCOBERTA DO MUNDO MCP")
        print("=" * 70)
        
        print(f"\n📡 Servidor: {self.server_url}")
        
        print(f"\n🔧 Ferramentas ({len(self.ferramentas)}):")
        for nome, ferramenta in self.ferramentas.items():
            descricao = ferramenta.get("description", "Sem descrição")[:60]
            print(f"   • {nome}: {descricao}...")
        
        print(f"\n📊 Bases ({len(self.bases)}):")
        for nome, base in self.bases.items():
            campos = base.get("campos", [])
            print(f"   • {nome}: {len(campos)} campos")
            if campos:
                campos_str = ', '.join(campos[:3])
                if len(campos) > 3:
                    campos_str += '...'
                print(f"     Campos: {campos_str}")
        
        print(f"\n📋 Exemplos ({len(self.exemplos)}):")
        for nome, exemplos in self.exemplos.items():
            print(f"   • {nome}: {len(exemplos)} registros")
        
        print("\n📁 Arquivos salvos:")
        print("   • docs/ferramentas.json")
        print("   • docs/bases.json")
        print("   • docs/exemplos/<base>.json")
        
        print("\n⚠️  IMPORTANTE:")
        print("   A primeira chamada ligou o relógio simulado.")
        print("   Reinicie o servidor antes de usar os agentes.")
        
        print("\n" + "=" * 70 + "\n")

    async def executar(self) -> bool:
        """
        Executa o descobrimento completo.

        Returns:
            True se tudo executado com sucesso, False caso contrário
        """
        try:
            # Conectar
            if not await self.conectar():
                return False
            
            # Descobrir ferramentas
            if not await self.descobrir_ferramentas():
                logger.warning("Continuando sem ferramentas...")
            
            if not await self.salvar_ferramentas():
                logger.warning("Não foi possível salvar ferramentas")
            
            # Listar bases
            if not await self.listar_bases():
                return False
            
            if not await self.salvar_bases():
                return False
            
            # Descobrir exemplos
            if not await self.descobrir_exemplos():
                logger.warning("Continuando sem exemplos...")
            
            if not await self.salvar_exemplos():
                logger.warning("Não foi possível salvar exemplos")
            
            # Imprimir resumo
            await self.imprimir_resumo()
            
            return True
        except Exception as e:
            logger.error(f"✗ Erro durante execução: {e}")
            return False
        finally:
            if self.client:
                await self.client.aclose()


async def main():
    """Função principal."""
    descobridor = DescobritorMundoHTTP()
    sucesso = await descobridor.executar()
    sys.exit(0 if sucesso else 1)


if __name__ == "__main__":
    asyncio.run(main())
