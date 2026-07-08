"""
module2_55.main
Core EPG transform logic for Module_2.55

Functions:
- sanitize_html(html_str)
- normalize_timezone(ts_str)
- compute_hash(text)
- transform_epg(file_like, config)

CLI: python -m module2_55 --input input.xml
"""
from lxml import etree, html
from lxml.html.clean import Cleaner
import hashlib
import yaml
import json
import sys
from typing import IO, Dict, Generator

_cleaner = Cleaner(scripts=True, javascript=True, comments=True, style=True, links=True,
                   safe_attrs_only=True)


def sanitize_html(html_str: str) -> str:
    """Strip dangerous HTML and return a cleaned fragment."""
    if not html_str:
        return ""
    try:
        doc = html.fromstring(html_str)
        cleaned = _cleaner.clean_html(doc)
        return html.tostring(cleaned, encoding="unicode", method="html")
    except Exception:
        # fallback: return text as-is
        return html_str


def normalize_timezone(ts_str: str) -> str:
    """Normalize simple ISO timestamps: convert trailing 'Z' to '+00:00'.
    This is intentionally small so it has no heavy external deps.
    """
    if not ts_str:
        return ts_str
    ts = ts_str.strip()
    if ts.endswith("Z"):
        return ts[:-1] + "+00:00"
    return ts


def compute_hash(text: str) -> str:
    h = hashlib.sha256()
    h.update((text or "").encode("utf-8"))
    return h.hexdigest()


def _process_program(elem: etree._Element, rules: Dict) -> Dict:
    """Extract fields from a <programme> element and apply transforms."""
    title = elem.findtext("title") or ""
    desc = elem.findtext("desc") or elem.findtext("description") or ""
    start = elem.get("start") or elem.findtext("start") or ""
    stop = elem.get("stop") or elem.findtext("stop") or ""

    # Apply simple sanitization and normalization
    title_clean = sanitize_html(title)
    desc_clean = sanitize_html(desc)
    start_norm = normalize_timezone(start)
    stop_norm = normalize_timezone(stop)

    combined = title_clean + "\n" + desc_clean
    content_hash = compute_hash(combined)

    processed = {
        "title": title_clean,
        "description": desc_clean,
        "start": start_norm,
        "stop": stop_norm,
        "hash": content_hash,
    }

    # Apply basic filter rules from config (whitelist/blacklist by title)
    if rules:
        allow = True
        wb = rules.get("whitelist")
        bb = rules.get("blacklist")
        if wb:
            allow = any(k.lower() in title.lower() for k in wb)
        if bb and any(k.lower() in title.lower() for k in bb):
            allow = False
        processed["allowed"] = allow
    else:
        processed["allowed"] = True

    return processed


def transform_epg(file_like: IO, config: Dict = None) -> Generator[Dict, None, None]:
    """Incrementally parse an EPG XML file-like and yield processed programme dicts.

    file_like can be a filename (str) or an open file object.
    """
    if config is None:
        config = {}
    # Allow passing filename
    source = file_like
    close_after = False
    if isinstance(file_like, str):
        source = open(file_like, "rb")
        close_after = True

    context = etree.iterparse(source, events=("end",), tag="programme")
    try:
        for _, elem in context:
            processed = _process_program(elem, config.get("filters", {}))
            yield processed
            # important: clear to save memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
    finally:
        if close_after:
            source.close()


def _load_config(path: str) -> Dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Module 2.55 EPG normalization engine")
    parser.add_argument("--input", "-i", help="Input EPG XML file", required=True)
    parser.add_argument("--config", "-c", help="config YAML file", default="config.yaml")
    parser.add_argument("--jsonl", action="store_true", help="Output JSON lines to stdout")
    args = parser.parse_args(argv)

    cfg = _load_config(args.config)
    for item in transform_epg(args.input, cfg):
        if args.jsonl:
            print(json.dumps(item, ensure_ascii=False))
        else:
            print(json.dumps(item, ensure_ascii=False))


if __name__ == "__main__":
    main()
