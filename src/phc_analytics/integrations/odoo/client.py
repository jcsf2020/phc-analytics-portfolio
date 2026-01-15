from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple
import os
import xmlrpc.client


@dataclass(frozen=True)
class OdooConfig:
    """
    Configuracao do client Odoo via XML-RPC.

    Required:
      - url: ex: http://localhost:8069
      - db:  ex: odoo_phc_local
      - login: ex: api-sync@local
      - password: ex: ApiSync2026!

    XML-RPC endpoints:
      - /xmlrpc/2/common  (auth, version)
      - /xmlrpc/2/object  (execute_kw)
    """
    url: str
    db: str
    login: str
    password: str
    timeout_seconds: int = 20

    def validate(self) -> None:
        if not self.url or not self.url.startswith(("http://", "https://")):
            raise ValueError("url must start with http:// or https://")
        if not self.db:
            raise ValueError("db is required")
        if not self.login:
            raise ValueError("login is required")
        if not self.password:
            raise ValueError("password is required")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be > 0")


class OdooClient:
    """
    Odoo XML-RPC client (Community Edition friendly).
    Security notes:
      - Do not print passwords/tokens.
      - Use a dedicated integration user (api-sync@local).
    """

    def __init__(self, cfg: OdooConfig) -> None:
        cfg.validate()
        self._cfg = cfg
        self._common = xmlrpc.client.ServerProxy(f"{cfg.url}/xmlrpc/2/common", allow_none=True)
        self._models = xmlrpc.client.ServerProxy(f"{cfg.url}/xmlrpc/2/object", allow_none=True)
        self._uid: Optional[int] = None

    @classmethod
    def from_env(cls) -> "OdooClient":
        """
        ENV:
          - ODOO_URL
          - ODOO_DB
          - ODOO_LOGIN
          - ODOO_PASSWORD
          - ODOO_TIMEOUT_SECONDS (optional)
        """
        url = os.getenv("ODOO_URL", "").strip()
        db = os.getenv("ODOO_DB", "").strip()
        login = os.getenv("ODOO_LOGIN", "").strip()
        password = os.getenv("ODOO_PASSWORD", "").strip()
        timeout_s = int(os.getenv("ODOO_TIMEOUT_SECONDS", "20"))
        return cls(OdooConfig(url=url, db=db, login=login, password=password, timeout_seconds=timeout_s))

    def version(self) -> Dict[str, Any]:
        return self._common.version()

    def authenticate(self) -> int:
        uid = self._common.authenticate(self._cfg.db, self._cfg.login, self._cfg.password, {})
        if not uid:
            raise RuntimeError("Odoo auth failed (check DB/login/password; MFA must be disabled for XML-RPC)")
        self._uid = int(uid)
        return self._uid

    @property
    def uid(self) -> int:
        if self._uid is None:
            return self.authenticate()
        return self._uid

    def execute_kw(
        self,
        model: str,
        method: str,
        args: Sequence[Any],
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if kwargs is None:
            kwargs = {}
        return self._models.execute_kw(self._cfg.db, self.uid, self._cfg.password, model, method, list(args), kwargs)

    # ---- Convenience helpers ----

    def search_read(
        self,
        model: str,
        domain: Optional[List[Any]] = None,
        fields: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
        order: str = "id asc",
    ) -> List[Dict[str, Any]]:
        domain = domain or []
        fields = fields or ["id"]
        return self.execute_kw(
            model,
            "search_read",
            [domain],
            {"fields": fields, "limit": int(limit), "offset": int(offset), "order": order},
        )

    def create(self, model: str, values: Dict[str, Any]) -> int:
        return int(self.execute_kw(model, "create", [values]))

    def write(self, model: str, ids: List[int], values: Dict[str, Any]) -> bool:
        return bool(self.execute_kw(model, "write", [ids, values]))

    def list_installed_modules(self, limit: int = 500) -> List[str]:
        rows = self.search_read(
            "ir.module.module",
            domain=[("state", "=", "installed")],
            fields=["name"],
            limit=limit,
        )
        return sorted(r["name"] for r in rows if "name" in r)

    def healthcheck(self) -> Dict[str, Any]:
        v = self.version()
        mods = self.list_installed_modules(limit=300)
        return {
            "ok": True,
            "url": self._cfg.url,
            "db": self._cfg.db,
            "login": self._cfg.login,
            "version": v.get("server_version"),
            "edition": v.get("server_serie"),
            "modules_count": len(mods),
        }


def build_local_client() -> OdooClient:
    """
    Helper for local dev (docker-compose.odoo.yml).
    Uses defaults that match our local environment.
    """
    return OdooClient(
        OdooConfig(
            url=os.getenv("ODOO_URL", "http://localhost:8069"),
            db=os.getenv("ODOO_DB", "odoo_phc_local"),
            login=os.getenv("ODOO_LOGIN", "api-sync@local"),
            password=os.getenv("ODOO_PASSWORD", "ApiSync2026!"),
        )
    )
