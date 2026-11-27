#!/usr/bin/env bash
# One-time setup for a FREE local voice (Piper TTS). No API key, runs offline afterwards.
# Usage: npm run setup:voice [-- <voice>]   default voice: en_US-lessac-medium (about 60 MB)
# Voice names: https://huggingface.co/rhasspy/piper-voices  (e.g. en_US-ryan-high, en_GB-alan-medium)
set -e
cd "$(dirname "$0")/.."
V="${1:-en_US-lessac-medium}"
lang="${V%%-*}"; rest="${V#*-}"; name="${rest%-*}"; q="${rest##*-}"; family="${lang%%_*}"
PY=""; for c in python3.12 python3.11 python3.13 python3; do command -v $c >/dev/null 2>&1 && PY=$c && break; done
[ -z "$PY" ] && { echo "Need Python 3.11+"; exit 1; }
[ -d .venv-tts ] || $PY -m venv .venv-tts
.venv-tts/bin/pip install --quiet piper-tts
mkdir -p .voices
base="https://huggingface.co/rhasspy/piper-voices/resolve/main/$family/$lang/$name/$q/$V"
for ext in onnx onnx.json; do
  [ -s ".voices/$V.$ext" ] || curl -fsSL -o ".voices/$V.$ext" "$base.$ext"
done
echo "Done. Use: npm run voice -- <reel-id> --provider piper --voice $V"
