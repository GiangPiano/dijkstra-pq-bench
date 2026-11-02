#!/usr/bin/env python3
"""Random directed graph generator: simple digraph, weights in [1, w], DIMACS output.

  ./gen.py rand1000 -n 1000 -m 10000 -o rand1000.c
  ./gen.py big -n 1000000 -m 5000000 -o big.c
  ./gen.py dense -n 200 -d 50 -w 20 -s 42      # no -o: writes to stdout
"""
import argparse
import contextlib
import random
import sys

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

    # generate a (u, v, w) arc
    def arc(idx):
      u, r = divmod(idx, n - 1)
      v = r + 1 if r >= u else r  # avoid self loop
      return f"{{ {u}, {v}, {rng.randint(1, a.w)} }}"

    # create all the arcs
    arcs = [arc(idx) for idx in rng.sample(range(total), m)]
    # join them all
    arcs = ",\n    ".join(arcs)

    name = " ".join(a.name.split())

    with ctx as out:
        # include headers
        out.write("#include <inttypes.h>\n")
        out.write("#include <stdint.h>\n")
        out.write("#include <stdio.h>\n")
        out.write("#include <stdlib.h>\n")
        out.write("#include \"../src/dijkstra.h\"\n")
        out.write("#include \"../src/graph.h\"\n")
        out.write("#include \"../src/ubench.h\"\n")
        out.write("\n")

        def emit_bench(variant):
          out.write(f"UBENCH_EX({variant}, {name}) {{\n")
          out.write(f"  size_t n = {n};\n")
          out.write(f"  size_t m = {m};\n")
          out.write("\n")
          out.write("  EdgeInput edges[] = {\n")
          out.write("    " + arcs)
          out.write("};\n")
          out.write("\n")
          out.write("  Graph* g = build_graph(n, m, edges);\n")
          out.write("  int* dist = malloc(sizeof(int) * g->num_vertices);\n")
          out.write("\n")
          out.write(f"  UBENCH_DO_BENCHMARK() {{ dijkstra_{variant}(dist, g); }}\n")
          out.write("\n")
          out.write("  free(dist);\n")
          out.write("}\n")

        # dk
        emit_bench("dk")
        out.write("\n")
        emit_bench("lazy")


    print(f"gen: n={n} m={m} ({100 * m / total:.4g}% dense) seed={a.s}", file=sys.stderr)

if __name__ == "__main__":
    main()
