from phc_analytics.transformations.prestashop_normalize import normalize_customers


def test_normalize_customers_accepts_list_input():
    raw_list = [
        {
            "id": "10",
            "email": "JOAO@EXAMPLE.COM",
            "firstname": "Joao",
            "lastname": "Fonseca",
            "active": 1,
            "date_add": "2024-02-10 10:00:00",
            "date_upd": "2024-02-10 10:30:00",
        }
    ]

    out = normalize_customers(raw_list)

    assert isinstance(out, list)
    assert len(out) == 1
    assert out[0]["prestashop_customer_id"] == 10
    assert out[0]["email"] == "joao@example.com"


def test_normalize_customers_accepts_envelope_customers():
    raw = {
        "customers": [
            {"id": 11, "email": "a@b.com", "firstname": "A", "lastname": "B", "active": True}
        ]
    }

    out = normalize_customers(raw)

    assert len(out) == 1
    assert out[0]["prestashop_customer_id"] == 11
    assert out[0]["email"] == "a@b.com"


def test_normalize_customers_accepts_id_alias():
    # pipeline/mock may provide prestashop_customer_id instead of id
    raw_list = [
        {
            "prestashop_customer_id": 12,
            "email": "x@y.com",
            "firstname": "X",
            "lastname": "Y",
            "active": 1,
        }
    ]

    out = normalize_customers(raw_list)

    assert len(out) == 1
    assert out[0]["prestashop_customer_id"] == 12
    assert out[0]["email"] == "x@y.com"
