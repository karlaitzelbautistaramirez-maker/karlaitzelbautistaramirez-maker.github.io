"""Monitoreo del sitio en producción (Módulo 3.3 - métricas DevOps).

Comprueba disponibilidad, código HTTP y tiempo de respuesta de las URLs clave,
agrega los resultados a monitoring/metrics.csv y muestra un resumen con:
  * Disponibilidad (% de comprobaciones exitosas)
  * Tiempo de respuesta promedio y percentil 95
  * Tasa de errores HTTP (4xx/5xx o sin respuesta)

Uso:  SITE_URL=https://usuario.github.io python scripts/monitor.py
Sale con código 1 si alguna URL falla (GitHub Actions envía la alerta por correo).
"""
from __future__ import annotations

import csv
import math
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "monitoring" / "metrics.csv"
PATHS = ["/", "/menu/", "/producto/paquete-familiar-eke/", "/ayuda/", "/sitemap.xml", "/robots.txt"]
SLOW_MS = 2000
MAX_ROWS = 3000


def check(url: str) -> tuple[int, int]:
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "EkeMonitor/1.0", "Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=20) as r:
            r.read()
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception:
        status = 0
    return status, round((time.perf_counter() - start) * 1000)


def main() -> int:
    base = os.environ.get("SITE_URL", "").rstrip("/")
    if not base:
        print("Define la variable SITE_URL, p. ej. https://usuario.github.io")
        return 2
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    rows, failed = [], 0
    for p in PATHS:
        status, ms = check(base + p)
        ok = 200 <= status < 400
        failed += not ok
        rows.append([now, p, status, ms, 1 if ok else 0])
        flag = "OK " if ok else "ERR"
        slow = "  (lento)" if ok and ms > SLOW_MS else ""
        print(f"[{flag}] {status:>3} {ms:>6} ms  {p}{slow}")

    CSV.parent.mkdir(exist_ok=True)
    history = []
    if CSV.exists():
        with CSV.open(encoding="utf-8") as f:
            history = list(csv.reader(f))[1:]
    history = (history + [[str(c) for c in r] for r in rows])[-MAX_ROWS:]
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp_utc", "path", "status", "response_ms", "ok"])
        w.writerows(history)

    total = len(history)
    ok_count = sum(1 for r in history if r[4] == "1")
    times = sorted(int(r[3]) for r in history if r[4] == "1")
    avg = sum(times) / len(times) if times else 0
    p95 = times[min(len(times) - 1, math.ceil(len(times) * 0.95) - 1)] if times else 0
    summary = (
        f"\n## Resumen del monitoreo ({total} comprobaciones)\n"
        f"- Disponibilidad: **{ok_count * 100 / total:.2f} %** (objetivo >= 99.5 %)\n"
        f"- Tiempo de respuesta promedio: **{avg:.0f} ms** - p95: **{p95} ms**\n"
        f"- Tasa de errores HTTP: **{(total - ok_count) * 100 / total:.2f} %**\n"
    )
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(summary)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
