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
- [x] Binary heap — array-backed, implements the `Heap` interface
      (`src/binary/binary_heap.c`)
- [ ] Pairing heap / Fibonacci heap — not yet implemented
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

The optional perf benchmark (`src/bench/perf/bench.py`) requires Linux
`perf`. It uses generic events where available and detects optional cache
counters from `perf list`; unsupported counters are left at zero in the CSV
with a diagnostic note. If `taskset` is unavailable, the benchmark runs
without CPU pinning. Other operating systems can still build and run the
runtime and memory benchmarks, but this perf runner is Linux-only.

## Layout

| File                          | Purpose                                              |
| ----------------------------- | ---------------------------------------------------- |
| `src/graph.h` / `src/graph.c` | Graph in CSR form: `adj_start[]` holds per-vertex offsets into `adj[]`, which stores outgoing edges contiguously. Built from a flat `EdgeInput` list via `build_graph`. |
| `src/heap.h`                  | Priority queue interface (`heap_create`, `heap_push`, `heap_min`, `heap_pop`, `heap_empty`, `heap_delete`) operating on `Item{distance, vertex}`. Each heap variant (binary, pairing, Fibonacci) will implement this interface so `dijkstra()` can run unmodified against all three. |
| `src/djikstra.c`              | Dijkstra's algorithm against the `Heap` interface — allocates a `dist[]` array, relaxes edges out of the CSR graph, pushes updated distances back onto the heap. |
| `src/binary/binary_heap.c`    | Binary heap variant of the `Heap` interface — a min-heap stored as an implicit binary tree in a flat, resizable `Item[]` array (`2*i+1` / `2*i+2` for a node's children). `heap_push` appends and bubbles the new element up; `heap_pop` moves the last element to the root and sinks it down. |
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
- The binary heap keeps the tree implicit in a flat array rather than linking
  nodes with pointers, so a node's parent/children are computed from its
  index (`(i-1)/2`, `2*i+1`, `2*i+2`) instead of being dereferenced — this is
  the baseline we expect pairing/Fibonacci heaps to beat (or not) once they
  land.

# Implementations

## `binary`

Array-backed binary min-heap (`src/binary/binary_heap.c`). O(log n)
push/pop via bubble-up/sink-down, O(1) `heap_min`. The baseline priority
queue the other variants will be benchmarked against.

## `pure`

// TODO

## `pure_rc`

// TODO
