#!/usr/bin/env python3
"""
Script de diagnóstico para testar conexão com MCP e LiteLLM.
"""

import asyncio
import json
import os
import sys

import httpx
import litellm

MCP_URL = "http://localhost:8765/mcp"
LITELLM_URL = "https://litellm.tech4humans.com.br"
LITELLM_MODEL = "gpt-4o-mini"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


async def testar_mcp():
    """Testa conexão com MCP."""
    print("\n" + "=" * 80)
    print("🔌 TESTANDO CONEXÃO COM MCP")
    print("=" * 80)
    print(f"URL: {MCP_URL}")
    print()

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Teste 1: POST vazio
            print("1️⃣  Enviando POST vazio...")
            try:
                resp = await client.post(MCP_URL, json={})
                print(f"   Status: {resp.status_code}")
                print(f"   Resposta: {resp.text[:200]}")
                try:
                    dados = resp.json()
                    print(f"   JSON: {json.dumps(dados, indent=2)[:300]}")
                except:
                    pass
            except Exception as e:
                print(f"   ❌ Erro: {e}")

            # Teste 2: POST com ação proximo_evento (JSON-RPC 2.0)
            print("\n2️⃣  Enviando proximo_evento (JSON-RPC 2.0)...")
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "proximo_evento",
                    "params": {
                        "agente": "diagnostico",
                        "motivo": "Teste de diagnóstico",
                        "esperar_segundos": 1,
                    },
                    "id": 1,
                }
                resp = await client.post(MCP_URL, json=payload)
                print(f"   Status: {resp.status_code}")
                print(f"   Resposta: {resp.text[:200]}")
                try:
                    dados = resp.json()
                    print(f"   JSON: {json.dumps(dados, indent=2)[:500]}")
                except:
                    pass
            except Exception as e:
                print(f"   ❌ Erro: {e}")

            # Teste 3: GET (se suportado)
            print("\n3️⃣  Tentando GET...")
            try:
                resp = await client.get(MCP_URL)
                print(f"   Status: {resp.status_code}")
                print(f"   Resposta: {resp.text[:200]}")
            except Exception as e:
                print(f"   ❌ Erro: {e}")

    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        print(f"\n💡 Dicas:")
        print(f"   • Verifique se o servidor está rodando")
        print(f"   • Verifique se a porta 8765 está aberta")
        print(f"   • Tente: netstat -an | findstr 8765 (Windows)")


async def testar_litellm():
    """Testa conexão com LiteLLM."""
    print("\n" + "=" * 80)
    print("🤖 TESTANDO CONEXÃO COM LiteLLM")
    print("=" * 80)
    print(f"URL: {LITELLM_URL}")
    print(f"Modelo: {LITELLM_MODEL}")
    print(f"API Key: {'✅ Configurada' if OPENAI_API_KEY else '❌ Não configurada'}")
    print()

    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY não configurada!")
        print("   Configure com: export OPENAI_API_KEY=sua_chave")
        return

    try:
        # Configurar LiteLLM
        litellm.api_base = LITELLM_URL
        litellm.api_key = OPENAI_API_KEY

        print("1️⃣  Enviando requisição ao LLM...")
        response = await asyncio.to_thread(
            litellm.completion,
            model=LITELLM_MODEL,
            messages=[{"role": "user", "content": "Responda com 'OK'."}],
            temperature=0.1,
            max_tokens=10,
        )

        print(f"   ✅ Sucesso!")
        print(f"   Resposta: {response.choices[0].message.content}")
        print(f"   Modelo: {response.model}")
        print(f"   Tokens: {response.usage.total_tokens}")

    except Exception as e:
        print(f"❌ Erro: {e}")
        print(f"\n💡 Dicas:")
        print(f"   • Verifique se a API Key é válida")
        print(f"   • Verifique se o LiteLLM está acessível")
        print(f"   • Tente: curl https://litellm.tech4humans.com.br")


async def testar_conectividade():
    """Testa conectividade básica."""
    print("\n" + "=" * 80)
    print("🌐 TESTANDO CONECTIVIDADE")
    print("=" * 80)

    # Teste 1: localhost:8765
    print("\n1️⃣  Testando localhost:8765...")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get("http://localhost:8765", follow_redirects=True)
            print(f"   ✅ Conectado! Status: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # Teste 2: litellm.tech4humans.com.br
    print("\n2️⃣  Testando litellm.tech4humans.com.br...")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get("https://litellm.tech4humans.com.br", follow_redirects=True)
            print(f"   ✅ Conectado! Status: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")


async def main():
    """Função principal."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  🔍 DIAGNÓSTICO DE CONEXÃO - MCP + LiteLLM".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    await testar_conectividade()
    await testar_mcp()
    await testar_litellm()

    print("\n" + "=" * 80)
    print("✅ DIAGNÓSTICO CONCLUÍDO")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
