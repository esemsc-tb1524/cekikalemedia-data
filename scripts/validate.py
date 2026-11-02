#!/usr/bin/env python3
"""Validate data/media.csv. Standard library only.

    python3 scripts/validate.py          # check, exit 1 on any problem
    python3 scripts/validate.py --fix    # rewrite the file in canonical form (sorted, LF, no BOM)

The rules mirror the constraints in the Supabase table and the extension's own
validation, plus the project rule that every row cites a public source.
"""
import csv
import io
import re
import sys
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "media.csv"
COLUMNS = ["domain", "information", "include_subdomains", "active", "link_url", "source_url"]
MAX_ROWS = 5000  # the extension's adapter refuses larger datasets
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")
URL_RE = re.compile(r"^https://[^\s|]+$")
BOOLS = {"TRUE", "FALSE"}


def read_text(path):
    raw = Path(path).read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("file starts with a UTF-8 BOM; save it as plain UTF-8")
    return raw.decode("utf-8")


def parse(text):
    return list(csv.reader(io.StringIO(text, newline="")))


def canonical(rows):
    """Serialise header + rows sorted by domain, so diffs stay small and merges rarely conflict."""
    header, body = rows[0], sorted(rows[1:], key=lambda r: r[0])
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(body)
    return buf.getvalue()


def check(text):
    """Return a list of human-readable problems (empty if the file is valid)."""
    problems = []
    try:
        rows = parse(text)
    except csv.Error as e:
        return [f"not valid CSV: {e}"]
    if not rows or rows[0] != COLUMNS:
        return [f"header must be exactly: {','.join(COLUMNS)}"]
    body = rows[1:]
    if not body:
        return ["no data rows"]
    if len(body) > MAX_ROWS:
        problems.append(f"{len(body)} rows exceeds the {MAX_ROWS}-row limit of the extension")
    seen = {}
    for n, row in enumerate(body, start=2):  # line numbers as seen by contributors
        if len(row) != len(COLUMNS):
            problems.append(f"line {n}: expected {len(COLUMNS)} columns, found {len(row)}")
            continue
        domain, info, subs, active, link, source = row
        where = f"line {n} ({domain or '?'})"
        if not DOMAIN_RE.match(domain):
            problems.append(f"{where}: domain must be a lowercase bare hostname such as lemonde.fr (no scheme, path, port or spaces)")
        elif domain in seen:
            problems.append(f"{where}: duplicate of line {seen[domain]}")
        else:
            seen[domain] = n
        if not info.strip() or len(info.strip()) > 4000:
            problems.append(f"{where}: information must be 1 to 4000 characters")
        if info != info.strip():
            problems.append(f"{where}: information has leading or trailing whitespace")
        if subs not in BOOLS:
            problems.append(f"{where}: include_subdomains must be TRUE or FALSE")
        if active not in BOOLS:
            problems.append(f"{where}: active must be TRUE or FALSE")
        if link and not URL_RE.match(link):
            problems.append(f"{where}: link_url must be an https:// URL (or empty)")
        if not source:
            problems.append(f"{where}: source_url is required; cite a public document for the ownership claim")
        else:
            for part in (p.strip() for p in source.split(" | ")):
                if not URL_RE.match(part):
                    problems.append(f"{where}: source_url must be one or more https:// URLs separated by ' | ' (got {part[:60]!r})")
                    break
    if not problems and text != canonical(rows):
        problems.append("file is not in canonical form (rows sorted by domain, LF line endings); run: python3 scripts/validate.py --fix")
    return problems


def main(argv):
    fix = "--fix" in argv
    args = [a for a in argv if not a.startswith("--")]
    path = Path(args[0]) if args else DEFAULT_PATH
    try:
        text = read_text(path)
    except (OSError, ValueError, UnicodeDecodeError) as e:
        print(f"ERROR: {path}: {e}")
        return 1
    if fix:
        rows = parse(text)
        path.write_text(canonical(rows), encoding="utf-8", newline="")
        text = read_text(path)
    problems = check(text)
    if problems:
        print(f"{path}: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"{path}: OK ({len(parse(text)) - 1} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
