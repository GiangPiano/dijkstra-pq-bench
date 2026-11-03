#include <limits.h>
#include <stdlib.h>

#include "graph.h"
#include "heap.h"

void dijkstra_decrease_key(int* dist, const Graph* g) {
  size_t n  = g->num_vertices;
  size_t src  = 0;
  for (size_t i = 0; i < n; i++) dist[i] = INT_MAX;
  dist[src] = 0;

  struct Heap* h = heap_create(n);
  heap_push(h, (Item){0, src});

  while (!heap_empty(h)) {
    struct Item it = heap_min(h);
    heap_pop(h);

    int d    = it.distance;
    size_t u = it.vertex;

    for (size_t idx = g->adj_start[u]; idx < g->adj_start[u + 1]; idx++) {
      Edge* e = &(g->adj[idx]);
      int nd  = d + e->weight;
      if (nd < dist[e->dest]) {
        if (dist[e->dest] == INT_MAX)
          heap_push(h, (Item){nd, e->dest});
        else
          heap_decrease_key(h, (Item){dist[e->dest], e->dest}, nd);
        dist[e->dest] = nd;
      }
    }
  }

  heap_delete(h);

  for (size_t i = 0; i < g->num_vertices; i++) {
    if (dist[i] == INT_MAX) dist[i] = -1;
  }
}

void dijkstra_lazy(int* dist, const Graph* g) {
  size_t n  = g->num_vertices;
  size_t src  = 0;
  for (size_t i = 0; i < n; i++) dist[i] = INT_MAX;
  dist[src] = 0;

  struct Heap* h = heap_create(n);
  heap_push(h, (Item){0, src});

  while (!heap_empty(h)) {
    struct Item it = heap_min(h);
    heap_pop(h);

    int d    = it.distance;
    size_t u = it.vertex;

    if (d > dist[u]) continue;

    for (size_t idx = g->adj_start[u]; idx < g->adj_start[u + 1]; idx++) {
      Edge* e = &(g->adj[idx]);
      int nd  = d + e->weight;
      if (nd < dist[e->dest]) {
        dist[e->dest] = nd;
        heap_push(h, (Item){nd, e->dest});
      }
    }
  }

  heap_delete(h);

  for (size_t i = 0; i < g->num_vertices; i++) {
    if (dist[i] == INT_MAX) dist[i] = -1;
  }
}
