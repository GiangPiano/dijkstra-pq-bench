#!/usr/bin/env python3
"""Deterministic directed graph generator used by the benchmark suite.

  ./gen.py rand1000 -n 1000 -m 10000 -o rand1000.c
  ./gen.py big -n 1000000 -m 5000000 -o big.c
  ./gen.py dense -n 200 -d 50 -w 20 -s 42      # no -o: writes to stdout
  ./gen.py grid_224 --family grid --rows 224 --cols 224 -s 67 -o grid_224.c
"""
import argparse
import contextlib
import json
import heapq
import random
import sys


def parse_metadata_entry(entry):
    fields = entry.split("|")
    if len(fields) < 3:
        raise ValueError("--metadata-entry requires name|family|description")
    metadata = {"family": fields[1], "description": fields[2]}
    for field in fields[3:]:
        key, separator, value = field.partition("=")
        if not separator:
            raise ValueError(f"invalid metadata field '{field}'")
        try:
            metadata[key] = int(value)
        except ValueError:
            metadata[key] = value
    return fields[0], metadata


def write_graph_registry(path, names, metadata_path=None, metadata_entries=None):
    with open(path, "w", encoding="utf-8") as out:
        out.write('#include <string.h>\n')
        out.write('#include "../../src/bench/graph_registry.h"\n\n')
        for name in names:
            out.write(f"extern const Graph* g_{name};\n")
        out.write("\n")
        out.write("const Graph* graph_for_name(const char* name) {\n")
        for name in names:
            out.write(f'  if (strcmp(name, "{name}") == 0) return g_{name};\n')
        out.write("  return NULL;\n")
        out.write("}\n")
    if metadata_path:
        with open(metadata_path, "w", encoding="utf-8") as out:
            metadata = {}
            for entry in metadata_entries or []:
                name, spec = parse_metadata_entry(entry)
                metadata[name] = spec
            missing = [name for name in names if name not in metadata]
            if missing:
                raise ValueError(f"missing metadata entries for: {', '.join(missing)}")
            json.dump({"graphs": names, "metadata": metadata}, out, indent=2, sort_keys=True)
            out.write("\n")


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


def uniform_edges(n, m, weight, rng):
    total = n * (n - 1)
    edges = []
    for idx in rng.sample(range(total), m):
        u, r = divmod(idx, n - 1)
        v = r + 1 if r >= u else r
        edges.append((u, v, rng.randint(1, weight)))
    return edges


def grid_edges(rows, cols, weight, rng):
    edges = []
    for row in range(rows):
        for col in range(cols):
            u = row * cols + col
            neighbours = []
            if row > 0:
                neighbours.append((row - 1) * cols + col)
            if row + 1 < rows:
                neighbours.append((row + 1) * cols + col)
            if col > 0:
                neighbours.append(u - 1)
            if col + 1 < cols:
                neighbours.append(u + 1)
            for v in neighbours:
                edges.append((u, v, rng.randint(1, weight)))
    return edges


def hub_skewed_edges(n, m, hubs, weight, rng):
    if not 1 <= hubs < n:
        raise ValueError("hub count must be between 1 and n-1")
    hub_vertices = list(range(hubs))
    edges = set()
    # Ensure every vertex has a deterministic path out of the hub core.
    for u in range(n):
        if u not in hub_vertices:
            hub = hub_vertices[u % hubs]
            edges.add((u, hub))
            edges.add((hub, u))
    while len(edges) < m:
        u = rng.randrange(n)
        if rng.random() < 0.75:
            v = rng.choice(hub_vertices)
        else:
            v = rng.randrange(n)
        if u != v:
            edges.add((u, v))
    return [(u, v, rng.randint(1, weight)) for u, v in sorted(edges)]


def layered_edges(layers, width, fanout, weight, rng):
    n = layers * width
    edges = set()
    for layer in range(layers - 1):
        start = layer * width
        next_start = (layer + 1) * width
        for offset in range(width):
            u = start + offset
            # A deterministic ring keeps every layer reachable; additional
            # choices create a broad frontier for the priority queues.
            for step in range(fanout):
                v = next_start + ((offset * fanout + step) % width)
                edges.add((u, v))
    return [(u, v, rng.randint(1, weight)) for u, v in sorted(edges)]


