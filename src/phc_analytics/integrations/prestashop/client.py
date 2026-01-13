from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict
import json
import os
import urllib.request
import urllib.error


@dataclass(frozen=True)
class PrestaShopConfig:
    """
    Configuracao do client PrestaShop.

    - base_url: URL base da loja / endpoint (ex: https://example.com)
    - api_key: chave/token para autenticar (pode ser vazio no modo mock)
    - timeout_seconds: timeout de rede (segundos)
    """
    base_url: str
    api_key: str = ""
    timeout_seconds: int = 20

    def validate(self) -> None:
        if not self.base_url or not self.base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be > 0")


class PrestaShopClient:
    """
    Client HTTP (Hypertext Transfer Protocol - protocolo web) para PrestaShop.

    Neste MVP:
    - Estrutura pronta para API real
    - Modo mock suportado (sem depender de credenciais)
    - Logging seguro: nao imprimir PII (dados pessoais) nem tokens
    """

    def __init__(self, config: PrestaShopConfig) -> None:
        config.validate()
        self._cfg = config

    @classmethod
    def from_env(cls) -> "PrestaShopClient":
        """
        Carrega configuracao via variaveis de ambiente (ENV).
        ENV = environment variables (variaveis do sistema).

        - PRESTASHOP_BASE_URL
        - PRESTASHOP_API_KEY
        - PRESTASHOP_TIMEOUT_SECONDS (opcional)
        """
        base_url = os.getenv("PRESTASHOP_BASE_URL", "").strip()
        api_key = os.getenv("PRESTASHOP_API_KEY", "").strip()
        timeout_s = int(os.getenv("PRESTASHOP_TIMEOUT_SECONDS", "20"))
        return cls(PrestaShopConfig(base_url=base_url, api_key=api_key, timeout_seconds=timeout_s))

    def _request(self, path: str) -> Dict[str, Any]:
        """
        Faz um GET simples. Ainda nao e' o endpoint final (depende da API real).
        Mantemos aqui apenas para estrutura.
        """
        url = self._cfg.base_url.rstrip("/") + "/" + path.lstrip("/")
        req = urllib.request.Request(url, method="GET")
        # Autenticacao: depende do modo. Mantemos header generico sem assumir formato.
        if self._cfg.api_key:
            req.add_header("Authorization", f"Bearer {self._cfg.api_key}")

        try:
            with urllib.request.urlopen(req, timeout=self._cfg.timeout_seconds) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP error {e.code} calling {url}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Network error calling {url}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON returned by {url}") from e

    # ---- MVP methods (stubs) ----

    def get_customers(self) -> Dict[str, Any]:
        """
        Customers (Clientes). Endpoint real sera confirmado quando houver credenciais.
        """
        return self._request("/api/customers")

    def get_products(self) -> Dict[str, Any]:
        """
        Products (Produtos).
        """
        return self._request("/api/products")

    def get_orders(self) -> Dict[str, Any]:
        """
        Orders (Encomendas).
        """
        return self._request("/api/orders")

    # ---- MOCK MODE (para desenvolvimento sem API real) ----

    def get_customers_mock(self) -> Dict[str, Any]:
        """
        Dados mock (falsos) de Customers.
        Estrutura alinhada com o Data Contract.
        """
        return {
            "customers": [
                {
                    "prestashop_customer_id": 1,
                    "email": "alice@example.com",
                    "firstname": "Alice",
                    "lastname": "Silva",
                    "active": True,
                    "created_at": "2024-01-10T10:15:00",
                    "updated_at": "2024-01-15T09:00:00",
                },
                {
                    "prestashop_customer_id": 2,
                    "email": "bob@example.com",
                    "firstname": "Bob",
                    "lastname": "Santos",
                    "active": True,
                    "created_at": "2024-02-01T14:20:00",
                    "updated_at": "2024-02-05T08:30:00",
                },
            ]
        }

    def get_products_mock(self) -> Dict[str, Any]:
        """
        Dados mock de Products.
        """
        return {
            "products": [
                {
                    "prestashop_product_id": 100,
                    "sku": "SKU-100",
                    "name": "Produto A",
                    "active": True,
                    "price": 19.99,
                    "currency": "EUR",
                    "created_at": "2024-01-05T11:00:00",
                    "updated_at": "2024-01-06T11:00:00",
                },
                {
                    "prestashop_product_id": 200,
                    "sku": "SKU-200",
                    "name": "Produto B",
                    "active": True,
                    "price": 29.99,
                    "currency": "EUR",
                    "created_at": "2024-01-07T12:00:00",
                    "updated_at": "2024-01-08T12:00:00",
                },
            ]
        }

    def get_orders_mock(self) -> Dict[str, Any]:
        """
        Dados mock de Orders.
        """
        return {
            "orders": [
                {
                    "prestashop_order_id": 5000,
                    "prestashop_customer_id": 1,
                    "status": "paid",
                    "total_paid": 49.98,
                    "currency": "EUR",
                    "created_at": "2024-02-10T16:00:00",
                    "updated_at": "2024-02-10T16:05:00",
                    "lines": [
                        {
                            "prestashop_product_id": 100,
                            "quantity": 1,
                            "unit_price": 19.99,
                            "line_total": 19.99,
                        },
                        {
                            "prestashop_product_id": 200,
                            "quantity": 1,
                            "unit_price": 29.99,
                            "line_total": 29.99,
                        },
                    ],
                },
                {
                    "prestashop_order_id": 5001,
                    "prestashop_customer_id": 2,
                    "status": "paid",
                    "total_paid": 19.99,
                    "currency": "EUR",
                    "created_at": "2024-02-12T09:00:00",
                    "updated_at": "2024-02-12T09:30:00",
                    "lines": [
                        {
                            "prestashop_product_id": 100,
                            "quantity": 1,
                            "unit_price": 19.99,
                            "line_total": 19.99,
                        }
                    ],
                },
            ]
        }
