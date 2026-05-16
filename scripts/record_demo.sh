#!/usr/bin/env bash
set -euo pipefail

if ! command -v asciinema >/dev/null 2>&1; then
  echo "asciinema is required. Install it with your package manager or see https://docs.asciinema.org/manual/cli/installation/"
  exit 1
fi

if ! command -v agg >/dev/null 2>&1; then
  echo "agg is required. Install it with: cargo install --locked agg"
  exit 1
fi

asciinema rec docs/assets/demo.cast \
  --overwrite \
  --idle-time-limit 2 \
  --command "uv run --all-extras python scripts/generate_synthetic_demo.py --playback"

agg --speed 1.2 --theme monokai --font-size 18 docs/assets/demo.cast docs/assets/demo.gif

if [ "$(wc -c < docs/assets/demo.gif)" -gt $((2 * 1024 * 1024)) ]; then
  echo "warning: docs/assets/demo.gif exceeded 2 MB; retrying with --font-size 14"
  agg --speed 1.2 --theme monokai --font-size 14 docs/assets/demo.cast docs/assets/demo.gif
fi