def generate_graph(family, n, m, weight, seed, rows, cols, hubs, layers, width, fanout):
    rng = random.Random(seed)
    if family == "uniform":
        if n is None:
            raise ValueError("--family uniform requires -n")
        total = n * (n - 1)
        if m is None:
            m = min(4 * n, total)
        if not 1 <= m <= total:
            raise ValueError(f"-m must be in [1, {total}] for n={n}")
        edges = uniform_edges(n, m, weight, rng)
    elif family == "grid":
        if rows is None or cols is None:
            raise ValueError("--family grid requires --rows and --cols")
        n = rows * cols
        edges = grid_edges(rows, cols, weight, rng)
        m = len(edges)
    elif family == "hub_skewed":
        if n is None or m is None or hubs is None:
            raise ValueError("--family hub_skewed requires -n, -m, and --hubs")
        edges = hub_skewed_edges(n, m, hubs, weight, rng)
        m = len(edges)
    elif family == "layered":
        if layers is None or width is None or fanout is None:
            raise ValueError("--family layered requires --layers, --width, and --fanout")
        n = layers * width
        edges = layered_edges(layers, width, fanout, weight, rng)
        m = len(edges)
    else:
        raise ValueError(f"unsupported family '{family}' (expected uniform, grid, hub_skewed, or layered)")
    return n, m, edges


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", nargs="?", help="graph name (written in a comment line)")
    ap.add_argument("--registry", metavar="PATH", help="write a graph registry source file")
    ap.add_argument("--metadata", metavar="PATH", help="write graph metadata JSON with the registry")
    ap.add_argument("--graphs", nargs="+", help="graph names for the generated registry")
    ap.add_argument("--metadata-entry", action="append", default=[],
                    help="registry metadata as name|family|description|key=value...")
    ap.add_argument("--family", default="uniform",
                    choices=("uniform", "grid", "hub_skewed", "layered"))
    ap.add_argument("-n", type=int, help="number of vertices (>= 2)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("-m", type=int, help="number of edges")
    g.add_argument("-d", type=float, help="density: percent of possible edges, (0, 100]")
    ap.add_argument("-w", type=int, default=100, help="max edge weight (default 100)")
    ap.add_argument("--rows", type=int)
    ap.add_argument("--cols", type=int)
    ap.add_argument("--hubs", type=int)
    ap.add_argument("--layers", type=int)
    ap.add_argument("--width", type=int)
    ap.add_argument("--fanout", type=int)
    ap.add_argument("-s", type=int, default=1, help="RNG seed (default 1)")
    ap.add_argument("-o", metavar="PATH", help="output file (default: stdout)")
    a = ap.parse_args()

    if a.registry:
        if not a.graphs:
            ap.error("--registry requires --graphs")
        try:
            write_graph_registry(a.registry, a.graphs, a.metadata, a.metadata_entry)
        except ValueError as e:
            ap.error(str(e))
        return
    if not a.name:
        ap.error("the graph name is required unless --registry is used")
    if a.w < 1:
        ap.error("-w must be >= 1")
    if a.n is not None and a.n < 2:
        ap.error("-n must be >= 2")
    if a.d is not None:
        if a.family != "uniform":
            ap.error("-d is only valid for --family uniform")
        if a.n is None or not 0 < a.d <= 100:
            ap.error("-d requires -n and must be in (0, 100]")
        a.m = max(1, round(a.d / 100 * a.n * (a.n - 1)))
    try:
        n, m, edge_tuples = generate_graph(
            a.family, a.n, a.m, a.w, a.s, a.rows, a.cols, a.hubs,
            a.layers, a.width, a.fanout)
    except ValueError as e:
        ap.error(str(e))

    try:
        ctx = open(a.o, "w") if a.o else contextlib.nullcontext(sys.stdout)
    except OSError as e:
        sys.exit(f"gen.py: {e}")

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
        out.write("#include \"../../src/bench/dijkstra.h\"\n")
        out.write("#include \"../../src/bench/graph.h\"\n")
        out.write("#include \"../../src/bench/ubench.h\"\n")
        out.write("\n")

        out.write(f"static const size_t n = {n};\n")
        out.write(f"static const size_t m = {m};\n")
        out.write("static const EdgeInput edges[] = {\n")
        out.write("  " + ",\n  ".join(arcs))
        out.write("};\n")
        out.write(f"static const uint64_t expected_checksum = {ref_checksum}ULL;\n")
        out.write("\n")
        out.write(f"const Graph* g_{name} = NULL;\n")
        out.write(f"static const Graph* g;\n")
        out.write(f"static void __attribute__((constructor)) make_graph_{name}() {{\n")
        out.write(f"  g = build_graph(n, m, edges);\n")
        out.write(f"  g_{name} = g;\n")
        out.write(f"}}\n")
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


    total = n * (n - 1)
    print(f"gen: {name} n={n} m={m} ({100 * m / total:.4g}% dense) seed={a.s}", file=sys.stderr)

if __name__ == "__main__":
    main()
