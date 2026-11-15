"""Time de agentes de Admissão (Tema 2): coordenador, conferente e comunicador.

    python admissao.py          (servidor do kit no ar com TEMA=admissao)
    python rh.py                (em outro terminal: decisões da pessoa do RH)

O CÓDIGO decide qual ferramenta MCP chamar; o modelo só classifica o que as regras não resolvem.
Regras: docs/regras_negocio.md (RN-xx citadas nos motivos).
"""

import asyncio
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel

load_dotenv()
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MCP_URL = os.getenv("MCP_URL", "http://localhost:8765/mcp")
MODELO = os.getenv("MODELO", "openai:gpt-4o-mini")
RAIZ = Path(__file__).parent
DATA, LOGS, DOCS = RAIZ / "data", RAIZ / "logs", RAIZ / "docs"
DATA.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)
ARQ_ESTADO, ARQ_RH, ARQ_LICOES = DATA / "estado.json", DATA / "rh.json", DATA / "licoes.json"
PARA_RH = "pessoa do RH responsável pela admissão"
ASSINATURA = "Equipe de Admissão"

FERR: dict = {}          # nome -> ferramenta MCP
ARGS: dict = {}          # nome -> conjunto de argumentos aceitos (esquema real)
BASES: dict = {}         # base -> info de listar_bases
AGORA = {"txt": ""}      # hora simulada oficial (campo `agora`)
CONTRATADOS: dict = {}   # ADM-xx -> ficha
ADMISSOES: dict = {}     # ADM-xx -> etapas
EXIGIDOS: list = []      # base documentos_exigidos
FAQ: list = []
AREAS: dict = {}         # nome sem acento -> email
RESUMO = {"eventos atendidos": 0, "respondidos com FAQ": 0, "recusas": 0, "propostas": 0,
          "escalações": 0, "correções do coordenador": 0}
MODELO_LLM = {"obj": None}


class Encerrado(Exception):
    """Erro 410 ou encerrado=true: o cenário acabou."""


# ---------------------------------------------------------------- utilidades
def sa(t) -> str:
    """Minúsculas e sem acento, para casar palavras-chave."""
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode()
    return t.lower()


