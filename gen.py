#!/usr/bin/env python3
"""Random directed graph generator: simple digraph, weights in [1, w], DIMACS output.

  ./gen.py rand1000 -n 1000 -m 10000 -o rand1000.c
  ./gen.py big -n 1000000 -m 5000000 -o big.c
  ./gen.py dense -n 200 -d 50 -w 20 -s 42      # no -o: writes to stdout
"""
import argparse
import contextlib
import heapq
import random
import sys


def compute_reference_checksum(n, edges, src=0):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    dist = [float("inf")] * n
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    checksum = 0
    for i in range(n):
        d = dist[i] if dist[i] != float("inf") else -1
        checksum = (checksum + (d & 0xFFFFFFFF)) & 0xFFFFFFFFFFFFFFFF
    return checksum


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="graph name (written in a comment line)")
    ap.add_argument("-n", type=int, required=True, help="number of vertices (>= 2)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("-m", type=int, help="number of edges")
    g.add_argument("-d", type=float, help="density: percent of possible edges, (0, 100]")
    ap.add_argument("-w", type=int, default=100, help="max edge weight (default 100)")
    ap.add_argument("-s", type=int, default=1, help="RNG seed (default 1)")
    ap.add_argument("-o", metavar="PATH", help="output file (default: stdout)")
    a = ap.parse_args()

    n = a.n
    if n < 2:
        ap.error("-n must be >= 2")
    if a.w < 1:
        ap.error("-w must be >= 1")

    total = n * (n - 1)  # possible directed arcs, no self-loops
    if a.d is not None:
        if not 0 < a.d <= 100:
            ap.error("-d must be in (0, 100]")
        m = max(1, round(a.d / 100 * total))
    elif a.m is not None:
        m = a.m
    else:
        m = min(4 * n, total)
    if not 1 <= m <= total:
        ap.error(f"-m must be in [1, {total}] for n={n}")

    try:
        ctx = open(a.o, "w") if a.o else contextlib.nullcontext(sys.stdout)
    except OSError as e:
        sys.exit(f"gen.py: {e}")

    rng = random.Random(a.s)

    # generate all (u, v, w) arcs
    edge_tuples = []
    for idx in rng.sample(range(total), m):
        u, r = divmod(idx, n - 1)
        v = r + 1 if r >= u else r  # avoid self loop
        w = rng.randint(1, a.w)
        edge_tuples.append((u, v, w))

    arcs = [f"{{ {u}, {v}, {w} }}" for u, v, w in edge_tuples]

    # Compute reference ground-truth checksum in Python
    ref_checksum = compute_reference_checksum(n, edge_tuples)

    name = " ".join(a.name.split())

    with ctx as out:
        # include headers
        out.write("#include <inttypes.h>\n")
        out.write("#include <stdint.h>\n")
        out.write("#include <stdio.h>\n")
        out.write("#include <stdlib.h>\n")
        out.write("#include \"../../src/dijkstra.h\"\n")
        out.write("#include \"../../src/graph.h\"\n")
        out.write("#include \"../../src/bench/bench0.h\"\n")
        out.write("\n")

        out.write(f"static const size_t n = {n};\n")
        out.write(f"static const size_t m = {m};\n")
        out.write("static const EdgeInput edges[] = {\n")
        out.write("  " + ",\n  ".join(arcs))
        out.write("};\n")
        out.write(f"static const uint64_t expected_checksum = {ref_checksum}ULL;\n")
        out.write("\n")
        out.write("static const Graph* g;\n")
        out.write("static void __attribute__((constructor)) make_graph() {\n")
        out.write("  g = build_graph(n, m, edges);\n")
        out.write("}\n")
        out.write("\n")

        out.write("static inline uint64_t calc_checksum(const int* dist, size_t num_nodes) {\n")
        out.write("  uint64_t sum = 0;\n")
        out.write("  for (size_t i = 0; i < num_nodes; i++) sum += (uint64_t)(unsigned)dist[i];\n")
        out.write("  return sum;\n")
        out.write("}\n")
        out.write("\n")

        out.write("static inline void run_bench(struct ubench_run_state_s* ubench_run_state,\n")
        out.write("                             void (*dijkstra_fn)(int*, const Graph*),\n")
        out.write("                             const char* mode_name,\n")
        out.write("                             const char* test_name) {\n")
        out.write("  int* dist = malloc(sizeof(int) * g->num_vertices);\n")
        out.write("  if (!dist) {\n")
        out.write("    UBENCH_FAIL();\n")
        out.write("    return;\n")
        out.write("  }\n")
        out.write("  /* Step 1: Correctness verification pass against precomputed checksum */\n")
        out.write("  dijkstra_fn(dist, g);\n")
        out.write("  uint64_t actual_checksum = calc_checksum(dist, g->num_vertices);\n")
        out.write("  if (actual_checksum != expected_checksum) {\n")
        out.write("    fprintf(stderr, \"[ERROR] %s.%s: checksum mismatch! Got %\" PRIu64 \", expected %\" PRIu64 \"\\n\",\n")
        out.write("            mode_name, test_name, actual_checksum, expected_checksum);\n")
        out.write("    free(dist);\n")
        out.write("    UBENCH_FAIL();\n")
        out.write("    return;\n")
        out.write("  }\n")
        out.write("  /* Step 2: Pure timing benchmark loop (no checksum overhead) */\n")
        out.write("  UBENCH_DO_BENCHMARK() {\n")
        out.write("    dijkstra_fn(dist, g);\n")
        out.write("  }\n")
        out.write("  free(dist);\n")
        out.write("}\n")
        out.write("\n")

        # decrease_key
        out.write(f"UBENCH_EX(decrease_key, {name}) {{\n")
        out.write(f"  run_bench(ubench_run_state, dijkstra_decrease_key, \"decrease_key\", \"{name}\");\n")
        out.write("}\n\n")

        # lazy
        out.write(f"UBENCH_EX(lazy, {name}) {{\n")
        out.write(f"  run_bench(ubench_run_state, dijkstra_lazy, \"lazy\", \"{name}\");\n")
        out.write("}\n")


    print(f"gen: n={n} m={m} ({100 * m / total:.4g}% dense) seed={a.s}", file=sys.stderr)

if __name__ == "__main__":
    main()
