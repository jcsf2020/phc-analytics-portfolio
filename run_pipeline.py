from typing import Any, Dict, List, Optional, Union


class DataValidationError(Exception):
    pass


def normalize_customers(
    raw_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]],
) -> List[Dict[str, Any]]:
    # Accept both envelope dicts and plain lists.
    # Real pipeline may already extract the list before calling the normalizer.
    if raw_data is None:
        return []

    # If list is provided, treat it as the customers array.
    if isinstance(raw_data, list):
        customers = raw_data
    elif isinstance(raw_data, dict):
        # Envelope forms.
        if "customers" in raw_data:
            customers = raw_data.get("customers")
        elif "customer" in raw_data:
            customers = raw_data.get("customer")
        else:
            # Be resilient: do not hard-fail on shape; return empty.
            return []

        # Normalize envelope content to list
        if isinstance(customers, dict):
            customers = [customers]
        elif customers is None:
            customers = []
        elif not isinstance(customers, list):
            # Unexpected scalar
            customers = []
    else:
        return []

    out = []
    for cst in customers:
        if not isinstance(cst, dict):
            continue

        # Backward-compatible id mapping: accept aliases.
        if "id" not in cst:
            for alias in (
                "prestashop_customer_id",
                "customer_id",
                "id_customer",
                "ps_customer_id",
            ):
                if alias in cst and cst.get(alias) is not None:
                    cst["id"] = cst.get(alias)
                    break

        # If still no id, skip
        if "id" not in cst or cst.get("id") in (None, ""):
            continue

        out.append(
            _normalize_customer_row(cst)
            if "_normalize_customer_row" in globals()
            else cst
        )

    return out
