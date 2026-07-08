# Module_2.55

EPG normalization engine implemented as a small Python package. This repository contains a lightweight transform
engine for Electronic Program Guide (EPG) data — it parses XML (TV listings), sanitizes HTML, normalizes
timestamps, and computes content hashes to detect changes.

Features
- Incremental XML processing using lxml.iterparse for memory-efficient transforms
- HTML sanitization using lxml Cleaner
- Simple timezone normalization (Z -> +00:00)
- Content-hash-based change detection (SHA-256)
- Configurable filter rules via config.yaml (whitelist/blacklist by title)

Quick start
1. Create a virtual environment (recommended):

   python -m venv .venv
   source .venv/bin/activate

2. Install dependencies:

   pip install -r requirements.txt

3. Run the transform against an EPG XML file:

   python -m module2_55 --input path/to/epg.xml --config config.yaml --jsonl > output.jsonl

Files added
- pyproject.toml — project metadata and build backend
- requirements.txt — lxml, PyYAML
- src/module2_55/ — package code
  - main.py — core transform logic with iterparse and helpers
- config.yaml — example filter rules
- wrapper.sh — convenience shell wrapper to run the module
- tests/test_basic.py — minimal pytest-based sanity tests
- .gitignore — common ignores

Configuration (config.yaml)
- filters:
  - whitelist: list of substrings; if provided only programs whose title contains one of these substrings are allowed
  - blacklist: list of substrings; if a title contains any of these the program is excluded

Output format
- By default the module prints JSON objects to stdout (one per program). Use --jsonl to explicitly request newline-delimited JSON.

Change detection
- Each processed item includes a `hash` field (SHA-256 of cleaned title+description). Use this to detect whether a program's content changed between runs.

Testing
- Run tests with pytest:

   pytest -q

Contributing
- Open an issue or submit a PR. Keep changes small and add tests for new behavior.

License
- See the LICENSE file for license details.
