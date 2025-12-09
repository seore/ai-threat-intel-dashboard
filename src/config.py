from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# IP geolocation 
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "")
ABUSEIPDB_KEY = os.getenv("ABUSEIPDB_KEY", "")

# Threat feeds 
FEODO_JSON_URL = "https://feodotracker.abuse.ch/downloads/ipblocklist_aggressive.json"

DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
