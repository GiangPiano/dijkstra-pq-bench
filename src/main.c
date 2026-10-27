#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "dijkstra.h"
#include "graph.h"
#include "ubench.h"

UBENCH_MAIN();

static void input_error(const char* path, const char* msg) {
  fprintf(stderr, "%s: %s\n", path, msg);
  exit(1);
}

// Read a DIMACS .gr file into a Graph.
static Graph* load_input(const char* path, size_t* n_out) {
  FILE* f = fopen(path, "r");
  if (!f) {
    perror(path);
    exit(1);
  }

  char line[256];
  size_t n = 0, m = 0, k = 0;
  EdgeInput* edges = NULL;

  while (fgets(line, sizeof line, f)) {
    if (line[0] == 'p') {
      if (sscanf(line, "p sp %zu %zu", &n, &m) != 2) input_error(path, "bad 'p sp' line");
      edges = malloc((m ? m : 1) * sizeof *edges);
      if (!edges) input_error(path, "out of memory");
    } else if (line[0] == 'a') {
      size_t u = 0, v = 0;
      int w = 0;
      if (!edges || k >= m || sscanf(line, "a %zu %zu %d", &u, &v, &w) != 3)
        input_error(path, "bad 'a' line, or more arcs than the header says");
      if (u > n || v > n) input_error(path, "vertex id out of range");
      edges[k++] = (EdgeInput){u, v, w};
    }
  }
  fclose(f);
  if (!edges || k != m) input_error(path, "arc count does not match header");

  Graph* g = build_graph(n, m, edges);
  free(edges);
  *n_out = n;
  return g;
}

typedef struct {
  Graph* g;
  size_t n;
} Input;

static void graph_bench(struct ubench_run_state_s* ubench_run_state,
                        Input* input,
                        const char* path,
                        size_t src) {
  // Runs on the first call only.
  if (!input->g) {
    input->g = load_input(path, &input->n);

    int* d       = dijkstra(input->g, src);
    uint64_t sum = 0;
    for (size_t i = 0; i < input->n; i++) sum += (uint64_t)(unsigned)d[i];
    printf("[ INFO ] %s: n=%zu src=%zu checksum=%lld\n", path, input->n, src, sum);

    free(d);
  }

  int* dist = NULL;
  UBENCH_DO_BENCHMARK() { dist = dijkstra(input->g, src); }
  UBENCH_DO_NOTHING(dist);  // prevent the compiler from removing unused variable
  free(dist);
}

#define GRAPH_BENCH(SET, NAME, PATH, SRC)             \
  UBENCH_EX(SET, NAME) {                              \
    static Input input;                               \
    graph_bench(ubench_run_state, &input, PATH, SRC); \
  }

GRAPH_BENCH(random, tiny_dense, "data/tiny_dense.gr", 0);
GRAPH_BENCH(random, small_med, "data/small_med.gr", 0);
GRAPH_BENCH(random, mod_sparse, "data/mod_sparse.gr", 0);
GRAPH_BENCH(random, big_sparse, "data/big_sparse.gr", 0);
