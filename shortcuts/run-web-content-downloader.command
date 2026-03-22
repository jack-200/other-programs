#!/bin/bash
SHORTCUTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SHORTCUTS_DIR")"
cd "$PROJECT_ROOT"
uv run web-content-downloader/main.py
