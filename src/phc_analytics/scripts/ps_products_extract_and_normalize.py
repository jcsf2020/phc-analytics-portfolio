from __future__ import annotations

import sys
import json
import xml.etree.ElementTree as ET

from src.phc_analytics.transformations import prestashop_normalize as n


def txt(root: ET.Element, path: str) -> str | None:
    el = root.find(path)
    if el is None or el.text is None:
        return None
    v = el.text.strip()
    return v if v else None


def txt_i18n(root: ET.Element, path: str) -> str | None:
    """
    PrestaShop i18n tipico:
      <name>
        <language id="1">Demo product</language>
      </name>

    Este helper devolve:
    - language[@id='1'] se existir
    - senao o primeiro <language>
    - senao texto direto do parent
    """
    parent = root.find(path)
    if parent is None:
        return None

    # preferir id=1 (muitas lojas usam 1 como default)
    el = parent.find("./language[@id='1']")
    if el is not None and el.text:
        return el.text.strip()

    # fallback: primeiro language
    el = parent.find("./language")
    if el is not None and el.text:
        return el.text.strip()

    # fallback final
    if parent.text:
        v = parent.text.strip()
        return v if v else None

    return None


def main() -> int:
    xml = sys.stdin.read()
    if not xml.strip():
        print(
            "ERROR: stdin vazio (nao recebemos XML). Usa: curl ... | python <script>",
            file=sys.stderr,
        )
        return 2

    root = ET.fromstring(xml)

    # Nota: quando pedes /api/products?display=full&limit=1
    # vem <products><product>...</product></products>
    product = root.find(".//product")
    if product is None:
        print("ERROR: nao encontrei <product> no XML.", file=sys.stderr)
        return 3

    raw = {
        "products": [
            {
                "id": txt(product, "./id"),
                "reference": txt(product, "./reference"),
                "name": txt_i18n(
                    product, "./name"
                ),  # <-- aqui resolve o teu erro "Product missing name"
                "active": txt(product, "./active"),
                "price": txt(product, "./price"),
                "date_add": txt(product, "./date_add"),
                "date_upd": txt(product, "./date_upd"),
            }
        ]
    }

    out = n.normalize_products(raw)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
