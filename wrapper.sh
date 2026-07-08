#!/usr/bin/env bash
# Simple wrapper to run the module easily
if [ -z "$1" ]; then
  echo "Usage: $0 <input-epg.xml> [config.yaml]"
  exit 1
fi
INPUT="$1"
CONFIG="${2:-config.yaml}"
python -m module2_55 --input "$INPUT" --config "$CONFIG" --jsonl
