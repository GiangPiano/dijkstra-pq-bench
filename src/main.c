
#include <stdio.h>
#include <stdarg.h>
#include "ubench.h"
#include "dijkstra.h"
#include "graph.h"

UBENCH_MAIN();

static void graph_bench(
    struct ubench_run_state_s *ubench_run_state,
    size_t src,
    size_t num_vertices,
    size_t num_edges,
    EdgeInput* edges) {

  Graph* g = build_graph(num_vertices, num_edges, edges);
  int* dist;

  UBENCH_DO_BENCHMARK() { dist = dijkstra(g, src); }

  free_graph(g);

  for (size_t i = 0; i < num_vertices; i++) printf("%d ", dist[i]);
  printf("\n");
}


#define GRAPH_BENCH(SET, NAME, SRC, NUM_VERTICES, NUM_EDGES, EDGES)            \
  UBENCH_EX(SET, NAME) {                                                       \
    graph_bench(                                                               \
        ubench_run_state,                                                      \
        SRC,                                                                   \
        NUM_VERTICES,                                                          \
        NUM_EDGES,                                                             \
        EDGES);                                                                \
  }

// the previous demo, doesn't include io in the benchmark
GRAPH_BENCH(
    simple,
    first,
    0,
    4,
    5,
    ((EdgeInput[5]) {
     { 0, 1, 4 },
     { 0, 2, 2 },
     { 1, 2, 1 },
     { 1, 3, 5 },
     { 2, 3, 8 },
    }))
