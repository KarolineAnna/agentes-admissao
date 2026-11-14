"""Canal da pessoa do RH: lista aprovações/escalações pendentes e grava a decisão em data/rh.json.

    python rh.py                                   (interativo)
    python rh.py --listar                          (só lista)
    python rh.py --decidir RH-001 --decisao aprovado --nome "Ana Souza" [--comentario "..."]

Os agentes (admissao.py) leem data/rh.json a cada volta e continuam os casos decididos.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ARQ = Path(__file__).parent / "data" / "rh.json"


def ler() -> list:
    try:
        return json.loads(ARQ.read_text(encoding="utf-8"))
    except Exception:
        return []


def gravar_decisao(item_id: str, status: str, nome: str, comentario: str = "") -> bool:
    """Relê o arquivo antes de gravar, para não apagar o que os agentes acabaram de criar."""
    itens = ler()
    for it in itens:
        if it["id"] == item_id and it.get("status") == "pendente":
            it.update({"status": status, "decidido_por": nome, "comentario": comentario or None,
                       "decidido_em": datetime.now().isoformat(timespec="seconds")})
            tmp = ARQ.with_suffix(".tmp")
            tmp.write_text(json.dumps(itens, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(ARQ)
            return True
    return False


def mostrar(it: dict) -> None:
    print("\n" + "=" * 70)
    print(f"{it['id']} | {it['tipo'].upper()} | caso {it.get('admissao_id') or '?'} | para: {it.get('para_quem')}")
    print(f"PEDIDO:       {it.get('pedido')}")
    print(f"SITUAÇÃO:     {it.get('situacao')}")
    print(f"JÁ FEITO:     {it.get('ja_feito')}")
    print(f"RISCO:        {it.get('risco')}")
    print("OPÇÕES:       " + " / ".join(it.get("opcoes") or []))
    print(f"RECOMENDAÇÃO: {it.get('recomendacao')}")


def pendentes() -> list:
    return [i for i in ler() if i.get("status") == "pendente"]


def interativo() -> None:
    nome = input("Seu nome (vai em aprovado_por; precisa ser uma pessoa): ").strip()
    while not nome:
        nome = input("Nome obrigatório: ").strip()
    pend = pendentes()
    if not pend:
        print("Nada pendente.")
    for it in pend:
        mostrar(it)
        if it["tipo"] == "escalacao":
            if it.get("subtipo") == "duvida_fora_faq":
                resp = input("Resposta ao contratado (vazio = pular): ").strip()
                if resp:
                    gravar_decisao(it["id"], "aprovado", nome, resp)
                continue
            op = input("[r]esolvido / [p]ular: ").strip().lower()
            if op.startswith("r"):
                gravar_decisao(it["id"], "resolvido", nome, input("Comentário: ").strip())
            continue
        op = input("[a]provar / [r]ecusar / [p]ular: ").strip().lower()
        if op.startswith("a") or op.startswith("r"):
            com = input("Comentário (opcional): ").strip()
            gravar_decisao(it["id"], "aprovado" if op.startswith("a") else "recusado", nome, com)
            print("Decisão gravada. Os agentes continuam o caso na próxima volta.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--listar", action="store_true")
    p.add_argument("--decidir")
    p.add_argument("--decisao", choices=["aprovado", "recusado", "resolvido"])
    p.add_argument("--nome")
    p.add_argument("--comentario", default="")
    a = p.parse_args()
    if a.listar:
        for it in pendentes():
            mostrar(it)
        print(f"\n{len(pendentes())} pendente(s).")
    elif a.decidir:
        if not (a.decisao and a.nome):
            sys.exit("Use --decisao e --nome.")
        print("gravado" if gravar_decisao(a.decidir, a.decisao, a.nome, a.comentario) else "não encontrado ou já decidido")
    else:
        interativo()
