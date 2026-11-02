#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "../../src/dijkstra.h"
#include "../../src/graph.h"
#include "../../src/ubench.h"

static const size_t n = 50;
static const size_t m = 20;
static const EdgeInput edges[] = {
  { 6, 13, 8 },
  { 9, 35, 5 },
  { 34, 6, 4 },
  { 39, 4, 7 },
  { 34, 36, 10 },
  { 22, 15, 1 },
  { 49, 41, 7 },
  { 35, 45, 9 },
  { 40, 37, 3 },
  { 23, 11, 3 },
  { 17, 1, 6 },
  { 3, 16, 9 },
  { 14, 39, 1 },
  { 24, 3, 8 },
  { 2, 46, 4 },
  { 13, 10, 7 },
  { 36, 37, 1 },
  { 15, 6, 6 },
  { 10, 14, 3 },
  { 7, 49, 7 }};
static const Graph* g;
static void __attribute__((constructor)) make_graph() {
  g = build_graph(n, m, edges);
}

UBENCH_EX(decrease_key, tiny_dense) {
  int* dist = malloc(sizeof(int) * g->num_vertices);
  UBENCH_DO_BENCHMARK() { dijkstra_decrease_key(dist, g); }
  free(dist);
}

UBENCH_EX(lazy, tiny_dense) {
  int* dist = malloc(sizeof(int) * g->num_vertices);
  UBENCH_DO_BENCHMARK() { dijkstra_lazy(dist, g); }
  free(dist);
}
