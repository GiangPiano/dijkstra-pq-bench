# dijkstra-pq-bench

This project compares priority-queue implementations in a real Dijkstra
workload. The benchmark runs the same CSR graph and algorithm with each heap,
then collects runtime, memory, and (on Linux) hardware-counter data.

## Dependencies

### Debian/Ubuntu

```sh
sudo apt update
sudo apt install build-essential bash coreutils python3 \
  linux-tools-generic texlive-latex-recommended texlive-fonts-recommended \
  texlive-science texlive-latex-extra latexmk
```

`perf` must be available for the Linux performance-counter benchmark. The
runtime benchmark and graph generation only require the compiler, Make, and
Python.

### Guix

The repository includes `manifest.scm` for a development environment:

```sh
guix shell -m manifest.scm
```

It provides GCC, Bash, Coreutils, Make, Python, `perf`, and the TeX Live
packages used to build the report.

### Homebrew

```sh
brew install gcc coreutils bash make python texlive
```

Homebrew does not provide the Linux `perf` workflow on macOS, and macOS does
not support the GNU linker wrapping used by the memory benchmark. Build and
run the runtime binaries there, but skip `perf` and `mem`.

## Building

On Linux, build the benchmark binaries with:

```sh
make build
```

Build the complete benchmark data, figures, and report with:

```sh
make
```

Remove generated build, binary, data, and report outputs with:

```sh
make clean
```

On macOS, build only the runtime variants:

```sh
make bin/runtime/binary bin/runtime/brodal-okasaki \
  bin/runtime/fibonacci bin/runtime/pairing
```

The `perf` and `mem` benchmark variants are Linux-only and are intentionally
skipped on macOS.

## Project structure

- `src/bench/` contains the CSR graph representation, Dijkstra
  implementation, graph generator, graph registry, and runtime/perf/memory
  benchmark runners and plotting scripts.
- `src/heap/` contains the common heap interface and one implementation per
  heap variant.
- `Makefile` defines compilation, graph-generation, benchmark, plotting, and
  report targets.
- `report/` contains the LaTeX report and receives generated benchmark data and
  figures.

## Input graphs

The Makefile builds these deterministic graphs with seed `SEED` (default
`67`):

| Graph | Description |
| --- | --- |
| `smoke_1k` | Uniform random graph with 1,000 vertices, 4,000 edges, and weights up to 50. |
| `uniform_sparse` | Uniform random digraph with 10,000 vertices and 40,000 edges (average out-degree 4). |
| `uniform_medium` | Uniform random digraph with 20,000 vertices and 200,000 edges (average out-degree 10). |
| `uniform_dense` | Uniform random digraph with 10,000 vertices and 500,000 edges (average out-degree 50). |
| `grid_224` | 224 × 224 directed four-neighbour grid, with weights up to 100. |
| `hub_skewed` | 20,000-vertex, 120,000-edge graph with a concentrated set of 32 hubs and weights up to 100. |
| `layered_frontier` | 100 layers of 200 vertices, with deterministic forward fan-out 8 and weights up to 100. |

## Heap implementations

All variants implement the interface in `src/heap/heap.h`, including
push, minimum, pop, decrease-key, empty, and delete operations.

- **`binary`** — array-backed binary min-heap with position tracking for
  decrease-key.
- **`pairing`** — pointer-based pairing heap with sibling/child links and
  position tracking.
- **`fibonacci`** — Fibonacci heap with circular root and child lists,
  consolidation, and cascading cuts.
- **`brodal-okasaki`** — an imperative buffer-based adaptation of the
  Brodal–Okasaki priority queue using relative tree references and a free list.

## Code generation and outputs

`src/bench/gen.py` generates deterministic C graph sources and graph metadata.
The Makefile invokes it automatically while building the benchmark binaries:

- Generated graph sources and objects go under `build/test/`.
- The generated registry is `build/test/graph_registry.c`, and graph metadata
  is `build/test/graphs.json`.
- Runtime, perf, and memory executables go under `bin/runtime/`, `bin/perf/`,
  and `bin/mem/`.
- Benchmark CSVs go under `report/data/runtime/`, `report/data/perf/`, and
  `report/data/mem/`; generated figures go under `report/figures/`.
