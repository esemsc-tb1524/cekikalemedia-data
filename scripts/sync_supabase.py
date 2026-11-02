#!/usr/bin/env python3
"""Publish data/media.csv to the Supabase table public.site_information. Standard library only.

    SUPABASE_URL=https://xxxx.supabase.co SUPABASE_SERVICE_ROLE_KEY=... python3 scripts/sync_supabase.py [--dry-run]

- Rows in the CSV are upserted by domain (the table's unique key); ids are never touched.
- Domains that are in the table but no longer in the CSV are set to active=false, never deleted,
  so a mistaken merge can be undone by restoring the rows.
- Refuses to run if the CSV fails validation, or if it would deactivate more than half of the
  currently active rows (a guard against publishing a truncated file).
"""
import csv
import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate  # noqa: E402

BATCH = 500
MAX_DEACTIVATE_FRACTION = 0.5


def request(method, url, key, body=None, extra=None):
    headers = {"apikey": key, "Authorization": "Bearer " + key, "Content-Type": "application/json"}
    headers.update(extra or {})
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = resp.read()
            return json.loads(payload) if payload else None
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase {method} {urllib.parse.urlsplit(url).path} failed: HTTP {e.code} {e.read().decode(errors='replace')[:300]}")


def load_rows(path):
    text = validate.read_text(path)
    problems = validate.check(text)
    if problems:
        raise SystemExit("Refusing to sync an invalid file:\n  - " + "\n  - ".join(problems))
    out = []
    for r in csv.DictReader(io.StringIO(text, newline="")):
        out.append({
            "domain": r["domain"],
            "information": r["information"].strip(),
            "link_url": r["link_url"] or None,
            "source_url": r["source_url"] or None,
            "include_subdomains": r["include_subdomains"] == "TRUE",
            "active": r["active"] == "TRUE",
        })
    return out


def main(argv):
    dry = "--dry-run" in argv
    base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not (base.startswith("https://") or base.startswith("http://127.0.0.1")) or not key:
        raise SystemExit("Set SUPABASE_URL (https://...) and SUPABASE_SERVICE_ROLE_KEY.")
    table = base + "/rest/v1/site_information"
    rows = load_rows(validate.DEFAULT_PATH)
    wanted = {r["domain"] for r in rows if r["active"]}

    current = []  # Supabase caps a response at 1,000 rows by default, so page through
    while True:
        page = request("GET", f"{table}?select=domain&active=eq.true&order=domain.asc&limit=1000&offset={len(current)}", key)
        current += page
        if len(page) < 1000:
            break
    stale = sorted({r["domain"] for r in current} - {r["domain"] for r in rows})
    if current and len(stale) > MAX_DEACTIVATE_FRACTION * len(current):
        raise SystemExit(f"Would deactivate {len(stale)} of {len(current)} active rows; refusing. Check the CSV.")

    print(f"{len(rows)} rows in CSV ({len(wanted)} active); {len(current)} active in Supabase; {len(stale)} to deactivate")
    for d in stale:
        print("  deactivate:", d)
    if dry:
        print("dry run: nothing written")
        return 0

    for i in range(0, len(rows), BATCH):
        request("POST", table + "?on_conflict=domain", key, rows[i:i + BATCH],
                {"Prefer": "resolution=merge-duplicates,return=minimal"})
    for i in range(0, len(stale), BATCH):
        chunk = stale[i:i + BATCH]
        in_list = ",".join('"' + d + '"' for d in chunk)
        request("PATCH", table + "?domain=in.(" + urllib.parse.quote(in_list, safe='",') + ")", key,
                {"active": False}, {"Prefer": "return=minimal"})
    print("sync complete")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
