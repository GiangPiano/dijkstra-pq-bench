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
static const uint64_t expected_checksum = 210453397455ULL;

static const Graph* g;
static void __attribute__((constructor)) make_graph() {
  g = build_graph(n, m, edges);
}

static inline uint64_t calc_checksum(const int* dist, size_t num_nodes) {
  uint64_t sum = 0;
  for (size_t i = 0; i < num_nodes; i++) sum += (uint64_t)(unsigned)dist[i];
  return sum;
}

static inline void run_bench(struct ubench_run_state_s* ubench_run_state,
                             void (*dijkstra_fn)(int*, const Graph*),
                             const char* mode_name,
                             const char* test_name) {
  int* dist = malloc(sizeof(int) * g->num_vertices);
  if (!dist) {
    UBENCH_FAIL();
    return;
  }
  /* Step 1: Correctness verification pass against precomputed checksum */
  dijkstra_fn(dist, g);
  uint64_t actual_checksum = calc_checksum(dist, g->num_vertices);
  if (actual_checksum != expected_checksum) {
    fprintf(stderr, "[ERROR] %s.%s: checksum mismatch! Got %" PRIu64 ", expected %" PRIu64 "\n",
            mode_name, test_name, actual_checksum, expected_checksum);
    free(dist);
    UBENCH_FAIL();
    return;
  }
  /* Step 2: Pure timing benchmark loop (no checksum overhead) */
  UBENCH_DO_BENCHMARK() {
    dijkstra_fn(dist, g);
  }
  free(dist);
}

UBENCH_EX(decrease_key, tiny_dense) {
  run_bench(ubench_run_state, dijkstra_decrease_key, "decrease_key", "tiny_dense");
}

UBENCH_EX(lazy, tiny_dense) {
  run_bench(ubench_run_state, dijkstra_lazy, "lazy", "tiny_dense");
}
