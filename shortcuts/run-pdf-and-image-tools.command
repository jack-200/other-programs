#!/bin/bash
SHORTCUTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SHORTCUTS_DIR")"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"
APPLICATION_DIR="$PROJECT_ROOT/pdf-and-image-tools"

if [ -f "$VENV_PYTHON" ]; then
    PYTHON_EXECUTABLE="$VENV_PYTHON"
else
    PYTHON_EXECUTABLE="python3"
fi

cd "$APPLICATION_DIR"
"$PYTHON_EXECUTABLE" main.pyw
