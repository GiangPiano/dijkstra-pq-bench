#include "graph.h"

#include <stdlib.h>
#include <string.h>

void free_graph(Graph* g) {
  if (!g) return;
  free(g->adj_start);
  free(g->adj);
  free(g);
}

Graph* build_graph(int num_vertices, int num_edges, const EdgeInput* edge_input) {
  Graph* g = malloc(sizeof(Graph));
  if (!g) return NULL;

  g->num_vertices = num_vertices;
  g->num_edges    = num_edges;
  g->adj_start    = calloc(num_vertices + 1, sizeof(int));
  g->adj          = malloc(sizeof(Edge) * num_edges);

  if (!g->adj_start || !g->adj) {
    free_graph(g);
    return NULL;
  }

  // build the adj_start ranges
  // - count how many edges per node
  // - compute prefix sum to place the ranges into adj_start[]
  for (int i = 0; i < num_edges; i++) g->adj_start[edge_input[i].src + 1]++;
  for (int u = 1; u <= num_vertices; u++) g->adj_start[u] += g->adj_start[u - 1];

  int* cursor = malloc(sizeof(Edge) * (num_vertices + 1));
  if (!cursor) {
    free_graph(g);
    return NULL;
  }
  memcpy(cursor, g->adj_start, num_vertices * sizeof(int));

  for (int i = 0; i < num_edges; i++) {
    g->adj[cursor[edge_input[i].src]++] = (Edge){edge_input[i].dest, edge_input[i].weight};
  }

  free(cursor);

  return g;
}
