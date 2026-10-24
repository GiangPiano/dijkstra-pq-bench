# dijkstra-pq-bench

Binary heap vs pairing heap vs Fibonacci heap, measured inside a real
shortest-path workload — not an isolated microbenchmark, but the full cost of
each priority queue as Dijkstra's algorithm actually uses it (interleaved
push/pop, decrease-key traffic, cache behavior on a real graph).

## Status

Early work in progress; nothing here is benchmarkable yet.

- [x] Graph representation — CSR adjacency (`graph.h`, `graph.c`)
- [x] Dijkstra's algorithm, written against a generic heap interface
      (`djikstra.c`)
- [ ] Heap implementations — `heap.h` currently only declares the interface; no
      backing implementation exists yet
- [ ] Benchmark harness / graph generation (`main.c` is a placeholder)
- [x] Build system — `Makefile` is not yet wired up to the current sources

## Project Layout

`src/*.{c, h}`:
common source and header files, used by all builds.

`src/*/`:
sub directories of src are considered variants, and will be automatically
supported by the Makefile. Variants are mutually exclusive and are used to
enable linking with alternate priority queue / heap implementations.

## Building

`make all`:
the default target
builds all executable variants under `bin/`

`make bin/*`:
builds an individual executable for any particular variant / heap
implementation.

`make clean`:
removes the build and bin directories.

## Layout

| File                          | Purpose                                              |
| ----------------------------- | ---------------------------------------------------- |
| `src/graph.h` / `src/graph.c` | Graph in CSR form: `adj_start[]` holds per-vertex offsets into `adj[]`, which stores outgoing edges contiguously. Built from a flat `EdgeInput` list via `build_graph`. |
| `src/heap.h`                  | Priority queue interface (`heap_create`, `heap_push`, `heap_min`, `heap_pop`, `heap_empty`, `heap_delete`) operating on `Item{distance, vertex}`. Each heap variant (binary, pairing, Fibonacci) will implement this interface so `dijkstra()` can run unmodified against all three. |
| `src/djikstra.c`              | Dijkstra's algorithm against the `Heap` interface — allocates a `dist[]` array, relaxes edges out of the CSR graph, pushes updated distances back onto the heap. |
| `src/main.c`                  | Entry point; currently just wires together a toy graph as a smoke test. |
| `Makefile`                    | Build rules. Not yet in sync with the current source filenames — needs revisiting once a heap implementation exists to link against. |
| `compile_flags.txt`           | Flags for clangd / clang tooling (`-xc -std=c11 -Iinclude`). |

## Design notes

- The graph uses CSR (compressed sparse row) instead of an adjacency list so
  that neighbor iteration is a single contiguous scan (`g->adj_start[u] ..
  g->adj_start[u+1]`), which matters for the benchmark since it's the inner loop
  of every heap variant being compared.
- `dijkstra()` is written once against the abstract `Heap` interface in `heap.h`
  so swapping in binary/pairing/Fibonacci implementations doesn't require
  touching the algorithm itself — only the heap's internals change between
  benchmark runs.

# Implementations

## `pure`

// TODO

## `pure_rc`

// TODO
