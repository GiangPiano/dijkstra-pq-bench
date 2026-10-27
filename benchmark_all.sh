#!/bin/bash

set -euo pipefail

BIN_DIR="bin"

for exe in "$BIN_DIR"/*; do
    # Skip non-files or non-executables
    [[ -f "$exe" && -x "$exe" ]] || continue

    name="$(basename "$exe")"

    # Exclude stub[cite: 3]
    [[ "$name" == "stub" ]] && continue

    echo "========================================"
    echo "Running benchmark: $name"
    echo "========================================"
    "$exe"
    echo
done