def ler_json(arq: Path, padrao):
    try:
        return json.loads(arq.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def gravar_json(arq: Path, dados) -> None:
    tmp = arq.with_suffix(".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(arq)


ESTADO = ler_json(ARQ_ESTADO, {"admissoes": {}, "enviadas": [], "rh_executados": [], "atendidos": []})
LICOES = ler_json(ARQ_LICOES, {"respostas": [], "licoes": []})


def caso(adm: str) -> dict:
    """Memória de curto prazo de uma admissão."""
    return ESTADO["admissoes"].setdefault(adm, {
        "docs": {}, "aguardando": None, "cobrancas": [], "ultima_msg": None, "primeiro_envio": False,
        "contrato_enviado": None, "contrato_cobrado": False, "exame_data": None, "exame_aviso": None,
        "exame_reaviso": False, "exame_confirmado": False, "remarcacoes": 0, "escalado": [],
    })


def salvar() -> None:
    gravar_json(ARQ_ESTADO, ESTADO)
    gravar_json(ARQ_LICOES, LICOES)


def log(agente: str, acao: str, motivo: str = "", evento_id=None) -> None:
    linha = f"[{AGORA['txt'] or '-'}] {agente} → {acao} ({motivo})" + (f" [{evento_id}]" if evento_id else "")
    print(linha, flush=True)
    with open(LOGS / "agentes.log", "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def agora() -> datetime:
    try:
        return datetime.fromisoformat(AGORA["txt"].replace("Z", "")[:19])
    except Exception:
        return datetime.now()


def br(d) -> str:
    """AAAA-MM-DD -> DD/MM/AAAA."""
    try:
        return datetime.fromisoformat(str(d)[:10]).strftime("%d/%m/%Y")
    except Exception:
        return str(d)


def dia_util_menos(d: date, n: int) -> date:
    while n > 0:
        d -= timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def dias_uteis(de: date, ate: date) -> int:
    """Dias úteis em (de, ate]; negativo se ate < de."""
    sinal, a, b = (1, de, ate) if ate >= de else (-1, ate, de)
    n, d = 0, a
    while d < b:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n * sinal


def horas_desde(iso) -> float:
    try:
        return (agora() - datetime.fromisoformat(str(iso)[:19])).total_seconds() / 3600
    except Exception:
        return 999


def inicio(adm: str) -> date:
    d = (ADMISSOES.get(adm) or {}).get("data_inicio") or CONTRATADOS[adm]["data_inicio"]
    return datetime.fromisoformat(str(d)[:10]).date()


def primeiro_nome(adm: str) -> str:
    return CONTRATADOS[adm]["nome"].split()[0]


# ---------------------------------------------------------------- chamadas ao servidor
def normalizar(ret) -> dict:
    """Retorno do adaptador (texto JSON, lista de blocos, tupla ou dict) -> dict."""
    if isinstance(ret, tuple):
        ret = ret[0]
    if isinstance(ret, dict):
        return ret
    if isinstance(ret, list):
        partes = []
        for b in ret:
            partes.append(b.get("text", "") if isinstance(b, dict) else getattr(b, "text", str(b)))
        ret = "".join(partes)
    try:
        r = json.loads(ret)
        return r if isinstance(r, dict) else {"status": "ok", "dados": r}
    except Exception:
        return {"status": "ok", "texto": str(ret)}


def codigo_erro(r: dict) -> Optional[int]:
    c = r.get("codigo") or r.get("code") or r.get("status_code")
    if c is None:
        m = re.search(r"\b(4\d\d|5\d\d)\b", str(r.get("mensagem") or r.get("erro") or r))
        c = m.group(1) if m else None
    try:
        return int(c)
    except Exception:
        return None


async def chamar(agente: str, ferramenta: str, args: dict, motivo: str, evento_id=None, acao=False) -> dict:
    """Chama uma ferramenta MCP com agente, motivo e evento_id, tratando 503/504/409/410 (RN-65)."""
    if ferramenta not in FERR:
        log(agente, f"{ferramenta} indisponível", motivo, evento_id)
        return {"status": "erro", "mensagem": "ferramenta inexistente"}
    payload = dict(args)
    payload.update({"agente": agente, "motivo": motivo})
    if evento_id:
        payload["evento_id"] = evento_id
    aceitos = ARGS.get(ferramenta)
    if aceitos:
        payload = {k: v for k, v in payload.items() if k in aceitos}
    esperas, extra = [2, 4, 8], 1
    while True:
        try:
            r = normalizar(await FERR[ferramenta].ainvoke(payload))
        except Exception as e:  # erro do adaptador (HTTP ou ToolException)
            r = normalizar(str(e)) if str(e).strip().startswith("{") else {"status": "erro", "mensagem": str(e)}
        if r.get("agora"):
            AGORA["txt"] = str(r["agora"])
        if r.get("status") != "erro":
            if acao:
                log(agente, ferramenta, motivo, evento_id)
            return r
        cod = codigo_erro(r)
        if cod == 410:
            raise Encerrado()
        if cod == 503 and esperas:
            await asyncio.sleep(esperas.pop(0))
            continue
        if cod == 504 and (not acao) and esperas:
            esperas.pop(0)
            continue
        if cod == 504 and acao and extra:
            extra -= 1
            if ferramenta == "enviar_mensagem" and await mensagem_ja_enviada(args):
                log(agente, "enviar_mensagem já constava após 504", motivo, evento_id)
                return {"status": "ok", "conferido": True}
            continue
        if cod == 409 and extra:
            extra -= 1
            await asyncio.sleep(1)
            continue
        log(agente, f"ERRO {cod} em {ferramenta}: {str(r.get('mensagem') or r)[:160]}", motivo, evento_id)
        return r


async def mensagem_ja_enviada(args: dict) -> bool:
    """Depois de 504 em enviar_mensagem: confere na base mensagens antes de repetir (RN-65)."""
    regs = await consultar("mensagens", filtro={"para": args.get("para")}, motivo="conferir envio após 504 (RN-65)")
    corpo = sa(args.get("mensagem"))[:60]
    return any(corpo and corpo in sa(json.dumps(m, ensure_ascii=False)) for m in regs)


async def consultar(base: str, filtro=None, busca=None, motivo="consultar base") -> list:
    regs, offset = [], 0
    while True:
        a = {"base": base, "limite": 100, "offset": offset}
        if filtro:
            a["filtro"] = filtro
        if busca:
            a["busca"] = busca
        r = await chamar("coordenador", "consultar", a, motivo)
        lote = r.get("registros") or r.get("dados") or r.get("itens") or []
        if not isinstance(lote, list):
            lote = []
        regs += lote
        if not r.get("tem_mais") or not lote:
            return regs
        offset += len(lote)


async def conversa(de: str, para: str, texto: str) -> None:
    """Passagem de caso entre agentes (registrar_conversa). Não sofre falha simulada: vai em segundo plano."""
    t = asyncio.create_task(chamar(de, "registrar_conversa", {"de": de, "para": para, "mensagem": texto}, f"passagem de caso para {para}"))
    TAREFAS.add(t)
    t.add_done_callback(TAREFAS.discard)
    log(de, f"conversa → {para}: {texto[:140]}")


TAREFAS: set = set()


async def mensagem(agente, para, assunto, corpo, motivo, evento_id=None, chave=None) -> bool:
    """enviar_mensagem com idempotência por chave (não repetir a mesma mensagem)."""
    if chave and chave in ESTADO["enviadas"]:
        return True
    r = await chamar(agente, "enviar_mensagem", {"para": para, "assunto": assunto, "mensagem": corpo},
                     motivo, evento_id, acao=True)
    ok = r.get("status") != "erro"
    if ok and chave:
        ESTADO["enviadas"].append(chave)
    if ok:
        adm = next((a for a, c in CONTRATADOS.items() if c.get("email") == para), None)
        if adm:
            caso(adm)["ultima_msg"] = AGORA["txt"]
    salvar()
    return ok


async def responder(agente, evento_id, texto, motivo) -> bool:
    r = await chamar(agente, "responder_evento", {"evento_id": evento_id, "mensagem": texto}, motivo, evento_id, acao=True)
    return r.get("status") != "erro"


async def observacao(evento_id, texto) -> None:
    """Decisão de não agir: registra o motivo na observacao do evento (RN-48)."""
    await chamar("coordenador", "atualizar", {"base": "eventos", "id": evento_id, "dados": {"observacao": texto}},
                 "registrar decisão de não agir (RN-48)", evento_id, acao=True)


# ---------------------------------------------------------------- RH (aprovações e escalações)
def rh_ler() -> list:
    return ler_json(ARQ_RH, [])


def rh_novo(item: dict) -> dict:
    itens = rh_ler()
    n = max([int(i["id"].split("-")[1]) for i in itens if str(i.get("id", "")).startswith("RH-")] + [0]) + 1
    item = {"id": f"RH-{n:03d}", "para_quem": PARA_RH, "status": "pendente", "decidido_por": None,
            "comentario": None, "decidido_em": None, "criado_em": AGORA["txt"], **item}
    itens.append(item)
    gravar_json(ARQ_RH, itens)
    return item


async def escalar(adm, pedido, situacao, ja_feito, risco, opcoes, recomendacao, evento_id=None, extra=None, chave=None):
    """Só escala: avisa a pessoa do RH com contexto (RN-51) e não age."""
    c = caso(adm) if adm else {"escalado": []}
    if chave and chave in c["escalado"]:
        return
    if chave:
        c["escalado"].append(chave)
    item = rh_novo({"tipo": "escalacao", "admissao_id": adm, "pedido": pedido, "situacao": situacao,
                    "ja_feito": ja_feito, "risco": risco, "opcoes": opcoes, "recomendacao": recomendacao,
                    "evento_id": evento_id, **(extra or {})})
    RESUMO["escalações"] += 1
    print(f"⚠ PARA: pessoa do RH | PEDIDO: {pedido} | CASO: {adm or '?'}", flush=True)
    log("coordenador", f"escalação {item['id']} para o RH", pedido[:80], evento_id)
    salvar()


def propor(adm, tipo, pedido, situacao, ja_feito, risco, opcoes, recomendacao, evento_id, extra=None) -> dict:
    """Propõe: uma pessoa aprova e só depois o agente executa (RN-35, RN-37, RN-51)."""
    item = rh_novo({"tipo": tipo, "admissao_id": adm, "pedido": pedido, "situacao": situacao, "ja_feito": ja_feito,
                    "risco": risco, "opcoes": opcoes, "recomendacao": recomendacao, "evento_id": evento_id,
                    **(extra or {})})
    RESUMO["propostas"] += 1
    print(f"⚠ PARA: pessoa do RH | PEDIDO: {pedido} | CASO: {adm}", flush=True)
    log("coordenador", f"proposta {item['id']} ({tipo}) para o RH", pedido[:80], evento_id)
    return item


# ---------------------------------------------------------------- documentos (conferente)
def exigidos(adm: str) -> dict:
    """tipo -> quantidade exigida para o perfil (RN-01 a RN-04)."""
    c, req = CONTRATADOS[adm], {}
    for d in EXIGIDOS:
        e = sa(d.get("exigido"))
        if e == "sempre":
            req[d["tipo"]] = 1
        elif "casad" in e and sa(c.get("estado_civil")).startswith("casad"):
            req[d["tipo"]] = 1
        elif "filho" in e and int(c.get("filhos") or 0) > 0:
            req[d["tipo"]] = int(c["filhos"])
        elif ("homen" in e or "militar" in sa(d["tipo"])) and c.get("exige_certificado_militar"):
            req[d["tipo"]] = 1
    return req


def nome_doc(tipo: str) -> str:
    return next((d["nome"] for d in EXIGIDOS if d["tipo"] == tipo), tipo)


def regra_doc(tipo: str) -> str:
    return next((d.get("regra", "") for d in EXIGIDOS if d["tipo"] == tipo), "")


def lista_exigidos(adm: str) -> str:
    itens = []
    for t, n in exigidos(adm).items():
        itens.append(nome_doc(t) + (f" (uma por filho: {n})" if n > 1 or "filhos" in t else ""))
    return ", ".join(itens)


CNH = r"\b(cnh|habilitacao|carteira de motorista|carteira nacional de habilitacao)\b"


def tipo_pela_descricao(desc: str, informado: str) -> str:
    """O conferente julga pela descrição, não pelo tipo informado (RN-09)."""
    s = sa(desc)
    if re.search(CNH, s):
        return "rg"  # CNH apresentada como identidade
    for d in EXIGIDOS:
        if any(re.search(rf"\b{re.escape(sa(p))}\b", s) for p in d.get("palavras", [])):
            return d["tipo"]
    return informado or "desconhecido"


def mais_de_90_dias(s: str) -> bool:
    m = re.search(r"(\d+)\s*dias", s)
    if m and int(m.group(1)) > 90:
        return True
    m = re.search(r"(\d+)\s*mes", s)
    if m and int(m.group(1)) >= 4:
        return True
    if re.search(r"mais de (90|tres|3) (dias|meses)|vencid|antig|desatualizad|do ano passado", s):
        return True
    for dd, mm, aa in re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", s):
        try:
            if (agora().date() - date(int(aa), int(mm), int(dd))).days > 90:
                return True
        except ValueError:
            pass
    for mm, aa in re.findall(r"\b(\d{1,2})/(\d{4})\b", s):
        try:
            if (agora().date() - date(int(aa), int(mm), 28)).days > 90:
                return True
        except ValueError:
            pass
    return False


def julgar(adm: str, doc: dict) -> dict:
    """Decide aceito / recusado (com motivo) / divergencia / nao_exigido pela descrição (RN-05 a RN-12)."""
    desc = str(doc.get("descricao") or "")
    s = sa(desc)
    tipo = tipo_pela_descricao(desc, sa(doc.get("tipo")))
    r = {"tipo": tipo, "arquivo": doc.get("arquivo"), "descricao": desc, "id": doc.get("id")}
    if tipo not in exigidos(adm):
        return {**r, "decisao": "nao_exigido"}
    if re.search(CNH, s):
        return {**r, "decisao": "recusado", "motivo": "CNH não serve no lugar do RG; envie o RG frente e verso (RN-05)"}
    if tipo == "rg" and re.search(r"(so|apenas|somente) (a )?frente|sem (o )?verso|falta (o )?verso", s):
        return {**r, "decisao": "recusado", "motivo": "O RG vale frente e verso; envie o RG frente e verso (RN-05)"}
    if re.search(r"ilegivel|borrad|cortad|nao (da|e possivel) (para )?ler|incomplet", s):
        return {**r, "decisao": "recusado",
                "motivo": f"Documento ilegível ou incompleto. Regra: {regra_doc(tipo)} (RN-10)"}
    if tipo == "comprovante_residencia":
        if mais_de_90_dias(s):
            return {**r, "decisao": "recusado",
                    "motivo": "Comprovante de residência com mais de 90 dias; envie uma conta de consumo dos últimos 90 dias no seu nome (RN-06)"}
        primeiro = sa(CONTRATADOS[adm]["nome"]).split()[0]
        proprio = re.search(r"(nome|titularidade) d[ao] (propria )?(pessoa|contratad\w*|candidat\w*)|no (seu|meu|proprio) nome", s)
        titular = re.search(r"(em nome|no nome|titular)\s+(d[aoe]s?\s+)?([a-z ]+)", s)
        outro = re.search(r"\b(marido|esposa|esposo|conjuge|mae|pai|irma|irmao|avo|tio|tia|sogr\w*|namorad\w*|"
                          r"companheir\w*|proprietari\w*|locador\w*|outra pessoa|terceir\w*|colega|amig\w*)\b", s)
        if outro or (titular and not proprio and primeiro not in titular.group(3)):
            return {**r, "decisao": "divergencia",
                    "motivo": "Comprovante de residência em nome de outra pessoa: divergência, depende do OK de uma pessoa (RN-06, RN-11)"}
    if tipo == "foto_3x4" and re.search(r"preto e branco|fundo escuro|antiga|selfie", s):
        return {**r, "decisao": "recusado", "motivo": "Foto 3x4 precisa ser recente, colorida e de fundo claro (RN-08)"}
    return {**r, "decisao": "aceito"}


def base_documentos() -> str:
    for b in BASES:
        if "documento" in sa(b) and "exig" not in sa(b):
            return b
    return "documentos"


def campos(base: str) -> set:
    info = BASES.get(base) or {}
    out = set()
    for k in ("campos", "campos_para_registrar", "campos_alteraveis", "pode_atualizar"):
        v = info.get(k) if isinstance(info, dict) else None
        if isinstance(v, dict):
            out |= set(v.keys())
        elif isinstance(v, list):
            out |= {x if isinstance(x, str) else (x.get("nome") or x.get("campo") or "") for x in v}
    return out


async def gravar_doc(adm, j, estado, evento_id, motivo_doc=None, aprovado_por=None, agente="conferente") -> None:
    """Grava o estado do documento no servidor (RN-12): recusado leva motivo; com ressalva leva aprovado_por."""
    base = base_documentos()
    cs = campos(base)
    campo_estado = next((c for c in ("estado", "status", "situacao") if c in cs), "estado")
    dados = {campo_estado: estado}
    if motivo_doc:
        dados["motivo"] = motivo_doc
    if aprovado_por:
        dados["aprovado_por"] = aprovado_por
    rid = j.get("id_servidor") or j.get("id")
    if not rid:
        filtro = {"admissao": adm, **({"arquivo": j["arquivo"]} if j.get("arquivo") else {})}
        regs = await consultar(base, filtro=filtro, motivo=f"localizar documento de {adm} (RN-12)")
        for reg in regs:
            if j.get("arquivo") and reg.get("arquivo") == j.get("arquivo"):
                rid = reg.get("id")
                break
    motivo = {"aceito": "documento válido pela descrição (RN-09)", "recusado": f"recusa com motivo (RN-05/RN-06/RN-12)",
              "aceito com ressalva": "divergência aprovada por pessoa do RH (RN-11)",
              "recebido": "documento não exigido para o perfil: só registrado (RN-12)"}.get(estado, "estado do documento")
    if rid:
        r = await chamar(agente, "atualizar", {"base": base, "id": rid, "dados": dados}, motivo, evento_id, acao=True)
    else:
        novo = {"admissao_id": adm, "contratado_id": adm, "tipo": j["tipo"], "arquivo": j.get("arquivo"),
                "descricao": j.get("descricao"), **dados}
        if cs:
            novo = {k: v for k, v in novo.items() if k in cs}
        r = await chamar(agente, "registrar", {"base": base, "dados": novo}, motivo, evento_id, acao=True)
        rid = r.get("id") or (r.get("registro") or {}).get("id")
    j["id_servidor"] = rid
    j["estado"] = estado


def faltam(adm: str) -> list:
    """Documentos exigidos ainda sem aceite (divergências em análise não contam como falta)."""
    docs = caso(adm)["docs"]
    out = []
    for t, n in exigidos(adm).items():
        ok = sum(1 for d in docs.values() if d["tipo"] == t and d.get("estado") in ("aceito", "aceito com ressalva", "em análise"))
        if ok < n:
            out.append(nome_doc(t))
    return out


# ---------------------------------------------------------------- revisão (coordenador)
def vazamentos(texto: str, dono: Optional[str]) -> list:
    """CPF, RG, PIS, nascimento ou endereço de quem não é o destinatário (RN-07)."""
    s, achados = sa(texto), []
    so_dig = re.sub(r"[^0-9x]", "", s)
    for adm, c in CONTRATADOS.items():
        if adm == dono:
            continue
        for campo in ("cpf", "rg", "pis"):
            dig = re.sub(r"[^0-9]", "", str(c.get(campo) or ""))[:6]
            if len(dig) >= 6 and dig in so_dig:
                achados.append(f"{campo} de {adm}")
        n = str(c.get("data_nascimento") or "")
        if n and (n in texto or br(n) in texto):
            achados.append(f"nascimento de {adm}")
        rua = sa(str(c.get("endereco") or "").split(",")[0])
        if rua and rua in s:
            achados.append(f"endereço de {adm}")
    if dono is None and re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?[\dx]{2}\b", s):
        achados.append("número com formato de CPF")
    return achados


GATILHOS = re.compile(r"\b(contrato|assin\w*|exame\w*)\b")
PEDIDO_DOC = re.compile(r"\b(envie|enviar|mande|mandar|falta\w*|precisamos)\b.{0,60}\b(rg|cpf|pis|titulo|comprovante|"
                        r"carteira|foto|diploma|escolaridade|sus|certid\w+|certificado|documento\w*)\b")


async def revisar(autor: str, tipo: str, texto: str, dono: Optional[str], livre: bool, recusas=None) -> Optional[str]:
    """Coordenador revisa antes de sair (RN-54). Devolve None se aprovado ou o erro encontrado."""
    erros = [f"dado pessoal ({', '.join(v)})" for v in [vazamentos(texto, dono)] if v]
    if livre and (GATILHOS.search(sa(texto)) or PEDIDO_DOC.search(sa(texto))):
        erros.append("palavra-gatilho em resposta livre (RN-57 a RN-59)")
    for rc in recusas or []:
        if not re.search(r"RN-\d\d", rc.get("motivo", "")):
            erros.append(f"recusa de {nome_doc(rc['tipo'])} sem regra citada")
    if erros:
        return "; ".join(erros)
    await conversa("coordenador", autor, f"Aprovado: {tipo} conferido (privacidade, gatilhos e regra das recusas)")
    return None


def corrigir(texto: str, dono: Optional[str], livre: bool) -> str:
    """O autor refaz uma vez: tira frases com dado pessoal ou gatilho."""
    frases = re.split(r"(?<=[.!?])\s+", texto)
    boas = [f for f in frases if not vazamentos(f, dono) and not (livre and (GATILHOS.search(sa(f)) or PEDIDO_DOC.search(sa(f))))]
    return " ".join(boas) or f"Recebemos a sua mensagem e já estamos cuidando. {ASSINATURA}"


async def enviar_revisado(autor, tipo, texto, dono, livre, envio, recusas=None, adm=None, evento_id=None) -> bool:
    """Revisão + até uma correção; falhou de novo -> escala. `envio(texto)` faz a ação."""
    erro = await revisar(autor, tipo, texto, dono, livre, recusas)
    if erro:
        RESUMO["correções do coordenador"] += 1
        texto2 = corrigir(texto, dono, livre)
        await conversa("coordenador", autor, f"Corrigir: {erro} | refazer sem o trecho problemático")
        erro2 = await revisar(autor, tipo, texto2, dono, livre, recusas)
        if erro2:
            await escalar(adm, f"Revisar mensagem que falhou na revisão duas vezes ({tipo})",
                          f"A mensagem de {autor} falhou na revisão: {erro2}", "Mensagem bloqueada antes do envio",
                          "Vazar dado ou disparar ação indevida no mundo", ["Redigir manualmente", "Descartar"],
                          "Redigir manualmente", evento_id)
            return False
        texto = texto2
    return await envio(texto)


# ---------------------------------------------------------------- classificação (coordenador)
class Classe(BaseModel):
    categoria: Literal["duvida", "pergunta_gestor", "mudanca_data", "dado_sensivel", "desistencia",
                       "agradecimento", "informacao_area", "confirmacao", "outro"]
    admissao_id: Optional[str] = None


def llm():
    if MODELO_LLM["obj"] is None and os.getenv("LITELLM_URL") and os.getenv("LITELLM_API_KEY"):
        MODELO_LLM["obj"] = init_chat_model(MODELO, base_url=os.environ["LITELLM_URL"],
                                            api_key=os.environ["LITELLM_API_KEY"], temperature=0.1)
    return MODELO_LLM["obj"]


async def classificar_llm(texto: str) -> str:
    m = llm()
    if not m:
        return "outro"
    try:
        r = await m.with_structured_output(Classe).ainvoke(
            "Classifique a mensagem recebida pela equipe de Admissão. Categorias: duvida (contratado pergunta algo), "
            "pergunta_gestor (gestor/área pergunta andamento ou pede algo), mudanca_data (pedido para mudar a data de "
            "início), dado_sensivel (saúde, laudo, processo), desistencia, agradecimento, informacao_area (área "
            "informa algo feito), confirmacao (contratado confirma presença ou assinatura), outro.\n\n" + texto[:1500])
        return r.categoria
    except Exception as e:
        log("coordenador", f"modelo indisponível: {str(e)[:80]}", "classificação cai em regra")
        return "outro"


SENSIVEL = r"\b(laudo|diagnostic\w*|deficien\w*|doenca|cid\b|gravid\w*|gestante|atestado|cirurgia|tratamento|" \
           r"psiquiatr\w*|medicament\w*|processo (judicial|trabalhista|criminal)|processando|acao judicial|saude)"
DESISTE = r"(desist\w*|nao (vou|quero) mais|aceitei outra|outra proposta|nao tenho mais interesse|recusar a vaga|abrir mao)"
MUDA_DATA = r"((mud|alter|adi|antecip|troc|posterg|transfer|remarc|passar)\w*.{0,50}(data|inicio|comec\w*|primeiro dia|entrada))" \
            r"|((comecar|iniciar|entrar) (so )?(em|no dia|dia|a partir) \d)"


def classificar_regras(ev: dict, quem: dict) -> Optional[str]:
    s = sa(texto_evento(ev))
    s_limpo = re.sub(r"plano de saude|cartao (nacional )?de saude|cartao do sus", "", s)
    if quem["papel"] != "area" and re.search(SENSIVEL, s_limpo):
        return "dado_sensivel"
    if quem["papel"] == "contratado" and re.search(DESISTE, s):
        return "desistencia"
    if quem["papel"] in ("contratado", "gestor") and re.search(MUDA_DATA, s) and "exame" not in s:
        return "mudanca_data"
    if quem["papel"] in ("contratado", "gestor") and quem["adm"] and "exame" not in s \
            and re.search(r"comec|inici|entrar|primeiro dia|chega", s):
        datas = datas_no_texto(s)
        if any(d != inicio(quem["adm"]) for d in datas):
            return "mudanca_data"  # data citada diferente da atual: sempre vai ao RH (RN-35)
        if datas and quem["papel"] == "contratado":
            return "confirma_data"
    if quem["papel"] == "contratado" and re.search(r"o que (eu )?(preciso|tenho que|devo) (mandar|enviar)|o que (esta |ainda )?falt|pendenc", s):
        return "pendencias"
    if ev.get("documentos"):
        return "documentos"
    if quem["papel"] == "contratado" and re.search(r"\b(segue|seguem|envio|enviei|mandei|mando|anex\w*|estou mandando)\b", s) \
            and re.search(CNH + r"|\b(rg|identidade|comprovante|conta de (luz|agua|gas)|foto)\b", s):
        return "doc_texto"
    if quem["papel"] == "area":
        return "area"
    if quem["papel"] is None:
        return "nao_identificado"
    if re.search(r"cobranc|sem resposta|aguardando (retorno|resposta)|ninguem respondeu", s) and sa(ev.get("origem")) == "mundo":
        return "cobranca_mundo"
    if quem["papel"] == "gestor":
        if re.search(r"(repositorio|licenca|github|gitlab|jira|figma|slack|acesso (a|ao|para)|permiss)", s):
            return "acesso_time"
        if re.search(r"obrigad|agradec", s) and "?" not in s:
            return "agradecimento"
        return "pergunta_gestor"
    if re.search(r"\b(assinei|assinado|assinada|confirmo|confirmada|confirmado|estarei|vou comparecer|estarei la)\b", s):
        return "confirmacao"
    if "?" in s or re.search(r"\b(duvida|pergunta|como|quando|qual|quais|posso|preciso|onde|tem )", s):
        return "duvida"
    if re.search(r"obrigad|agradec|beleza|combinado|\bok\b", s):
        return "agradecimento"
    return None


def datas_no_texto(s: str) -> list:
    out = []
    for a, m, d in re.findall(r"\b(\d{4})-(\d{2})-(\d{2})\b", s):
        out.append((int(a), int(m), int(d)))
    for d, m, a in re.findall(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", s):
        ano = int(a) if a else agora().year
        out.append((ano + 2000 if ano < 100 else ano, int(m), int(d)))
    datas = []
    for a, m, d in out:
        try:
            datas.append(date(a, m, d))
        except ValueError:
            pass
    return datas


def texto_evento(ev: dict) -> str:
    partes = [str(ev.get(k)) for k in ("assunto", "texto", "corpo", "mensagem", "conteudo", "descricao", "pedido") if ev.get(k)]
    return " | ".join(partes)


def remetente(ev: dict) -> str:
    r = ev.get("de") or ev.get("remetente") or ev.get("email") or ev.get("from") or ""
    if isinstance(r, dict):
        r = r.get("email") or r.get("nome") or ""
    return sa(r)


def identificar(ev: dict) -> dict:
    """Quem mandou (contratado, gestor, área) e de qual admissão."""
    rem, s = remetente(ev), sa(texto_evento(ev))
    adm = ev.get("admissao_id") or ev.get("contratado_id")
    m = re.search(r"adm-?\s?(\d+)", s)
    if not adm and m:
        adm = f"ADM-{int(m.group(1)):02d}"
    papel = None
    for a, c in CONTRATADOS.items():
        if rem and rem == sa(c.get("email")):
            papel, adm = "contratado", adm or a
        elif rem and rem == sa(c.get("gestor_email")):
            papel = "gestor"
            if not adm:
                # gestor com mais de uma pessoa: tenta pelo nome no texto
                nomes = [x for x, y in CONTRATADOS.items() if sa(y.get("gestor_email")) == rem]
                adm = next((x for x in nomes if sa(CONTRATADOS[x]["nome"].split()[0]) in s), nomes[0] if len(nomes) == 1 else None)
    for nome_area, email in AREAS.items():
        if rem and rem == sa(email):
            papel = "area"
            ev["_area"] = nome_area
    if not adm:
        for a, c in CONTRATADOS.items():
            partes = sa(c["nome"]).split()
            if partes[0] in s and (len(partes) < 2 or any(p in s for p in partes[1:])):
                adm = a
                break
            if partes[0] in s.split():
                adm = adm or a
    if papel is None and adm and not rem and sa(ev.get("origem")) in ("cenario", "painel"):
        papel = "contratado"  # evento do painel sem remetente: trata como do contratado da admissão citada
    if adm and adm not in CONTRATADOS:
        adm = None
    return {"papel": papel, "adm": adm, "rem": rem}


# ---------------------------------------------------------------- FAQ e memória longa
def buscar_faq(texto: str) -> Optional[dict]:
    s, melhor, pontos = sa(texto), None, 0
    for f in FAQ:
        p = sum(len(sa(k)) for k in f.get("palavras_chave", []) if re.search(rf"\b{re.escape(sa(k))}\b", s))
        if p > pontos:
            melhor, pontos = f, p
    return melhor


def resposta_aprendida(texto: str) -> Optional[dict]:
    """RN-53: resposta do RH a uma dúvida fora do FAQ vira resposta pronta."""
    alvo = set(re.findall(r"[a-z]{4,}", sa(texto)))
    for r in LICOES["respostas"]:
        base = set(re.findall(r"[a-z]{4,}", sa(r["pergunta"])))
        if alvo and base and len(alvo & base) / len(base) >= 0.6:
            return r
    return None


def licao(texto: str) -> None:
    if texto not in LICOES["licoes"]:
        LICOES["licoes"].append(texto)
        log("coordenador", f"lição registrada: {texto}", "memória de longo prazo")


# ---------------------------------------------------------------- mensagens de modelo fixo (RN-56 a RN-61)
def modelo(tipo: str, adm: str, **x) -> tuple:
    c = CONTRATADOS[adm]
    ini = br((ADMISSOES.get(adm) or {}).get("data_inicio") or c["data_inicio"])
    nome, cargo, pn = c["nome"], c["cargo"], primeiro_nome(adm)
    if tipo == "ti":
        return AREAS.get("ti"), f"Pedido de acesso {adm}", \
            f"Olá, TI. Pedido de acesso para {adm}: criar e-mail, conta e VPN para {nome}, {cargo}, com início em {ini}. {ASSINATURA}"
    if tipo == "equip":
        mon = ", e monitor" if re.search(r"desenvolv|design", sa(c.get("area")) + sa(cargo)) else ""
        return AREAS.get("equipamentos"), f"Pedido de kit {adm}", \
            f"Olá, Equipamentos. Pedido de kit para {adm}: {nome}, {cargo}, com início em {ini}. Kit: notebook, headset, teclado e mouse{mon}. {ASSINATURA}"
    if tipo == "gestor":
        return c["gestor_email"], f"Chegada de {nome}", \
            f"Olá. {nome} ({cargo}) chega ao seu time em {ini}, às 09:00, na recepção da sede. {ASSINATURA}"
    if tipo == "docs":
        prazo = dia_util_menos(inicio(adm), 7).strftime("%d/%m/%Y")
        return c["email"], f"Documentos da admissão {adm}", \
            f"Oi, {pn}! Para seguir com a sua admissão ({adm}), envie por favor: {lista_exigidos(adm)}. Prazo: {prazo}. {ASSINATURA}"
    if tipo == "clinica":
        return AREAS.get("clinica"), f"Exame admissional {adm}", \
            f"Olá, Clínica. Pedido de agendamento do exame admissional para {adm}: {nome}, {cargo}. {ASSINATURA}"
    if tipo == "remarcar":
        return AREAS.get("clinica"), f"Remarcação {adm}", \
            f"Olá, Clínica. Pedido de remarcação do exame admissional para {adm}: {nome}, {cargo}. {ASSINATURA}"
    if tipo == "contrato":
        return c["email"], f"Contrato de trabalho {adm}", \
            f"Oi, {pn}! Segue o seu contrato de trabalho ({adm}). Por favor, assine e responda esta mensagem. {ASSINATURA}"
    if tipo == "cobrar_contrato":
        prazo = dia_util_menos(inicio(adm), 2).strftime("%d/%m/%Y")
        return c["email"], f"Contrato {adm}", \
            f"Oi, {pn}! Precisamos do seu contrato ({adm}) assinado até {prazo} para garantir o seu primeiro dia. Pode assinar hoje? {ASSINATURA}"
    if tipo == "aviso_exame":
        return c["email"], f"Exame admissional {adm}", \
            f"Oi, {pn}! Seu exame admissional ({adm}) está agendado para {x.get('data')}, às 09:00. Leve um documento com foto e a guia da clínica. Pode confirmar sua presença respondendo esta mensagem? {ASSINATURA}"
    if tipo == "cobrar":
        return c["email"], f"Pendências da admissão {adm}", \
            f"Oi, {pn}! Ainda aguardamos {x.get('falta')} para seguir com a sua admissão ({adm}). Pode nos responder hoje? {ASSINATURA}"
    raise ValueError(tipo)


async def enviar_modelo(agente, tipo, adm, motivo, evento_id=None, chave=None, **x) -> bool:
    para, assunto, corpo = modelo(tipo, adm, **x)
    if not para:
        log(agente, f"sem e-mail para {tipo}", "e-mail só das bases (RN-62)", evento_id)
        return False
    return await mensagem(agente, para, assunto, corpo, motivo, evento_id, chave)


# ---------------------------------------------------------------- início (RN-13, RN-60)
async def iniciar_frentes() -> None:
    """As cinco admissões em paralelo: o 1º dia já tem prazo vencendo (RN-13, RN-14)."""
    await asyncio.gather(*(iniciar_uma(adm) for adm in CONTRATADOS))
    salvar()


async def iniciar_uma(adm: str) -> None:
    if True:
        if all(f"{t}:{adm}" in ESTADO["enviadas"] for t in ("ti", "equip", "gestor", "docs")):
            return
        await conversa("coordenador", "comunicador",
                       f"{adm}: acionar TI, equipamentos, avisar gestor e pedir a lista completa de documentos (RN-13, RN-17, RN-60)")
        await enviar_modelo("comunicador", "ti", adm, f"acionar TI para {adm} no 1º dia (RN-13, RN-25)", chave=f"ti:{adm}")
        await enviar_modelo("comunicador", "equip", adm, f"pedir kit para {adm} (RN-13, RN-26)", chave=f"equip:{adm}")
        await enviar_modelo("comunicador", "gestor", adm, f"avisar gestor da chegada de {adm} (RN-17, RN-30)", chave=f"gestor:{adm}")
        if await enviar_modelo("comunicador", "docs", adm, f"pedir documentos exigidos de {adm} (RN-01 a RN-04, RN-60)",
                               chave=f"docs:{adm}"):
            caso(adm)["aguardando"] = {"o_que": "os documentos da lista que enviamos", "desde": AGORA["txt"]}


# ---------------------------------------------------------------- casos
async def caso_documentos(ev, quem) -> None:
    adm, eid = quem["adm"], ev["id"]
    c = caso(adm)
    await conversa("coordenador", "conferente", f"{adm}: {len(ev['documentos'])} documento(s) recebidos no evento {eid}; conferir pela descrição (RN-09)")
    julgados = [julgar(adm, d) for d in ev["documentos"]]
    recusas = [j for j in julgados if j["decisao"] == "recusado"]
    if recusas:
        # coordenador revisa as recusas antes de gravar e responder (RN-54)
        texto_rev = "; ".join(f"{nome_doc(j['tipo'])}: {j['motivo']}" for j in recusas)
        await conversa("conferente", "coordenador", f"{adm}: recusas para revisar -> {texto_rev}")
        erro = await revisar("conferente", "recusa de documento", texto_rev, adm, False, recusas)
        if erro:
            RESUMO["correções do coordenador"] += 1
            await conversa("coordenador", "conferente", f"Corrigir: {erro} | citar a regra do documento")
            for j in recusas:
                j["motivo"] = f"{j.get('motivo', '')} Regra: {regra_doc(j['tipo'])} (RN-12)".strip()
    divergencias, gravacoes = [], []
    for j in julgados:
        chave = j.get("arquivo") or f"{j['tipo']}-{len(c['docs'])}"
        c["docs"][chave] = j
        if j["decisao"] == "aceito":
            gravacoes.append(gravar_doc(adm, j, "aceito", eid))
        elif j["decisao"] == "recusado":
            gravacoes.append(gravar_doc(adm, j, "recusado", eid, motivo_doc=j["motivo"]))  # recusa antes de pedir o novo (RN-60)
            RESUMO["recusas"] += 1
        elif j["decisao"] == "nao_exigido":
            j["estado"] = "recebido"  # não exigido: fica como recebido, sem contar (RN-12)
        else:
            j["estado"] = "em análise"  # divergência: fica recebido no servidor até o OK (RN-11)
            divergencias.append((chave, j))
    await asyncio.gather(*gravacoes)
    for chave, j in divergencias:
        await conversa("conferente", "coordenador", f"{adm}: {nome_doc(j['tipo'])} com divergência ({j['descricao'][:80]}); montar proposta ao RH (RN-11)")
        propor(adm, "divergencia_documento", f"Aceitar com ressalva o {nome_doc(j['tipo'])} de {adm}?",
               f"{CONTRATADOS[adm]['nome']} enviou: {j['descricao']}", "Documento registrado como recebido; demais conferidos",
               "Aceitar sem OK gera alerta; recusar atrasa os documentos (prazo D-7)",
               ["Aprovar: aceito com ressalva", "Recusar: pedir outro comprovante no nome da pessoa"],
               "Aprovar se a pessoa mora no endereço (ex.: conta no nome do cônjuge ou familiar)", eid,
               {"doc_chave": chave})
    # resposta ao contratado: aceitos, recusados com motivo e o que falta
    aceitos = [nome_doc(j["tipo"]) for j in julgados if j["decisao"] == "aceito"]
    falta = faltam(adm)
    partes = [f"Oi, {primeiro_nome(adm)}! Conferimos os documentos que você mandou ({adm})."]
    if aceitos:
        partes.append("Aceitos: " + ", ".join(aceitos) + ".")
    for j in recusas:
        partes.append(f"Recusado: {nome_doc(j['tipo'])}. Motivo: {j['motivo']}")
    if divergencias:
        partes.append("Em análise com a pessoa do RH: " + ", ".join(nome_doc(j["tipo"]) for _, j in divergencias) + ".")
    partes.append(("Ainda falta enviar: " + ", ".join(falta) + ".") if falta else "Com isso, a sua documentação está completa.")
    partes.append(ASSINATURA)
    await conversa("conferente", "comunicador", f"{adm}: responder ao contratado com aceitos, recusados e o que falta")
    corpo = " ".join(partes)
    await enviar_revisado("comunicador", "resposta de documentos", corpo, adm, False,
                          lambda t: mensagem("comunicador", CONTRATADOS[adm]["email"], f"Conferência de documentos {adm}", t,
                                             f"retorno da conferência de documentos (RN-12, RN-60)", eid),
                          adm=adm, evento_id=eid)
    c["aguardando"] = {"o_que": ", ".join(falta), "desde": AGORA["txt"]} if falta else None
    if not c["primeiro_envio"]:
        c["primeiro_envio"] = True  # pessoa se engajou: exame e contrato já (RN-24, RN-34)
        await conversa("coordenador", "comunicador", f"{adm}: primeiro envio de documentos; pedir exame à clínica e mandar o contrato (RN-24, RN-34)")
        await enviar_modelo("comunicador", "clinica", adm, f"pedir exame admissional de {adm} (RN-24, RN-27)", eid, chave=f"clinica:{adm}")
        if await enviar_modelo("comunicador", "contrato", adm, f"enviar contrato a {adm} (RN-29, RN-34)", eid, chave=f"contrato:{adm}"):
            c["contrato_enviado"] = AGORA["txt"]
    salvar()


async def caso_doc_texto(ev, quem) -> None:
    """Documento descrito só no texto (sem anexo na base): o conferente julga pela descrição (RN-09)."""
    adm, eid, texto = quem["adm"], ev["id"], texto_evento(ev)
    await conversa("coordenador", "conferente", f"{adm}: documento descrito no texto do evento {eid}; conferir pela descrição (RN-09)")
    j = julgar(adm, {"tipo": "", "descricao": texto})
    if j["decisao"] == "recusado":
        await conversa("conferente", "coordenador", f"{adm}: recusa para revisar -> {nome_doc(j['tipo'])}: {j['motivo']}")
        erro = await revisar("conferente", "recusa de documento", j["motivo"], adm, False, [j])
        if erro:
            RESUMO["correções do coordenador"] += 1
            j["motivo"] += f" Regra: {regra_doc(j['tipo'])} (RN-12)"
        RESUMO["recusas"] += 1
        corpo = (f"Oi, {primeiro_nome(adm)}! Conferimos o documento que você mandou ({adm}). Recusado: {nome_doc(j['tipo'])}. "
                 f"Motivo: {j['motivo']} Por favor, envie o {nome_doc(j['tipo'])} correto. {ASSINATURA}")
        await conversa("conferente", "comunicador", f"{adm}: avisar a recusa com motivo e pedir o documento certo (RN-05, RN-60)")
        await enviar_revisado("comunicador", "recusa de documento", corpo, adm, False,
                              lambda t: mensagem("comunicador", CONTRATADOS[adm]["email"], f"Conferência de documentos {adm}", t,
                                                 "recusa com motivo e pedido do documento certo (RN-05, RN-60)", eid), adm=adm, evento_id=eid)
    elif j["decisao"] == "divergencia":
        await responder("comunicador", eid, f"Recebido, {primeiro_nome(adm)}! O documento está em análise com a pessoa do RH. {ASSINATURA}",
                        "divergência vai ao RH (RN-11)")
        propor(adm, "divergencia_documento", f"Aceitar com ressalva o {nome_doc(j['tipo'])} de {adm}?", texto[:300],
               "Contratado avisado que está em análise", "Aceitar sem OK gera alerta", ["Aprovar", "Recusar"],
               "Aprovar se a pessoa mora no endereço", eid)
    else:
        await responder("comunicador", eid, f"Recebido, {primeiro_nome(adm)}! Vamos conferir o documento assim que ele chegar no sistema. {ASSINATURA}",
                        "documento citado no texto; conferência quando chegar na base (RN-12)")


async def caso_mudanca_data(ev, quem) -> None:
    adm, eid = quem["adm"], ev["id"]
    nome = CONTRATADOS[adm]["nome"]
    aberta = next((i for i in rh_ler() if i["tipo"] == "mudanca_data" and i.get("admissao_id") == adm and i["status"] == "pendente"), None)
    if aberta:  # já está com o RH: não abre proposta repetida
        await responder("comunicador", eid, f"O pedido de mudança da data de início de {nome} já está com a pessoa do RH, que vai decidir. "
                        f"Avisamos assim que houver resposta. {ASSINATURA}", f"pedido já em aprovação ({aberta['id']}) (RN-36)")
        return
    await conversa("coordenador", "comunicador", f"{adm}: pedido de mudança de data; responder na hora a quem pediu (RN-36)")
    await responder("comunicador", eid,
                    f"Recebemos o seu pedido de mudança da data de início de {nome} e encaminhamos à pessoa do RH, que vai decidir. Avisamos assim que houver resposta. {ASSINATURA}",
                    "confirmar recebimento do pedido de mudança de data (RN-35, RN-36)")
    s = sa(texto_evento(ev))
    nova = None
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s) or None
    if m:
        nova = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    else:
        m = re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", s) or re.search(r"\bdia (\d{1,2})\b", s)
        if m:
            g = m.groups()
            mes = int(g[1]) if len(g) > 1 and g[1] else inicio(adm).month
            ano = int(g[2]) if len(g) > 2 and g[2] else agora().year
            ano = ano + 2000 if ano < 100 else ano
            try:
                nova = date(ano, mes, int(g[0]))
            except ValueError:
                nova = None
    ini, hoje = inicio(adm), agora().date()
    adm_reg = ADMISSOES.get(adm, {})
    risco = []
    if nova:
        for etapa, n in (("documentos", 7), ("contabilidade", 6), ("exame agendado", 5), ("gestor avisado", 3),
                         ("exame apto", 2), ("contrato assinado", 2)):
            if dia_util_menos(nova, n) < hoje:
                risco.append(f"{etapa} (D-{n} = {dia_util_menos(nova, n).strftime('%d/%m')}) já estaria vencido")
        folga = dias_uteis(hoje, dia_util_menos(nova, 2))
        tempo = folga >= 0 and (folga >= 2 or ("apto" in sa(adm_reg.get("exame")) and "assinad" in sa(adm_reg.get("contrato"))))
        risco.append(f"exame apto e contrato até D-2 ({dia_util_menos(nova, 2).strftime('%d/%m')}): {'dá tempo' if tempo else 'NÃO dá tempo'}")
        if nova.weekday() >= 5 or nova <= hoje or nova > date(2026, 12, 11):
            risco.append("data fora das regras do servidor (dia útil, depois de hoje, até 11/12/2026): erro 422 (RN-39)")
            recom = "Recusar: data inválida para o servidor"
        elif nova > ini:
            recom = "Aprovar: adiar dá mais folga às etapas"
        else:
            recom = "Aprovar" if tempo else "Recusar e manter a data: não dá tempo de exame apto e contrato"
    else:
        risco.append("não foi possível ler a data nova no pedido")
        recom = "Pedir a data exata a quem pediu"
    feito = ", ".join(f"{k}: {adm_reg.get(k)}" for k in ("ti", "equipamento", "contabilidade", "exame", "contrato", "gestor_avisado") if adm_reg.get(k))
    propor(adm, "mudanca_data", f"Aprovar a mudança da data de início de {nome} de {ini.strftime('%d/%m/%Y')} para "
           f"{nova.strftime('%d/%m/%Y') if nova else '?'}?",
           f"{quem['papel']} ({quem['rem'] or '?'}) pediu: {texto_evento(ev)[:300]}", feito or "frentes acionadas no 1º dia",
           "; ".join(risco), ["Aprovar a nova data", "Recusar e manter a data atual", "Propor outra data"], recom, eid,
           {"nova_data": nova.isoformat() if nova else None, "solicitante": quem["rem"], "data_atual": ini.isoformat()})
    salvar()


async def caso_duvida(ev, quem) -> None:
    adm, eid, texto = quem["adm"], ev["id"], texto_evento(ev)
    f = buscar_faq(texto)
    if f:
        await conversa("coordenador", "comunicador", f"{adm}: dúvida respondida pelo FAQ {f['id']}")
        await enviar_revisado("comunicador", "resposta do FAQ", f["resposta"], adm, False,
                              lambda t: responder("comunicador", eid, t, f"dúvida respondida com o FAQ {f['id']}"),
                              adm=adm, evento_id=eid)
        RESUMO["respondidos com FAQ"] += 1
        return
    r = resposta_aprendida(texto)
    if r:
        await conversa("coordenador", "comunicador", f"{adm}: dúvida já respondida antes pelo RH ({r['aprovado_por']}); usar resposta aprendida (RN-53)")
        await enviar_revisado("comunicador", "resposta aprendida", r["resposta"], adm, True,
                              lambda t: responder("comunicador", eid, t, "resposta aprendida com o RH (RN-53)"), adm=adm, evento_id=eid)
        return
    await responder("comunicador", eid, "Sua pergunta foi encaminhada à pessoa do RH responsável pela admissão; retornamos assim que ela responder.",
                    "dúvida fora do FAQ: avisar que foi ao RH (RN-50)")
    await escalar(adm, "Responder dúvida fora do FAQ", f"Pergunta de {adm}: {texto[:300]}", "Contratado avisado que a dúvida foi ao RH",
                  "Contratado sem resposta; resposta inventada poderia estar errada", ["Responder (texto vai ao contratado)", "Ignorar"],
                  "Responder; a resposta vira resposta pronta para a próxima vez (RN-53)", eid,
                  {"subtipo": "duvida_fora_faq", "pergunta": texto[:500], "destinatario": CONTRATADOS[adm]["email"] if adm else None})


def situacao_texto(adm: str) -> str:
    """Resumo sem dado pessoal: nome, cargo, data e etapas (RN-07)."""
    c, a = CONTRATADOS[adm], ADMISSOES.get(adm, {})
    rotulo = {"ti": "acessos de TI", "equipamento": "equipamento", "contabilidade": "registro na contabilidade",
              "exame": "ASO (saúde ocupacional)", "contrato": "formalização do vínculo", "gestor_avisado": "aviso ao gestor"}
    feito, pend = [], []
    for k, r in rotulo.items():
        v = sa(a.get(k))
        (feito if re.search(r"pronto|sim|concluid|apto|assinad|acionad|agendad|enviad|registrad", v) and "inapto" not in v else pend).append(
            f"{r} ({a.get(k) or 'pendente'})")
    docs = "completos" if not faltam(adm) else f"{len(faltam(adm))} pendente(s)"
    return (f"{c['nome']}, {c['cargo']}, início em {br(a.get('data_inicio') or c['data_inicio'])}. "
            f"Já feito: {', '.join(feito) or 'frentes acionadas'}. Pendente: {', '.join(pend) or 'nada'}. Documentação: {docs}.")


async def caso_gestor(ev, quem, acesso=False) -> None:
    adm, eid = quem["adm"], ev["id"]
    if not adm:
        return await caso_nao_identificado(ev, quem)
    await conversa("coordenador", "comunicador", f"{adm}: {'pedido de acesso do time' if acesso else 'pergunta de andamento'} do gestor")
    txt = f"Olá. {situacao_texto(adm)}"
    if acesso:
        txt += (" Acessos específicos do time (repositório, licença de software) são pedidos pelo próprio gestor à TI. "
                "E-mail, conta e VPN a Equipe de Admissão já pediu.")
    if any(k in (ADMISSOES.get(adm, {}).get("_escalado") or "") for k in ("sem_resposta",)) or "sem_resposta" in caso(adm)["escalado"]:
        txt += " O caso está com a pessoa do RH, porque a pessoa ainda não respondeu aos nossos pedidos."
    txt += f" {ASSINATURA}"
    await enviar_revisado("comunicador", "resposta ao gestor", txt, None, True,
                          lambda t: responder("comunicador", eid, t, "responder gestor sem dado pessoal (RN-07, RN-25)"),
                          adm=adm, evento_id=eid)


async def caso_area(ev, quem) -> None:
    adm, eid, s = quem["adm"], ev["id"], sa(texto_evento(ev))
    area = ev.get("_area", "")
    if "clinica" in area and adm:
        c = caso(adm)
        if re.search(r"inapt", s):
            await responder("coordenador", eid, f"Recebido. {ASSINATURA}", "registrar resultado da clínica (RN-18)")
            return await escalar(adm, "Primeiro dia em risco: resultado inapto", f"Clínica informou resultado inapto para {adm}",
                                 "Resultado registrado", "Sem exame apto a pessoa não começa (RN-18, RN-55)",
                                 ["Avaliar com medicina do trabalho", "Rever data de início"], "Falar com a medicina do trabalho hoje",
                                 eid, chave="inapto")
        if re.search(r"falt|nao compareceu|ausent|nao veio|remarc", s):
            await responder("coordenador", eid, f"Recebido; vamos verificar com a pessoa do RH a remarcação. {ASSINATURA}",
                            "contratado faltou: remarcação vai para o RH (RN-23, RN-27)")
            if c["remarcacoes"] >= 1:
                return await escalar(adm, "Contratado faltou de novo", f"{adm} faltou ao exame remarcado", "Já remarcado uma vez",
                                     "Sem exame apto a pessoa não começa (RN-55)", ["Falar com a pessoa", "Rever data"], "Falar com a pessoa", eid,
                                     chave="falta2")
            c["remarcacoes"] += 1
            propor(adm, "remarcar_exame", f"Remarcar o exame de {CONTRATADOS[adm]['nome']} ({adm})?", f"Clínica avisou falta: {s[:200]}",
                   "Exame pedido e aviso enviado", "Sem exame apto até D-2 a pessoa não começa",
                   ["Aprovar remarcação", "Recusar"], "Aprovar (máximo uma remarcação)", eid)
            return
        if re.search(r"\bapto\b|resultado", s):
            await responder("coordenador", eid, f"Recebido, obrigado. {ASSINATURA}", "resultado do exame registrado (RN-18)")
            return
        m = re.search(r"(\d{4}-\d{2}-\d{2})|(\d{1,2}/\d{1,2}(?:/\d{4})?)", s)
        if re.search(r"agend|marcad", s) or m:
            data_txt = br(m.group(1)) if m and m.group(1) else (m.group(2) if m else "a data informada pela clínica")
            c["exame_data"] = data_txt
            await conversa("coordenador", "comunicador", f"{adm}: exame agendado ({data_txt}); avisar o contratado e pedir confirmação (RN-23, RN-28)")
            if await enviar_modelo("comunicador", "aviso_exame", adm, f"avisar data do exame e pedir confirmação (RN-23, RN-28)", eid,
                                   chave=f"aviso_exame:{adm}:{data_txt}", data=data_txt):
                c["exame_aviso"] = AGORA["txt"]
                licao("A clínica agenda o exame às 09:00, 2 dias úteis depois do pedido; o contratado precisa confirmar antes.")
            salvar()
            return
    if "contabil" in area:
        await responder("coordenador", eid, f"Recebido, obrigado. {ASSINATURA}", "retorno da contabilidade registrado (RN-31)")
        return
    if re.search(r"\?|mandem|informem|enviem|quem (e|sao|vai)|precisamos saber", s) and area in ("ti", "equipamentos"):
        # área pede quem começa: id, nome, cargo e início (sem dado pessoal, RN-07)
        linhas = [f"{a}: {c['nome']}, {c['cargo']}, início em {inicio(a).strftime('%d/%m/%Y')}" for a, c in CONTRATADOS.items()]
        txt = f"Olá. Seguem as admissões de dezembro. " + "; ".join(linhas) + f". {ASSINATURA}"
        await enviar_revisado("comunicador", "resposta à área", txt, None, True,
                              lambda t: responder("comunicador", eid, t, f"informar à área {area} quem começa e o cargo (RN-25, RN-26)"),
                              evento_id=eid)
        return
    await responder("coordenador", eid, f"Recebido, obrigado. {ASSINATURA}", f"confirmar recebimento de {area or 'área'} (RN-25, RN-26)")


async def caso_confirmacao(ev, quem) -> None:
    adm, eid, s = quem["adm"], ev["id"], sa(texto_evento(ev))
    c = caso(adm)
    if "assin" in s:
        if c["contrato_cobrado"]:
            licao("Há contratado que só assina o contrato depois do 2º pedido.")
    else:
        c["exame_confirmado"] = True
    c["aguardando"] = None if not faltam(adm) else c["aguardando"]
    await responder("comunicador", eid, f"Recebido, obrigado, {primeiro_nome(adm)}! {ASSINATURA}", "confirmação do contratado registrada (RN-23, RN-29)")
    salvar()


async def caso_nao_identificado(ev, quem) -> None:
    eid = ev["id"]
    await responder("coordenador", eid, f"Recebemos a sua mensagem e encaminhamos à pessoa do RH responsável pela admissão. {ASSINATURA}",
                    "evento não identificado vai ao RH (RN-50)")
    await escalar(quem["adm"], "Identificar remetente/assunto do evento", f"Evento {eid} de {quem['rem'] or '?'}: {texto_evento(ev)[:300]}",
                  "Remetente avisado que foi ao RH", "Agir no caso errado ou expor dado de outra pessoa",
                  ["Indicar a admissão", "Descartar"], "Indicar a admissão certa", eid)


async def atender(ev: dict) -> None:
    """Coordenador classifica e decide quem cuida (regras primeiro, modelo só no resto)."""
    eid = ev.get("id")
    quem = identificar(ev)
    if quem["papel"] == "contratado" and not ev.get("documentos"):
        # documentos chegam na base `documentos`, ligados ao evento pelo evento_id
        docs = await consultar("documentos", filtro={"evento_id": eid}, motivo="ver documentos que chegaram no evento (RN-12)")
        ev["documentos"] = [d for d in docs if d.get("evento_id") == eid and d.get("status") == "recebido"]
    cat = classificar_regras(ev, quem)
    if cat is None:
        cat = await classificar_llm(texto_evento(ev))
        if quem["papel"] == "gestor" and cat == "duvida":
            cat = "pergunta_gestor"
    if cat in ("duvida", "confirmacao", "agradecimento") and not quem["adm"]:
        cat = "nao_identificado"
    log("coordenador", f"evento classificado como {cat}", f"{quem['papel'] or '?'} {quem['adm'] or ''}".strip(), eid)
    if quem["papel"] == "contratado" and quem["adm"]:
        caso(quem["adm"])["aguardando"] = caso(quem["adm"])["aguardando"] and {**caso(quem["adm"])["aguardando"], "desde": AGORA["txt"]}
    if cat == "documentos" and quem["adm"]:
        await caso_documentos(ev, quem)
    elif cat == "mudanca_data" and quem["adm"]:
        await caso_mudanca_data(ev, quem)
    elif cat == "dado_sensivel":
        await responder("coordenador", eid, f"Recebemos a sua mensagem e encaminhamos à pessoa do RH responsável pela admissão, com sigilo. {ASSINATURA}",
                        "dado sensível vai ao RH sem análise (RN-49)")
        await escalar(quem["adm"], "Tratar mensagem com dado sensível", f"Evento {eid} com dado sensível (não analisado pelo agente)",
                      "Remetente avisado; conteúdo não repassado", "Exposição de dado sensível", ["RH trata diretamente com a pessoa"],
                      "RH trata diretamente com a pessoa", eid)
    elif cat == "desistencia":
        await responder("coordenador", eid, f"Recebemos a sua mensagem e encaminhamos à pessoa do RH responsável pela admissão. {ASSINATURA}",
                        "desistência vai ao RH (RN-50)")
        await escalar(quem["adm"], "Contratado sinaliza desistência", f"{quem['adm']}: {texto_evento(ev)[:300]}", "Contratado avisado",
                      "Vaga sem pessoa no 1º dia; frentes acionadas à toa", ["Conversar com a pessoa", "Cancelar a admissão"],
                      "Conversar com a pessoa hoje", eid)
    elif cat == "doc_texto":
        await caso_doc_texto(ev, quem)
    elif cat == "confirma_data":
        await responder("comunicador", eid, f"Isso, {primeiro_nome(quem['adm'])}! O seu primeiro dia ({quem['adm']}) é "
                        f"{inicio(quem['adm']).strftime('%d/%m/%Y')}, às 09:00, na recepção da sede. {ASSINATURA}",
                        "confirmar a data de início que a pessoa citou (RN-20)")
    elif cat == "pendencias":
        falta = faltam(quem["adm"])
        await conversa("coordenador", "comunicador", f"{quem['adm']}: contratado perguntou o que falta; reenviar a lista (RN-59, RN-60)")
        if falta:
            prazo = dia_util_menos(inicio(quem["adm"]), 7).strftime("%d/%m/%Y")
            await mensagem("comunicador", CONTRATADOS[quem["adm"]]["email"], f"Pendências da admissão {quem['adm']}",
                           f"Oi, {primeiro_nome(quem['adm'])}! Para seguir com a sua admissão ({quem['adm']}), envie por favor: "
                           f"{', '.join(falta)}. Prazo: {prazo}. {ASSINATURA}", "responder o que falta com pedido claro (RN-59)", eid)
            caso(quem["adm"])["aguardando"] = {"o_que": ", ".join(falta), "desde": AGORA["txt"]}
        else:
            await responder("comunicador", eid, f"Oi, {primeiro_nome(quem['adm'])}! A sua documentação está completa. {ASSINATURA}",
                            "informar que não há documentos pendentes")
    elif cat == "duvida":
        await caso_duvida(ev, quem)
    elif cat in ("pergunta_gestor", "acesso_time"):
        await caso_gestor(ev, quem, acesso=cat == "acesso_time")
    elif cat == "area":
        await caso_area(ev, quem)
    elif cat == "confirmacao":
        await caso_confirmacao(ev, quem)
    elif cat == "cobranca_mundo":
        alvo = ev.get("responde_a")
        txt = f"Recebido. {situacao_texto(quem['adm'])} {ASSINATURA}" if quem["adm"] else f"Recebido; estamos cuidando. {ASSINATURA}"
        await enviar_revisado("coordenador", "resposta à cobrança", txt, None, True,
                              lambda t: responder("coordenador", eid, t, f"responder cobrança do mundo sobre {alvo or 'evento'} (RN-47)"),
                              adm=quem["adm"], evento_id=eid)
    elif cat in ("agradecimento", "informacao_area"):
        await responder("comunicador", eid, f"Recebido, obrigado! {ASSINATURA}", "confirmar recebimento (sem pedido no evento, RN-63)")
    else:
        await caso_nao_identificado(ev, quem)
    RESUMO["eventos atendidos"] += 1
    ESTADO["atendidos"].append(eid)
    salvar()


# ---------------------------------------------------------------- decisões do RH (rh.json)
async def executar_decisoes() -> None:
    """Continua os casos que a pessoa do RH já decidiu, sem perguntar de novo."""
    for it in rh_ler():
        if it.get("status") == "pendente" or it["id"] in ESTADO["rh_executados"]:
            continue
        ESTADO["rh_executados"].append(it["id"])
        salvar()
        adm, eid, quem, ok = it.get("admissao_id"), it.get("evento_id"), it.get("decidido_por"), it.get("status") == "aprovado"
        log("coordenador", f"decisão do RH {it['id']}: {it['status']} por {quem}", "continuar caso decidido (RN-52)", eid)
        if it["tipo"] == "mudanca_data":
            await caso_data_decidida(it, adm, eid, quem, ok)
        elif it["tipo"] == "divergencia_documento":
            j = caso(adm)["docs"].get(it.get("doc_chave"))
            if not j:
                continue
            if ok:
                await gravar_doc(adm, j, "aceito com ressalva", eid, aprovado_por=quem, agente="conferente")
                falta = faltam(adm)
                await mensagem("comunicador", CONTRATADOS[adm]["email"], f"Comprovante de residência {adm}",
                               f"Oi, {primeiro_nome(adm)}! O seu comprovante de residência foi aceito ({adm})."
                               + (f" Ainda falta enviar: {', '.join(falta)}." if falta else " A sua documentação está completa.") + f" {ASSINATURA}",
                               "comprovante aceito com ressalva após OK do RH (RN-11)", eid)
            else:
                j["motivo"] = f"Comprovante em nome de outra pessoa não foi aceito pelo RH; envie uma conta de consumo dos últimos 90 dias no seu nome (RN-06). {it.get('comentario') or ''}".strip()
                await gravar_doc(adm, j, "recusado", eid, motivo_doc=j["motivo"])
                RESUMO["recusas"] += 1
                await mensagem("comunicador", CONTRATADOS[adm]["email"], f"Comprovante de residência {adm}",
                               f"Oi, {primeiro_nome(adm)}! O comprovante de residência foi recusado. Motivo: {j['motivo']} "
                               f"Por favor, envie um comprovante de residência no seu nome. {ASSINATURA}",
                               "pedir novo comprovante depois da recusa (RN-06, RN-60)", eid)
        elif it["tipo"] == "remarcar_exame" and ok:
            await enviar_modelo("comunicador", "remarcar", adm, f"remarcar exame aprovado por {quem} (RN-27)", eid, chave=f"remarcar:{adm}")
        elif it.get("subtipo") == "duvida_fora_faq" and it.get("comentario") and it.get("destinatario"):
            resp = it["comentario"]
            LICOES["respostas"].append({"pergunta": re.sub(r"\S+@\S+", "", it.get("pergunta", ""))[:300], "resposta": resp, "aprovado_por": quem})
            await enviar_revisado("comunicador", "resposta do RH", f"Oi, {primeiro_nome(adm)}! {resp} {ASSINATURA}", adm, True,
                                  lambda t: mensagem("comunicador", it["destinatario"], f"Resposta à sua dúvida {adm}", t,
                                                     f"resposta do RH ({quem}) à dúvida fora do FAQ (RN-53)", eid), adm=adm, evento_id=eid)
        salvar()


async def caso_data_decidida(it, adm, eid, quem, ok) -> None:
    nome = CONTRATADOS[adm]["nome"]
    destino = it.get("solicitante") or CONTRATADOS[adm]["email"]
    if ok and it.get("nova_data") and quem:
        await conversa("coordenador", "comunicador", f"{adm}: RH ({quem}) aprovou a data {br(it['nova_data'])}; atualizar e avisar contratado e gestor (RN-38, RN-41)")
        r = await chamar("coordenador", "atualizar", {"base": "admissoes", "id": adm,
                                                      "dados": {"data_inicio": it["nova_data"], "aprovado_por": quem}},
                         f"mudança de data aprovada por {quem} (RN-38)", eid, acao=True)
        if r.get("status") == "erro":
            await mensagem("comunicador", destino, f"Data de início de {nome}",
                           f"Olá. Não foi possível mudar a data de início de {nome}: a data pedida não é aceita (precisa ser dia útil, "
                           f"depois de hoje e até 11/12/2026). A data segue {br(it.get('data_atual'))}. {ASSINATURA}",
                           "mudança de data recusada pelo servidor (RN-39)", eid)
            return
        ADMISSOES.setdefault(adm, {})["data_inicio"] = it["nova_data"]
        c = CONTRATADOS[adm]
        await mensagem("comunicador", c["email"], f"Nova data de início {adm}",
                       f"Oi, {primeiro_nome(adm)}! A sua data de início ({adm}) mudou para {br(it['nova_data'])}, às 09:00, na recepção da sede. {ASSINATURA}",
                       "avisar contratado da nova data (RN-41)", eid)
        await mensagem("comunicador", c["gestor_email"], f"Nova data de chegada de {nome}",
                       f"Olá. {nome} ({c['cargo']}) chega ao seu time em {br(it['nova_data'])}, às 09:00, na recepção da sede. {ASSINATURA}",
                       "avisar gestor da nova data (RN-30, RN-41)", eid)
    else:
        await mensagem("comunicador", destino, f"Data de início de {nome}",
                       f"Olá. A pessoa do RH avaliou o pedido e a data de início de {nome} segue em {br(it.get('data_atual'))}. "
                       f"{it.get('comentario') or ''} {ASSINATURA}".replace("  ", " "),
                       "RH recusou a mudança: data mantida (RN-42)", eid)


# ---------------------------------------------------------------- prazos e cobranças (voltas sem evento)
async def atualizar_admissoes() -> None:
    for a in await consultar("admissoes", motivo="ver situação real das admissões (B0, RN-25 a RN-31)"):
        aid = a.get("id") or a.get("admissao_id")
        if aid:
            ADMISSOES[aid] = a


async def docs_pendentes() -> None:
    """Documentos `recebido` ainda não conferidos (ex.: chegaram depois do evento): conferir no mesmo dia (RN-14)."""
    por_adm: dict = {}
    for d in await consultar("documentos", filtro={"status": "recebido"}, motivo="achar documentos ainda não conferidos (RN-12, RN-14)"):
        adm = d.get("admissao")
        if adm in CONTRATADOS and d.get("arquivo") not in caso(adm)["docs"]:
            por_adm.setdefault((adm, d.get("evento_id")), []).append(d)
    for (adm, eid), docs in por_adm.items():
        ev = {"id": eid, "documentos": docs}
        await caso_documentos(ev, {"adm": adm, "papel": "contratado", "rem": CONTRATADOS[adm]["email"]})


async def varrer_prazos() -> None:
    hoje = agora().date()
    for adm in CONTRATADOS:
        c, a = caso(adm), ADMISSOES.get(adm, {})
        ini = inicio(adm)
        ate_inicio = dias_uteis(hoje, ini)
        # D0: boas-vindas e próximos passos, só com textos do FAQ (RN-21)
        if hoje >= ini and f"d0:{adm}" not in ESTADO["enviadas"]:
            textos = [f["resposta"] for f in (buscar_faq("plano de saude"), buscar_faq("salario"), buscar_faq("vale refeicao")) if f]
            corpo = f"Oi, {primeiro_nome(adm)}! Boas-vindas ao time! Próximos passos: " + " ".join(textos) + f" {ASSINATURA}"
            await enviar_revisado("comunicador", "boas-vindas D0", corpo, adm, True,
                                  lambda t: mensagem("comunicador", CONTRATADOS[adm]["email"], f"Boas-vindas {adm}", t,
                                                     "boas-vindas e próximos passos no 1º dia (RN-20, RN-21)", chave=f"d0:{adm}"), adm=adm)
            continue
        if hoje >= ini:
            continue
        exame_ok = "apto" in sa(a.get("exame")) and "inapto" not in sa(a.get("exame"))
        contrato_ok = "assinad" in sa(a.get("contrato"))
        # D-2 sem exame apto ou contrato: primeiro dia em risco (RN-55)
        if ate_inicio <= 2 and a and not (exame_ok and contrato_ok):
            falta = [x for x, ok in (("exame apto", exame_ok), ("contrato assinado", contrato_ok)) if not ok]
            await escalar(adm, "Primeiro dia em risco", f"{adm} a {ate_inicio} dia(s) útil(eis) do início sem {', '.join(falta)}",
                          f"Etapas atuais: exame={a.get('exame')}, contrato={a.get('contrato')}", "A pessoa não começa e gera alerta grave (RN-55)",
                          ["Cobrar a pessoa por telefone", "Adiar a data de início", "Acionar a clínica"], "Cobrar hoje e avaliar adiar a data",
                          chave="d2_risco")
        # exame agendado na base e ainda não avisado: avisar já, sem depender do evento da clínica (RN-23, RN-28)
        if sa(a.get("exame")) == "agendado" and a.get("exame_data"):
            data_txt = br(a["exame_data"])
            try:
                futuro = datetime.fromisoformat(str(a["exame_data"])[:10]).date() >= hoje
            except ValueError:
                futuro = False
            if futuro and f"aviso_exame:{adm}:{data_txt}" not in ESTADO["enviadas"]:
                c["exame_data"] = data_txt
                if await enviar_modelo("comunicador", "aviso_exame", adm, "avisar data do exame e pedir confirmação (RN-23, RN-28)",
                                       chave=f"aviso_exame:{adm}:{data_txt}", data=data_txt):
                    c["exame_aviso"], c["exame_confirmado"], c["exame_reaviso"] = AGORA["txt"], False, False
        # contrato não assinado há 3 h simuladas: cobrar uma vez (há quem só assine no 2º pedido)
        if c["contrato_enviado"] and not contrato_ok and not c["contrato_cobrado"] and horas_desde(c["contrato_enviado"]) >= 3 \
                and horas_desde(c["ultima_msg"]) >= 1:
            if await enviar_modelo("comunicador", "cobrar_contrato", adm, "cobrar assinatura do contrato, 2º pedido (RN-29, RN-46)",
                                   chave=f"cobrar_contrato:{adm}"):
                c["contrato_cobrado"] = True
        # exame avisado e não confirmado há 3 h: reavisar uma vez
        if c["exame_aviso"] and not c["exame_confirmado"] and not c["exame_reaviso"] and horas_desde(c["exame_aviso"]) >= 3 \
                and horas_desde(c["ultima_msg"]) >= 1 and "realiz" not in sa(a.get("exame")) and not exame_ok:
            if await enviar_modelo("comunicador", "aviso_exame", adm, "2º aviso do exame para confirmação (RN-23, RN-28)",
                                   chave=f"reaviso_exame:{adm}", data=c["exame_data"]):
                c["exame_reaviso"] = True
        # contratado sem responder: cobrar no 2º dia útil, escalar no 4º (RN-43 a RN-46)
        ag = c.get("aguardando")
        if ag and ag.get("desde"):
            try:
                desde = datetime.fromisoformat(ag["desde"][:19]).date()
            except Exception:
                continue
            du = dias_uteis(desde, hoje)
            if du >= 4:
                await escalar(adm, "Contratado sem resposta há 4 dias úteis", f"{adm} não responde desde {br(ag['desde'])}",
                              f"Pedidos e cobranças enviados: {len(c['cobrancas'])}", "Documentos, exame e contrato parados; 1º dia em risco",
                              ["Ligar para a pessoa", "Adiar a data", "Cancelar a admissão"], "Ligar hoje; avisar o gestor que o caso está com o RH",
                              chave="sem_resposta")
                licao("Há contratado que nunca responde: cobrar no 2º dia útil e escalar no 4º.")
            elif du >= 2 and str(hoje) not in c["cobrancas"] and horas_desde(c["ultima_msg"]) >= 1:
                falta = ", ".join(faltam(adm)) or ag["o_que"]
                if await enviar_modelo("comunicador", "cobrar", adm, f"cobrança após {du} dias úteis sem resposta (RN-43, RN-46)", falta=falta):
                    c["cobrancas"].append(str(hoje))
    salvar()


# ---------------------------------------------------------------- laço
async def carregar_dados() -> None:
    global EXIGIDOS, FAQ
    r = await chamar("coordenador", "listar_bases", {}, "conhecer bases e campos")
    bases = r.get("bases") or r
    if isinstance(bases, list):
        bases = {(b.get("base") or b.get("nome")): b for b in bases if isinstance(b, dict)}
    BASES.update({k: v for k, v in bases.items() if isinstance(v, (dict, list)) and k not in ("status", "agora")})
    gravar_json(DOCS / "bases.json", BASES)
    for c in await consultar("contratados", motivo="ler fichas dos contratados (RN-01 a RN-04)") or ler_json(DOCS / "contratados.json", []):
        CONTRATADOS[c["id"]] = c
    await atualizar_admissoes()
    EXIGIDOS = await consultar("documentos_exigidos", motivo="regras dos documentos (RN-01 a RN-08)") or ler_json(DOCS / "documentos_exigidos.json", [])
    FAQ = await consultar("faq", motivo="FAQ para respostas prontas") or ler_json(DOCS / "faq.json", [])
    for a in await consultar("areas", motivo="e-mails das áreas (RN-62)") or ler_json(DOCS / "areas.json", []):
        if "@" in str(a.get("email")):
            AREAS[sa(a["area"]).replace("clinica", "clinica")] = a["email"]
    log("coordenador", f"dados carregados: {len(CONTRATADOS)} contratados, {len(ADMISSOES)} admissões, {len(EXIGIDOS)} docs exigidos, "
        f"{len(FAQ)} FAQ, áreas {list(AREAS)}", "início")


def imprimir_resumo() -> None:
    print("\n========== RESUMO ==========")
    for k, v in RESUMO.items():
        print(f"  {k}: {v}")
    pend = [i for i in rh_ler() if i.get("status") == "pendente"]
    print(f"  pendentes com o RH: {len(pend)}")
    print("============================")
    with open(LOGS / "agentes.log", "a", encoding="utf-8") as f:
        f.write("RESUMO " + json.dumps(RESUMO, ensure_ascii=False) + "\n")


async def main() -> None:
    cliente = MultiServerMCPClient({"mundo": {"transport": "streamable_http", "url": MCP_URL, "timeout": timedelta(seconds=60)}})
    for t in await cliente.get_tools():
        FERR[t.name] = t
        esquema = t.args_schema if isinstance(t.args_schema, dict) else t.args_schema.model_json_schema()
        ARGS[t.name] = set((esquema or {}).get("properties", {}).keys())
    gravar_json(DOCS / "ferramentas.json", {n: {"descricao": FERR[n].description, "argumentos": sorted(ARGS[n])} for n in FERR})
    print(f"Conectado a {MCP_URL}: {', '.join(FERR)}")
    if LICOES["licoes"]:
        print("Lições de rodadas anteriores:\n  - " + "\n  - ".join(LICOES["licoes"]))
    try:
        await carregar_dados()
        await iniciar_frentes()
        volta = 0
        while True:
            volta += 1
            await executar_decisoes()
            r = await chamar("coordenador", "proximo_evento", {"esperar_segundos": 8}, "puxar próximo evento")
            if r.get("encerrado"):
                raise Encerrado()
            ev = r.get("evento")
            if ev and ev.get("id") not in ESTADO["atendidos"]:
                try:
                    await atender(ev)
                except Encerrado:
                    raise
                except Exception as e:  # nunca travar o laço
                    log("coordenador", f"falha ao atender: {type(e).__name__}: {str(e)[:150]}", "seguir o laço", ev.get("id"))
                    try:
                        await observacao(ev["id"], f"Falha interna ao atender; caso encaminhado ao RH ({type(e).__name__})")
                    except Encerrado:
                        raise
                    except Exception:
                        pass
            else:
                if volta % 3 == 1:
                    await atualizar_admissoes()
                    await docs_pendentes()
                await varrer_prazos()
    except (Encerrado, KeyboardInterrupt, asyncio.CancelledError):
        log("coordenador", "cenário encerrado", "410 / encerrado / Ctrl+C")
    finally:
        salvar()
        imprimir_resumo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
