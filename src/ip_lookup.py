from __future__ import annotations

import requests
from typing import Dict, Any, Optional

from .config import IPINFO_TOKEN, ABUSEIPDB_KEY


def lookup_geo_ipinfo(ip: str) -> Dict[str, Any]:
    if not IPINFO_TOKEN:
        return {"provider": "ipinfo", "error": "IPINFO_TOKEN not set"}

    url = f"https://ipinfo.io/{ip}"
    params = {"token": IPINFO_TOKEN}
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        loc = data.get("loc", "")
        lat, lon = (None, None)
        if loc and "," in loc:
            lat_str, lon_str = loc.split(",", 1)
            lat, lon = float(lat_str), float(lon_str)
        return {
            "ip": ip,
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "org": data.get("org"),
            "lat": lat,
            "lon": lon,
            "provider": "ipinfo",
        }
    except Exception as exc:
        return {"provider": "ipinfo", "error": str(exc)}


def lookup_reputation_abuseipdb(ip: str) -> Dict[str, Any]:
    if not ABUSEIPDB_KEY:
        return {"provider": "abuseipdb", "error": "ABUSEIPDB_KEY not set"}

    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": ABUSEIPDB_KEY, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": 90}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        return {
            "ip": ip,
            "abuse_confidence_score": data.get("abuseConfidenceScore"),
            "total_reports": data.get("totalReports"),
            "country_code": data.get("countryCode"),
            "isp": data.get("isp"),
            "domain": data.get("domain"),
            "usage_type": data.get("usageType"),
            "provider": "abuseipdb",
        }
    except Exception as exc:
        return {"provider": "abuseipdb", "error": str(exc)}


def full_ip_report(ip: str) -> Dict[str, Any]:
    geo = lookup_geo_ipinfo(ip)
    rep = lookup_reputation_abuseipdb(ip)

    report: Dict[str, Any] = {"ip": ip}

    if "error" not in geo:
        report.update(
            {
                "city": geo.get("city"),
                "region": geo.get("region"),
                "country": geo.get("country"),
                "org": geo.get("org"),
                "lat": geo.get("lat"),
                "lon": geo.get("lon"),
            }
        )

    if "error" not in rep:
        report.update(
            {
                "abuse_confidence_score": rep.get("abuse_confidence_score"),
                "total_reports": rep.get("total_reports"),
                "isp": rep.get("isp"),
                "reputation_country": rep.get("country_code"),
                "usage_type": rep.get("usage_type"),
            }
        )


    if "error" in geo:
        report["geo_error"] = geo["error"]
    if "error" in rep:
        report["rep_error"] = rep["error"]

    return report
