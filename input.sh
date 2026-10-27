#!/usr/bin/env bash
set -euo pipefail

GEN="./gen.py"
OUT_DIR="./data"
SEED=67
mkdir -p "$OUT_DIR"

# 1. Tiny: Dense (n = 50, avg degree = 20)
"$GEN" tiny_dense \
    -n 50 \
    -d 20 \
    -w 10 \
    -s "$SEED" \
    -o "$OUT_DIR/tiny_dense.gr"

# 2. Small: Moderate density (n = 2,000, m = 40,000; avg degree = 20)
"$GEN" small_med \
    -n 2000 \
    -m 40000 \
    -w 50 \
    -s "$SEED" \
    -o "$OUT_DIR/small_med.gr"

# 3. Moderate: Sparse (n = 100,000, m = 400,000; avg degree = 4)
"$GEN" mod_sparse \
    -n 100000 \
    -m 400000 \
    -w 100 \
    -s "$SEED" \
    -o "$OUT_DIR/mod_sparse.gr"

# 4. Big: Sparse (n = 1,000,000, m = 5,000,000; avg degree = 5)
"$GEN" big_sparse \
    -n 1000000 \
    -m 5000000 \
    -w 1000 \
    -s "$SEED" \
    -o "$OUT_DIR/big_sparse.gr"
