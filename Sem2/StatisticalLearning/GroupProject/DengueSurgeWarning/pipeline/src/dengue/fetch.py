"""Stage `fetch`: download raw data from data.gov.sg and Open-Meteo."""
import datetime as dt
import os
import time

import pandas as pd
import requests

from .config import write_summary

DATAGOV = "https://api-open.data.gov.sg/v1/public/api/datasets"
OPEN_METEO = "https://archive-api.open-meteo.com/v1/archive"


def _headers(env_name):
    key = os.environ.get(env_name or "", "")
    return {"x-api-key": key} if key else {}


def download_datagov(dataset_id, env_name=None, max_polls=10, wait=3):
    h = _headers(env_name)
    url = None
    for attempt in range(max_polls):
        r = requests.get(f"{DATAGOV}/{dataset_id}/poll-download", headers=h, timeout=60)
        if r.status_code == 429:
            time.sleep(wait * (attempt + 1))
            continue
        js = r.json()
        if js.get("code") == 0 and (js.get("data") or {}).get("url"):
            url = js["data"]["url"]
            break
        if attempt == 0:  # large datasets must be prepared first
            try:
                requests.get(f"{DATAGOV}/{dataset_id}/initiate-download", headers=h, timeout=60)
            except requests.RequestException:
                pass
        time.sleep(wait)
    if url is None:
        raise RuntimeError(f"poll-download never returned a URL (last response: {js})")
    f = requests.get(url, timeout=300)
    f.raise_for_status()
    return f.content


def download_weather(wcfg):
    end = wcfg.get("end_date") or (dt.date.today() - dt.timedelta(days=1)).isoformat()
    params = {
        "latitude": wcfg["latitude"],
        "longitude": wcfg["longitude"],
        "start_date": wcfg["start_date"],
        "end_date": end,
        "daily": ",".join(wcfg["daily"]),
        "timezone": "Asia/Singapore",
    }
    r = requests.get(OPEN_METEO, params=params, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"Open-Meteo {r.status_code}: {r.text[:300]}")
    daily = r.json()["daily"]
    return pd.DataFrame(daily).rename(columns={"time": "date"})


def run(cfg, force=False):
    raw = cfg["paths"]["raw"]
    env = cfg["datagov"].get("api_key_env")
    lines = ["# Fetch summary", f"run at {dt.datetime.now():%Y-%m-%d %H:%M}", ""]

    for key, d in cfg["datagov"]["datasets"].items():
        if d.get("snapshot"):
            out = raw / key / f"{dt.date.today():%Y%m%d}.{d['format']}"
            out.parent.mkdir(exist_ok=True)
        else:
            out = raw / f"{key}.{d['format']}"
        if out.exists() and not force:
            lines.append(f"- {key}: SKIPPED (exists: {out.name})")
            continue
        try:
            content = download_datagov(d["id"], env)
            out.write_bytes(content)
            lines.append(f"- {key}: OK ({len(content)/1024:.1f} KB) -> {out.relative_to(raw.parent.parent)}")
        except Exception as e:  # keep going, report at the end
            lines.append(f"- {key}: FAILED - {e}")
        time.sleep(1)  # be polite with the rate limit

    out = raw / "weather_open_meteo_daily.csv"
    if out.exists() and not force:
        lines.append(f"- weather_open_meteo: SKIPPED (exists)")
    else:
        try:
            w = download_weather(cfg["weather"])
            w.to_csv(out, index=False)
            lines.append(f"- weather_open_meteo: OK ({len(w)} days, {w.date.min()} -> {w.date.max()})")
        except Exception as e:
            lines.append(f"- weather_open_meteo: FAILED - {e}")

    for l in lines:
        print(l)
    write_summary(cfg, "fetch", lines)
