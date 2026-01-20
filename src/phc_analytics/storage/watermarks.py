from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import psycopg2
import psycopg2.extras


@dataclass(frozen=True)
class Watermark:
    entity_name: str
    watermark_ts: str


class WatermarkManager:
    """
    Gestor de estado incremental (watermarks) em Postgres.

    Regra:
    - watermark_ts representa o ultimo source_updated_at carregado com sucesso.
    - nunca usar now() como watermark; now() so serve para updated_at.
    """

    def __init__(self, dsn: str):
        self.dsn = dsn

    def get(self, entity_name: str) -> Optional[Watermark]:
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(
                    """
                    SELECT entity_name, watermark_ts
                    FROM staging.etl_watermarks
                    WHERE entity_name = %s
                    """,
                    (entity_name,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return Watermark(
                    entity_name=row["entity_name"],
                    watermark_ts=str(row["watermark_ts"]),
                )

    def set(self, entity_name: str, new_ts: str) -> None:
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE staging.etl_watermarks
                    SET watermark_ts = %s,
                        updated_at = now()
                    WHERE entity_name = %s
                    """,
                    (new_ts, entity_name),
                )
                conn.commit()
