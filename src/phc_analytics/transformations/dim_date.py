from datetime import date, timedelta
from typing import List, Dict


def generate_dim_date(start_date: date, end_date: date) -> List[Dict[str, int]]:
    """
    Gera uma dimensão de datas (DimDate).
    1 linha por dia entre start_date e end_date.
    """
    dim_date = []
    current = start_date

    while current <= end_date:
        dim_date.append(
            {
                "date": current.isoformat(),
                "year": current.year,
                "month": current.month,
                "day": current.day,
                "week": current.isocalendar().week,
                "quarter": (current.month - 1) // 3 + 1,
                "weekday": current.weekday(),  # 0=Mon, 6=Sun
                "is_weekend": current.weekday() >= 5,
            }
        )
        current += timedelta(days=1)

    return dim_date
