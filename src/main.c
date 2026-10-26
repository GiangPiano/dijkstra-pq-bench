
#include <stdio.h>
#include "ubench.h"
#include "dijkstra.h"
#include "graph.h"

UBENCH_MAIN();

// the previous demo, doesn't include io in the benchmark
UBENCH_EX(simple, first) {
  size_t num_vertices = 4;
  size_t num_edges = 5;
  EdgeInput edges[5] = {
    { 0, 1, 4 },
    { 0, 2, 2 },
    { 1, 2, 1 },
    { 1, 3, 5 },
    { 2, 3, 8 }};

  size_t src = 0;

  int* dist;

  UBENCH_DO_BENCHMARK() {
    Graph* g = build_graph(num_vertices, num_edges, edges);
    dist = dijkstra(g, src);
    free_graph(g);
  }

  for (size_t i = 0; i < num_vertices; i++) printf("%d ", dist[i]);
  printf("\n");
}
