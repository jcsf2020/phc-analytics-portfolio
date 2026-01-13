from __future__ import annotations

import sys
import json
import xml.etree.ElementTree as ET

from src.phc_analytics.transformations import prestashop_normalize as n


def _txt(parent: ET.Element, tag: str) -> str | None:
    """Extrai texto de <tag> dentro de parent (customer), já stripado."""
    el = parent.find(f"./{tag}")
    if el is None or el.text is None:
        return None
    s = el.text.strip()
    return s if s != "" else None


def _to_int(s: str | None) -> int | None:
    if s is None:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def main() -> int:
    # 1) Lê XML da stdin (vem do pipe do curl)
    xml = sys.stdin.read().strip()
    if not xml:
        print("ERROR: stdin vazio (sem XML). Confirma o pipe do curl.", file=sys.stderr)
        return 2

    # 2) Parse do XML
    root = ET.fromstring(xml)

    # 3) Vai buscar o primeiro <customer> (porque estás a usar limit=1)
    customer = root.find(".//customer")
    if customer is None:
        print("ERROR: não encontrei <customer> no XML.", file=sys.stderr)
        return 3

    # 4) Constrói raw no formato esperado pela normalize_customers()
    raw = {
        "customers": [
            {
                "id": _txt(customer, "id"),
                "email": _txt(customer, "email"),
                "firstname": _txt(customer, "firstname"),
                "lastname": _txt(customer, "lastname"),
                # importante: converter "0"/"1" para int para bool() funcionar bem na normalização
                "active": _to_int(_txt(customer, "active")),
                "date_add": _txt(customer, "date_add"),
                "date_upd": _txt(customer, "date_upd"),
            }
        ]
    }

    # 5) Normaliza (canónico)
    out = n.normalize_customers(raw)

    # 6) Imprime JSON final
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
