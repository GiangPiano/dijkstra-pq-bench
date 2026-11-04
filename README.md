# dijkstra-pq-bench

This project compares priority-queue implementations in a real Dijkstra
workload. The benchmark runs the same CSR graph and algorithm with each heap,
then collects runtime, cpu perf, and memory data.

This project requires a linux computer for complete functionality.

macos can be used to compile and run the runtime benchmarks, but does not
support the perf or mem benchmarks.

windows is not supported.

## Dependencies

### Debian/Ubuntu

```sh
sudo apt update
# for building and running the benchmarks
sudo apt install build-essential bash coreutils python3 linux-tools-generic
# for compiling the report
sudo apt install texlive-latex-recommended texlive-fonts-recommended texlive-science texlive-latex-extra latexmk
```

`perf` must be available for the perf benchmark.

### Guix

The repository includes `manifest.scm` for a development environment:

```sh
# dev shell
guix shell -m manifest.scm
# isolated build and run container
guix shell -FC -m manifest.scm
```

It provides GCC, Bash, Coreutils, Make, Python, `perf`.
A similar manifest is in `report/` which contains the texlive packages for
compiling the report.

### Homebrew

```sh
brew install gcc coreutils bash make python texlive
```

You need a version of bash that supports globstar, and the default macos version
is too old.

You also need gnu make, as we use features not available in darwin make.

Install extra packages to build the report

```sh
sudo tlmgr update --self
sudo tlmgr install svg transparent
```

## Building

Build the complete benchmark data and figures with:

```sh
make figures
# or
make all
# or
make
```

Build the benchmark binaries with:

```sh
make build
```

Record data csvs with:

```sh
make csvs
```

Remove generated build, binary, data, and figures with:

```sh
make clean
```

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
- `report/frozen_results` contains the outputs from the selected run used for
  making the submitted report.

## Input graphs

The Makefile builds these deterministic graphs with seed `SEED` (default
`67`):

| Graph              | Description                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------------- |
| `smoke_1k`         | Uniform random graph with 1,000 vertices, 4,000 edges, and weights up to 50.                |
| `uniform_sparse`   | Uniform random digraph with 10,000 vertices and 40,000 edges (average out-degree 4).        |
| `uniform_medium`   | Uniform random digraph with 20,000 vertices and 200,000 edges (average out-degree 10).      |
| `uniform_dense`    | Uniform random digraph with 10,000 vertices and 500,000 edges (average out-degree 50).      |
| `grid_224`         | 224 × 224 directed four-neighbour grid, with weights up to 100.                             |
| `hub_skewed`       | 20,000-vertex, 120,000-edge graph with a concentrated set of 32 hubs and weights up to 100. |
| `layered_frontier` | 100 layers of 200 vertices, with deterministic forward fan-out 8 and weights up to 100.     |

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
