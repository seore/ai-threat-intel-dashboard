from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

from .config import FEODO_JSON_URL, CACHE_DIR


def fetch_feodo_blocklist(cache: bool = True) -> pd.DataFrame:
    cache_path = CACHE_DIR / "feodo_blocklist.json"

    if cache and cache_path.exists():
        with cache_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        resp = requests.get(FEODO_JSON_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if cache:
            with cache_path.open("w", encoding="utf-8") as f:
                json.dump(data, f)

    entries = data.get("data", [])
    if not entries:
        return pd.DataFrame()

    df = pd.DataFrame(entries)
    if "ip_address" in df.columns:
        df.rename(columns={"ip_address": "ip"}, inplace=True)
    return df
