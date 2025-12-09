import io
import requests
import pandas as pd

FEODO_CSV_URL = "https://feodotracker.abuse.ch/downloads/ipblocklist.csv"  # example stable CSV

def fetch_feodo_blocklist(cache: bool = True) -> pd.DataFrame:
    resp = requests.get(FEODO_CSV_URL, timeout=15)
    resp.raise_for_status()

    raw = "\n".join(
        line for line in resp.text.splitlines() 
        if not line.startswith("#") and line.strip()
    )
    df = pd.read_csv(io.StringIO(raw))
    df = df.rename(columns={
        "IP address": "ip",
        "Port": "dst_port",
        "Firstseen (UTC)": "first_seen",
        "Lastonline (UTC)": "last_seen",
    })
    return df
