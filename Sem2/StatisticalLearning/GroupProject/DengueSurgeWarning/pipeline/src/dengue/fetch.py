"""Stage `fetch`: download raw data from data.gov.sg and Open-Meteo."""
import datetime as dt
import hashlib
import json
import os
import time

import pandas as pd
import requests

from .config import write_summary

DATAGOV = "https://api-open.data.gov.sg/v1/public/api/datasets"
DATAGOV_META = "https://api-production.data.gov.sg/v2/public/api/datasets"
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


MSS_URL = "https://www.weather.gov.sg/files/dailydata/DAILYDATA_{station}_{ym}.csv"


def download_mss(mcfg, raw, force=False):
    """NEA / Meteorological Service Singapore daily station records, one CSV per month.
    Returns (n_downloaded, n_skipped, failed months)."""
    station = mcfg["station"]
    out_dir = raw / "mss" / station
    out_dir.mkdir(parents=True, exist_ok=True)
    end = mcfg.get("end") or f"{dt.date.today():%Y-%m}"
    got, skipped, failed = 0, 0, []
    for p in pd.period_range(mcfg["start"], end, freq="M"):
        out = out_dir / f"{p.strftime('%Y%m')}.csv"
        if out.exists() and not force:
            skipped += 1
            continue
        try:
            r = requests.get(MSS_URL.format(station=station, ym=f"{p.strftime('%Y%m')}"),
                             headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
            if r.status_code != 200 or not r.content.lstrip(b"\xef\xbb\xbf").startswith(b"Station"):
                raise RuntimeError(f"HTTP {r.status_code}")
            out.write_bytes(r.content)
            got += 1
        except Exception:
            failed.append(f"{p.strftime('%Y-%m')}")
        time.sleep(0.2)
    return got, skipped, failed


def _datagov_metadata(dataset_id):
    try:
        r = requests.get(f"{DATAGOV_META}/{dataset_id}/metadata", timeout=60)
        m = r.json().get("data", {})
        return {k: m.get(k) for k in ["name", "managedBy", "lastUpdatedAt", "coverageStart", "coverageEnd"]}
    except Exception:
        return {}


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _entry(path, raw, **kw):
    return {"file": str(path.relative_to(raw)), "bytes": path.stat().st_size, "sha256": _sha256(path),
            "retrieved_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"), **kw}


def run(cfg, force=False):
    """Download every source and record provenance (URL, query parameters, retrieval time,
    size, sha256, publisher metadata) in data/raw/MANIFEST.json - the frozen-snapshot record."""
    raw = cfg["paths"]["raw"]
    env = cfg["datagov"].get("api_key_env")
    mpath = raw / "MANIFEST.json"
    manifest = json.loads(mpath.read_text()) if mpath.exists() else {}
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
            manifest[key] = _entry(out, raw, source="data.gov.sg", dataset_id=d["id"],
                                   url=f"https://data.gov.sg/datasets/{d['id']}/view",
                                   query=f"{DATAGOV}/{d['id']}/poll-download",
                                   licence="Singapore Open Data Licence v1.0",
                                   metadata=_datagov_metadata(d["id"]))
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
            wc = cfg["weather"]
            manifest["weather_open_meteo"] = _entry(
                out, raw, source="Open-Meteo historical weather API (ERA5 reanalysis)", url=OPEN_METEO,
                params={k: wc[k] for k in ["latitude", "longitude", "start_date", "end_date", "daily"]},
                licence="CC BY 4.0 (open-meteo.com)")
            lines.append(f"- weather_open_meteo: OK ({len(w)} days, {w.date.min()} -> {w.date.max()})")
        except Exception as e:
            lines.append(f"- weather_open_meteo: FAILED - {e}")

    mcfg = cfg["weather"].get("mss")
    if mcfg:
        got, skipped, failed = download_mss(mcfg, raw, force)
        files = sorted((raw / "mss" / mcfg["station"]).glob("*.csv"))
        if got or "mss" not in manifest:
            h = hashlib.sha256(b"".join(_sha256(f).encode() for f in files)).hexdigest()
            manifest["mss"] = {"source": "Meteorological Service Singapore (NEA), historical daily records",
                               "url": "http://www.weather.gov.sg/climate-historical-daily/",
                               "query": MSS_URL, "station": mcfg["station"],
                               "months": f"{mcfg['start']} -> {mcfg.get('end')}", "n_files": len(files),
                               "sha256_of_file_hashes": h,
                               "retrieved_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                               "licence": "NEA/MSS terms of use: free use with attribution "
                                          "(raw files not redistributed; recreate with `run.py fetch`)"}
        lines.append(f"- mss_{mcfg['station']} daily ({mcfg['start']} -> {mcfg.get('end') or 'now'}): "
                     f"{got} months downloaded, {skipped} skipped, failed: {failed or 'none'}")

    mpath.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    lines.append(f"provenance: {mpath.relative_to(raw.parent.parent)}")
    for l in lines:
        print(l)
    write_summary(cfg, "fetch", lines)
