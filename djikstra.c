#include <_stdlib.h>
#include <limits.h>
#include <stdlib.h>

#include "graph.h"
#include "heap.h"

int* dijkstra(Graph* g, int src) {
  int n     = g->num_vertices;
  int* dist = malloc(sizeof(int) * n);
  if (!dist) return NULL;
  for (int i = 0; i < n; i++) dist[i] = INT_MAX;
  dist[src] = 0;

  struct Heap* h = heap_create(n);
  heap_push(h, (Item){0, src});

  while (!heap_empty(h)) {
    struct Item it = heap_min(h);
    heap_pop(h);

    int d = it.distance, u = it.vertex;

    if (d > dist[u]) continue;

    for (int idx = g->adj_start[u]; idx < g->adj_start[u + 1]; idx++) {
      Edge* e = &(g->adj[idx]);
      int nd  = d + e->weight;
      if (nd < dist[e->dest]) {
        dist[e->dest] = nd;
        heap_push(h, (Item){nd, e->dest});
      }
    }
  }

  heap_delete(h);
  return dist;
}
