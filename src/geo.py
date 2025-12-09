# src/geo.py
from __future__ import annotations

from typing import Iterable, List, Dict

import pandas as pd

from .ip_lookup import lookup_geo_ipinfo


def geocode_ips(ips: Iterable[str], limit: int = 200) -> pd.DataFrame:
    unique_ips = list(dict.fromkeys(ips))[:limit]  # preserve order, dedupe
    records: List[Dict] = []
    for ip in unique_ips:
        info = lookup_geo_ipinfo(ip)
        if "error" not in info and info.get("lat") is not None:
            records.append(info)
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)
